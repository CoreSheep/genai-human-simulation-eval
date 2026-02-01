"""
LLM-as-Judge evaluator using Claude for holistic assessment.

Uses a state-of-the-art LLM to evaluate how well AI responses match human
responses across multiple dimensions, providing nuanced qualitative assessment.
"""

import asyncio
import json
import os
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from anthropic import AsyncAnthropic
import logging

logger = logging.getLogger(__name__)


@dataclass
class LLMJudgment:
    """Result of LLM judge evaluation."""

    semantic_match: float  # 0-10 scale
    style_match: float  # 0-10 scale
    personality_match: float  # 0-10 scale
    naturalness: float  # 0-10 scale
    overall_score: float  # 0-10 scale
    explanation: str
    ai_weaknesses: List[str]

    def to_dict(self) -> Dict:
        return asdict(self)


class LLMJudgeEvaluator:
    """
    Uses Claude as an expert judge to evaluate response quality.

    This provides a holistic, nuanced evaluation that captures dimensions
    difficult to measure with automated metrics alone.
    """

    EVALUATION_PROMPT = """You are an expert evaluator assessing how well an AI simulation mimics a real human's response.

You will be shown:
1. A question asked to both a human and an AI simulation
2. The human's actual response
3. The AI simulation's response

Your task is to evaluate how accurately the AI simulation captures the human's response across multiple dimensions.

QUESTION: {question}

HUMAN RESPONSE:
{human_answer}

AI SIMULATION RESPONSE:
{ai_answer}

Evaluate the AI simulation on these dimensions (0-10 scale):

1. SEMANTIC MATCH: How similar is the factual content and meaning?
   - 10: Identical meaning
   - 7-9: Very similar meaning with minor differences
   - 4-6: Partially overlapping meaning
   - 0-3: Different meaning or contradictory

2. STYLE MATCH: How similar is the writing style?
   - 10: Indistinguishable style (tone, formality, structure)
   - 7-9: Very similar style with minor differences
   - 4-6: Noticeable style differences
   - 0-3: Completely different style

3. PERSONALITY MATCH: How well does the AI capture individual personality traits?
   - 10: Perfectly captures personal quirks, voice, attitude
   - 7-9: Captures overall personality well
   - 4-6: Generic response lacking personal flavor
   - 0-3: Misses personality entirely

4. NATURALNESS: How natural and human-like is the AI response?
   - 10: Fully convincing as human (includes imperfections, casual language)
   - 7-9: Mostly natural with slight AI tells
   - 4-6: Noticeably polished/artificial
   - 0-3: Obviously AI-generated

Provide your evaluation in this JSON format:
{{
    "semantic_match": <score 0-10>,
    "style_match": <score 0-10>,
    "personality_match": <score 0-10>,
    "naturalness": <score 0-10>,
    "overall_score": <weighted average>,
    "explanation": "<brief explanation of your assessment>",
    "ai_weaknesses": ["<weakness 1>", "<weakness 2>", ...]
}}

Focus on specific, concrete observations. Be critical and note even subtle differences.
Respond ONLY with the JSON, no additional text."""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-opus-4-20250514"):
        """
        Initialize LLM judge evaluator.

        Args:
            api_key: Anthropic API key (if None, reads from ANTHROPIC_API_KEY env var)
            model: Claude model to use for evaluation
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            logger.warning("No Anthropic API key found. LLM judge evaluation will be skipped.")
            self.client = None
        else:
            self.client = AsyncAnthropic(api_key=self.api_key)
        self.model = model
        self.semaphore = asyncio.Semaphore(5)  # Max 5 concurrent requests

    async def evaluate_single(self,
                             question: str,
                             human_answer: str,
                             ai_answer: str) -> Optional[LLMJudgment]:
        """
        Evaluate a single response pair using Claude.

        Args:
            question: The question asked
            human_answer: Human's response
            ai_answer: AI simulation's response

        Returns:
            LLMJudgment or None if API unavailable
        """
        if not self.client:
            logger.warning("Skipping LLM judgment - no API key")
            return None

        prompt = self.EVALUATION_PROMPT.format(
            question=question,
            human_answer=human_answer,
            ai_answer=ai_answer
        )

        async with self.semaphore:  # Rate limiting
            try:
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=1500,
                    temperature=0.3,  # Lower temperature for more consistent evaluation
                    messages=[{"role": "user", "content": prompt}]
                )

                # Parse JSON response
                result_text = response.content[0].text.strip()

                # Handle markdown code blocks if present
                if result_text.startswith("```"):
                    result_text = result_text.split("```")[1]
                    if result_text.startswith("json"):
                        result_text = result_text[4:]
                    result_text = result_text.strip()

                result = json.loads(result_text)

                return LLMJudgment(
                    semantic_match=float(result['semantic_match']),
                    style_match=float(result['style_match']),
                    personality_match=float(result['personality_match']),
                    naturalness=float(result['naturalness']),
                    overall_score=float(result['overall_score']),
                    explanation=result['explanation'],
                    ai_weaknesses=result.get('ai_weaknesses', [])
                )

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response as JSON: {e}")
                logger.error(f"Response text: {result_text}")
                return None
            except Exception as e:
                logger.error(f"Error in LLM evaluation: {e}")
                return None

    async def evaluate_batch(self,
                           questions: List[str],
                           human_answers: List[str],
                           ai_answers: List[str]) -> List[Optional[LLMJudgment]]:
        """
        Evaluate multiple pairs concurrently with async I/O.

        Args:
            questions: List of questions
            human_answers: List of human responses
            ai_answers: List of AI responses

        Returns:
            List of LLMJudgment results (None for failed evaluations)
        """
        if not self.client:
            logger.warning("Skipping batch LLM judgment - no API key")
            return [None] * len(questions)

        tasks = [
            self.evaluate_single(q, h, a)
            for q, h, a in zip(questions, human_answers, ai_answers)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Evaluation failed: {result}")
                processed_results.append(None)
            else:
                processed_results.append(result)

        return processed_results

    def get_aggregate_stats(self, judgments: List[Optional[LLMJudgment]]) -> Dict[str, any]:
        """
        Compute aggregate statistics from LLM judgments.

        Args:
            judgments: List of LLMJudgment results (may include None values)

        Returns:
            Dictionary with aggregate metrics
        """
        valid_judgments = [j for j in judgments if j is not None]

        if not valid_judgments:
            return {
                'count': 0,
                'mean_semantic_match': 0,
                'mean_style_match': 0,
                'mean_personality_match': 0,
                'mean_naturalness': 0,
                'mean_overall_score': 0,
                'common_weaknesses': []
            }

        # Aggregate scores
        semantic_scores = [j.semantic_match for j in valid_judgments]
        style_scores = [j.style_match for j in valid_judgments]
        personality_scores = [j.personality_match for j in valid_judgments]
        naturalness_scores = [j.naturalness for j in valid_judgments]
        overall_scores = [j.overall_score for j in valid_judgments]

        # Find common weaknesses
        all_weaknesses = []
        for j in valid_judgments:
            all_weaknesses.extend(j.ai_weaknesses)

        # Count weakness frequency
        from collections import Counter
        weakness_counts = Counter(all_weaknesses)
        common_weaknesses = [
            {"weakness": w, "count": c}
            for w, c in weakness_counts.most_common(5)
        ]

        import numpy as np
        return {
            'count': len(valid_judgments),
            'mean_semantic_match': float(np.mean(semantic_scores)),
            'std_semantic_match': float(np.std(semantic_scores)),
            'mean_style_match': float(np.mean(style_scores)),
            'std_style_match': float(np.std(style_scores)),
            'mean_personality_match': float(np.mean(personality_scores)),
            'std_personality_match': float(np.std(personality_scores)),
            'mean_naturalness': float(np.mean(naturalness_scores)),
            'std_naturalness': float(np.std(naturalness_scores)),
            'mean_overall_score': float(np.mean(overall_scores)),
            'std_overall_score': float(np.std(overall_scores)),
            'common_weaknesses': common_weaknesses
        }
