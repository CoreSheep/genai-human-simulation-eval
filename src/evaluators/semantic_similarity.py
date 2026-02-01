"""
Semantic similarity evaluation using sentence embeddings.

Measures how similar the AI response is to the human response in terms of
meaning and content, regardless of exact wording.
"""

import numpy as np
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer, util
from dataclasses import dataclass


@dataclass
class SemanticResult:
    """Result of semantic similarity evaluation."""

    cosine_similarity: float
    euclidean_distance: float
    manhattan_distance: float

    def to_dict(self) -> Dict[str, float]:
        return {
            'cosine_similarity': self.cosine_similarity,
            'euclidean_distance': self.euclidean_distance,
            'manhattan_distance': self.manhattan_distance
        }


class SemanticSimilarityEvaluator:
    """
    Evaluates semantic similarity between human and AI responses.

    Uses pre-trained sentence transformers to create dense embeddings
    and compute various similarity metrics.
    """

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the evaluator.

        Args:
            model_name: Name of the sentence-transformer model to use.
                       'all-MiniLM-L6-v2' is fast and effective for semantic similarity.
        """
        self.model = SentenceTransformer(model_name)
        self.embeddings_cache: Dict[str, np.ndarray] = {}

    def _get_embedding(self, text: str) -> np.ndarray:
        """
        Get embedding for text with caching.

        Args:
            text: Input text

        Returns:
            Dense embedding vector
        """
        if text not in self.embeddings_cache:
            self.embeddings_cache[text] = self.model.encode(text, convert_to_tensor=False)
        return self.embeddings_cache[text]

    def evaluate_pair(self, human_answer: str, ai_answer: str) -> SemanticResult:
        """
        Evaluate semantic similarity between a human-AI answer pair.

        Args:
            human_answer: The human's response
            ai_answer: The AI simulation's response

        Returns:
            SemanticResult with various similarity metrics
        """
        # Get embeddings
        human_emb = self._get_embedding(human_answer)
        ai_emb = self._get_embedding(ai_answer)

        # Compute metrics
        cosine_sim = float(util.cos_sim(human_emb, ai_emb)[0][0])
        euclidean = float(np.linalg.norm(human_emb - ai_emb))
        manhattan = float(np.sum(np.abs(human_emb - ai_emb)))

        return SemanticResult(
            cosine_similarity=cosine_sim,
            euclidean_distance=euclidean,
            manhattan_distance=manhattan
        )

    def evaluate_batch(self,
                      human_answers: List[str],
                      ai_answers: List[str]) -> List[SemanticResult]:
        """
        Evaluate multiple pairs efficiently.

        Args:
            human_answers: List of human responses
            ai_answers: List of AI responses

        Returns:
            List of SemanticResult objects
        """
        if len(human_answers) != len(ai_answers):
            raise ValueError("Human and AI answer lists must have same length")

        # Batch encode for efficiency
        human_embs = self.model.encode(human_answers, convert_to_tensor=False, show_progress_bar=False)
        ai_embs = self.model.encode(ai_answers, convert_to_tensor=False, show_progress_bar=False)

        results = []
        for h_emb, a_emb in zip(human_embs, ai_embs):
            cosine_sim = float(util.cos_sim(h_emb, a_emb)[0][0])
            euclidean = float(np.linalg.norm(h_emb - a_emb))
            manhattan = float(np.sum(np.abs(h_emb - a_emb)))

            results.append(SemanticResult(
                cosine_similarity=cosine_sim,
                euclidean_distance=euclidean,
                manhattan_distance=manhattan
            ))

        return results

    def get_aggregate_stats(self, results: List[SemanticResult]) -> Dict[str, float]:
        """
        Compute aggregate statistics from multiple results.

        Args:
            results: List of SemanticResult objects

        Returns:
            Dictionary with mean, std, min, max for each metric
        """
        cosine_sims = [r.cosine_similarity for r in results]

        return {
            'mean_cosine_similarity': np.mean(cosine_sims),
            'std_cosine_similarity': np.std(cosine_sims),
            'min_cosine_similarity': np.min(cosine_sims),
            'max_cosine_similarity': np.max(cosine_sims),
            'median_cosine_similarity': np.median(cosine_sims)
        }
