#!/usr/bin/env python3
"""
Main evaluation script for GenAI human simulation assessment.

This orchestrates all evaluation dimensions and produces comprehensive results.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from data_loader import DataLoader, ResponsePair
from evaluators import (
    SemanticSimilarityEvaluator,
    StylisticAnalyzer,
    LLMJudgeEvaluator
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ComprehensiveEvaluator:
    """
    Orchestrates multi-dimensional evaluation of human simulations.

    This is the main evaluation engine that coordinates all evaluation
    dimensions and produces comprehensive results.
    """

    def __init__(self, data_path: str = "data/RB_GenAI_Datatest.xlsx"):
        """Initialize evaluator with data path."""
        self.data_loader = DataLoader(data_path)
        self.semantic_evaluator = SemanticSimilarityEvaluator()
        self.stylistic_analyzer = StylisticAnalyzer()
        self.llm_judge = LLMJudgeEvaluator()

        self.results: Dict = {}

    async def run_evaluation(self) -> Dict:
        """
        Run comprehensive evaluation across all dimensions.

        Returns:
            Dictionary containing all evaluation results
        """
        logger.info("Loading dataset...")
        self.data_loader.load()
        pairs = self.data_loader.response_pairs

        logger.info(f"Loaded {len(pairs)} response pairs")
        logger.info("=" * 60)

        # Extract lists for batch processing
        questions = [p.question for p in pairs]
        human_answers = [p.human_answer for p in pairs]
        ai_answers = [p.ai_answer for p in pairs]
        person_ids = [p.person_id for p in pairs]
        categories = [p.question_category for p in pairs]

        # 1. Semantic Similarity Evaluation
        logger.info("Running semantic similarity evaluation...")
        semantic_results = self.semantic_evaluator.evaluate_batch(
            human_answers, ai_answers
        )
        semantic_stats = self.semantic_evaluator.get_aggregate_stats(semantic_results)
        logger.info(f"  Mean cosine similarity: {semantic_stats['mean_cosine_similarity']:.3f}")

        # 2. Stylistic Analysis
        logger.info("Running stylistic analysis...")
        stylistic_results = self.stylistic_analyzer.evaluate_batch(
            human_answers, ai_answers
        )
        stylistic_stats = self.stylistic_analyzer.get_aggregate_stats(stylistic_results)
        logger.info(f"  Mean style score: {stylistic_stats['mean_style_score']:.3f}")
        logger.info(f"  Mean length ratio (AI/Human): {stylistic_stats['mean_length_ratio']:.2f}x")

        # 3. LLM Judge Evaluation (async)
        logger.info("Running LLM-as-judge evaluation (this may take a few minutes)...")
        llm_results = await self.llm_judge.evaluate_batch(
            questions, human_answers, ai_answers
        )
        llm_stats = self.llm_judge.get_aggregate_stats(llm_results)
        if llm_stats['count'] > 0:
            logger.info(f"  Mean overall score: {llm_stats['mean_overall_score']:.2f}/10")
        else:
            logger.warning("  LLM evaluation skipped (no API key)")

        # 4. Per-person analysis
        logger.info("Analyzing per-person performance...")
        person_analysis = self._analyze_by_dimension(
            pairs, semantic_results, stylistic_results, llm_results,
            group_by='person_id'
        )

        # 5. Per-category analysis
        logger.info("Analyzing per-category performance...")
        category_analysis = self._analyze_by_dimension(
            pairs, semantic_results, stylistic_results, llm_results,
            group_by='question_category'
        )

        # 6. Identify weakest matches
        logger.info("Identifying weakest simulation matches...")
        weakest_matches = self._find_weakest_matches(
            pairs, semantic_results, stylistic_results, llm_results
        )

        # Compile results
        self.results = {
            'metadata': {
                'evaluation_date': datetime.now().isoformat(),
                'total_pairs': len(pairs),
                'num_persons': len(set(person_ids)),
                'num_categories': len(set(categories)),
                'model_version': 'v1.0'
            },
            'aggregate_scores': {
                'semantic': semantic_stats,
                'stylistic': stylistic_stats,
                'llm_judge': llm_stats
            },
            'per_person_analysis': person_analysis,
            'per_category_analysis': category_analysis,
            'weakest_matches': weakest_matches,
            'detailed_results': {
                'semantic': [r.to_dict() for r in semantic_results],
                'stylistic': [r.to_dict() for r in stylistic_results],
                'llm_judge': [r.to_dict() if r else None for r in llm_results]
            }
        }

        logger.info("=" * 60)
        logger.info("Evaluation complete!")

        return self.results

    def _analyze_by_dimension(self,
                             pairs: List[ResponsePair],
                             semantic_results: List,
                             stylistic_results: List,
                             llm_results: List,
                             group_by: str) -> Dict:
        """
        Analyze results grouped by a dimension (person or category).

        Args:
            pairs: Response pairs
            semantic_results: Semantic evaluation results
            stylistic_results: Stylistic evaluation results
            llm_results: LLM judge results
            group_by: Field to group by ('person_id' or 'question_category')

        Returns:
            Dictionary with analysis for each group
        """
        from collections import defaultdict
        import numpy as np

        groups = defaultdict(lambda: {
            'semantic': [],
            'stylistic': [],
            'llm': []
        })

        for i, pair in enumerate(pairs):
            key = getattr(pair, group_by)
            groups[key]['semantic'].append(semantic_results[i])
            groups[key]['stylistic'].append(stylistic_results[i])
            if llm_results[i]:
                groups[key]['llm'].append(llm_results[i])

        analysis = {}
        for key, data in groups.items():
            semantic_scores = [r.cosine_similarity for r in data['semantic']]
            style_scores = [r.style_consistency_score for r in data['stylistic']]
            llm_scores = [r.overall_score for r in data['llm']] if data['llm'] else []

            analysis[key] = {
                'count': len(data['semantic']),
                'mean_semantic_similarity': float(np.mean(semantic_scores)),
                'mean_style_score': float(np.mean(style_scores)),
                'mean_llm_score': float(np.mean(llm_scores)) if llm_scores else None,
                'std_semantic': float(np.std(semantic_scores)),
                'std_style': float(np.std(style_scores))
            }

        return analysis

    def _find_weakest_matches(self,
                             pairs: List[ResponsePair],
                             semantic_results: List,
                             stylistic_results: List,
                             llm_results: List,
                             n: int = 5) -> List[Dict]:
        """
        Find the N weakest simulation matches.

        Args:
            pairs: Response pairs
            semantic_results: Semantic evaluation results
            stylistic_results: Stylistic evaluation results
            llm_results: LLM judge results
            n: Number of weakest matches to return

        Returns:
            List of dictionaries describing weakest matches
        """
        scored_pairs = []
        for i, pair in enumerate(pairs):
            # Composite score (lower = worse match)
            semantic_score = semantic_results[i].cosine_similarity
            style_score = stylistic_results[i].style_consistency_score
            llm_score = llm_results[i].overall_score / 10 if llm_results[i] else 0.5

            # Weighted average
            composite = (
                semantic_score * 0.35 +
                style_score * 0.35 +
                llm_score * 0.30
            )

            scored_pairs.append({
                'pair_id': pair.id,
                'person_id': pair.person_id,
                'question': pair.question,
                'category': pair.question_category,
                'composite_score': composite,
                'semantic_score': semantic_score,
                'style_score': style_score,
                'llm_score': llm_score if llm_results[i] else None,
                'human_answer': pair.human_answer,
                'ai_answer': pair.ai_answer,
                'issues': llm_results[i].ai_weaknesses if llm_results[i] else []
            })

        # Sort by composite score (ascending - worst first)
        scored_pairs.sort(key=lambda x: x['composite_score'])

        return scored_pairs[:n]

    def save_results(self, output_path: str = "outputs/evaluation_results.json"):
        """Save results to JSON file."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        logger.info(f"Results saved to {output_path}")


async def main():
    """Main execution function."""
    evaluator = ComprehensiveEvaluator()

    # Run evaluation
    results = await evaluator.run_evaluation()

    # Save results
    evaluator.save_results()

    # Print summary
    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)

    agg = results['aggregate_scores']

    print(f"\n📊 SEMANTIC SIMILARITY")
    print(f"  Mean: {agg['semantic']['mean_cosine_similarity']:.3f}")
    print(f"  Range: [{agg['semantic']['min_cosine_similarity']:.3f}, {agg['semantic']['max_cosine_similarity']:.3f}]")

    print(f"\n✍️  STYLISTIC ALIGNMENT")
    print(f"  Mean style score: {agg['stylistic']['mean_style_score']:.3f}")
    print(f"  Length ratio (AI/Human): {agg['stylistic']['mean_length_ratio']:.2f}x")
    print(f"  Responses with human-like imperfections: {agg['stylistic']['pct_with_imperfections']:.1f}%")

    if agg['llm_judge']['count'] > 0:
        print(f"\n🤖 LLM JUDGE ASSESSMENT (n={agg['llm_judge']['count']})")
        print(f"  Overall score: {agg['llm_judge']['mean_overall_score']:.2f}/10")
        print(f"  Semantic match: {agg['llm_judge']['mean_semantic_match']:.2f}/10")
        print(f"  Style match: {agg['llm_judge']['mean_style_match']:.2f}/10")
        print(f"  Personality match: {agg['llm_judge']['mean_personality_match']:.2f}/10")
        print(f"  Naturalness: {agg['llm_judge']['mean_naturalness']:.2f}/10")

        if agg['llm_judge']['common_weaknesses']:
            print(f"\n⚠️  COMMON AI WEAKNESSES:")
            for weakness in agg['llm_judge']['common_weaknesses'][:3]:
                print(f"    • {weakness['weakness']} ({weakness['count']} occurrences)")

    print(f"\n👥 PER-PERSON ANALYSIS")
    for person, stats in results['per_person_analysis'].items():
        print(f"  {person}: Semantic={stats['mean_semantic_similarity']:.3f}, "
              f"Style={stats['mean_style_score']:.3f}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
