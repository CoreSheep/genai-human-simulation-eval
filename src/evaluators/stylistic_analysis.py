"""
Stylistic analysis evaluator for linguistic feature comparison.

Measures how well the AI mimics the human's writing style, including
length, complexity, formality, and natural imperfections.
"""

import re
import textstat
import numpy as np
from typing import Dict, List
from dataclasses import dataclass
from collections import Counter


@dataclass
class StylisticFeatures:
    """Linguistic features of a text response."""

    length: int
    word_count: int
    avg_word_length: float
    sentence_count: int
    avg_sentence_length: float
    flesch_reading_ease: float
    flesch_kincaid_grade: float
    formality_score: float
    has_typos: bool
    punctuation_density: float
    vocabulary_richness: float  # type-token ratio

    def to_dict(self) -> Dict[str, any]:
        return self.__dict__


@dataclass
class StylisticAlignment:
    """Alignment scores between human and AI stylistic features."""

    length_ratio: float  # AI/Human length ratio
    length_similarity: float  # 1 - abs difference normalized
    complexity_similarity: float  # Based on readability scores
    formality_similarity: float
    style_consistency_score: float  # Overall style match
    has_human_like_imperfections: bool

    def to_dict(self) -> Dict[str, any]:
        return self.__dict__


class StylisticAnalyzer:
    """
    Analyzes and compares stylistic features of responses.

    This evaluator is critical for human simulation because style often
    reveals more about authenticity than semantic content alone.
    """

    # Informal markers (contractions, casual language)
    INFORMAL_PATTERNS = [
        r"\bi'm\b", r"\byou're\b", r"\bdon't\b", r"\bcan't\b", r"\bwon't\b",
        r"\bgonna\b", r"\bwanna\b", r"\bkinda\b", r"\bsorta\b",
        r"\byeah\b", r"\bnah\b", r"\bumm\b", r"\blike\b.*\blike\b"
    ]

    # Common typo patterns
    TYPO_PATTERNS = [
        r"\s{2,}",  # Multiple spaces
        r"\.{2,}",  # Multiple periods
        r"[a-z][A-Z]",  # Case inconsistency
    ]

    def extract_features(self, text: str) -> StylisticFeatures:
        """
        Extract stylistic features from text.

        Args:
            text: Input text

        Returns:
            StylisticFeatures object
        """
        # Basic metrics
        length = len(text)
        words = text.split()
        word_count = len(words)

        # Avoid division by zero
        if word_count == 0:
            return StylisticFeatures(
                length=length, word_count=0, avg_word_length=0,
                sentence_count=0, avg_sentence_length=0,
                flesch_reading_ease=0, flesch_kincaid_grade=0,
                formality_score=0, has_typos=False,
                punctuation_density=0, vocabulary_richness=0
            )

        avg_word_length = np.mean([len(w) for w in words])

        # Sentence metrics
        sentences = textstat.sentence_count(text)
        sentences = max(sentences, 1)  # Avoid division by zero
        avg_sentence_length = word_count / sentences

        # Readability scores
        try:
            flesch = textstat.flesch_reading_ease(text)
            fk_grade = textstat.flesch_kincaid_grade(text)
        except:
            flesch = 50  # Default moderate readability
            fk_grade = 8

        # Formality score (lower = more informal)
        formality = self._compute_formality(text)

        # Detect typos and imperfections
        has_typos = self._detect_typos(text)

        # Punctuation density
        punct_count = len(re.findall(r'[.,!?;:]', text))
        punct_density = punct_count / word_count if word_count > 0 else 0

        # Vocabulary richness (type-token ratio)
        unique_words = len(set(w.lower() for w in words))
        vocab_richness = unique_words / word_count if word_count > 0 else 0

        return StylisticFeatures(
            length=length,
            word_count=word_count,
            avg_word_length=avg_word_length,
            sentence_count=sentences,
            avg_sentence_length=avg_sentence_length,
            flesch_reading_ease=flesch,
            flesch_kincaid_grade=fk_grade,
            formality_score=formality,
            has_typos=has_typos,
            punctuation_density=punct_density,
            vocabulary_richness=vocab_richness
        )

    def _compute_formality(self, text: str) -> float:
        """
        Compute formality score (0-1, higher = more formal).

        Based on presence of informal language patterns.
        """
        text_lower = text.lower()
        informal_count = sum(
            len(re.findall(pattern, text_lower))
            for pattern in self.INFORMAL_PATTERNS
        )

        # Normalize by text length (per 100 words)
        word_count = len(text.split())
        if word_count == 0:
            return 0.5

        informal_density = (informal_count / word_count) * 100
        # Invert: high informal density = low formality
        formality = max(0, 1 - (informal_density / 10))  # Scale to 0-1

        return formality

    def _detect_typos(self, text: str) -> bool:
        """
        Detect common typos and imperfections.

        Args:
            text: Input text

        Returns:
            True if likely contains typos
        """
        # Check for common typo patterns
        for pattern in self.TYPO_PATTERNS:
            if re.search(pattern, text):
                return True

        # Check for known misspellings in the dataset
        common_errors = ['discouns', 'toothpase', 'mum ']
        return any(error in text.lower() for error in common_errors)

    def compare_styles(self,
                      human_features: StylisticFeatures,
                      ai_features: StylisticFeatures) -> StylisticAlignment:
        """
        Compare stylistic features between human and AI.

        Args:
            human_features: Features from human response
            ai_features: Features from AI response

        Returns:
            StylisticAlignment with comparison metrics
        """
        # Length comparison
        if human_features.length > 0:
            length_ratio = ai_features.length / human_features.length
        else:
            length_ratio = float('inf') if ai_features.length > 0 else 1.0

        # Length similarity (penalize large differences)
        length_diff = abs(human_features.length - ai_features.length)
        max_length = max(human_features.length, ai_features.length)
        length_similarity = 1 - (length_diff / max_length) if max_length > 0 else 1.0

        # Complexity similarity (based on readability)
        complexity_diff = abs(
            human_features.flesch_kincaid_grade - ai_features.flesch_kincaid_grade
        )
        complexity_similarity = max(0, 1 - (complexity_diff / 12))  # Normalize by grade range

        # Formality similarity
        formality_diff = abs(human_features.formality_score - ai_features.formality_score)
        formality_similarity = 1 - formality_diff

        # Overall style consistency
        style_score = (
            length_similarity * 0.3 +
            complexity_similarity * 0.3 +
            formality_similarity * 0.4
        )

        # Check for human-like imperfections
        has_imperfections = (
            ai_features.has_typos or
            (ai_features.formality_score < 0.7 and human_features.formality_score < 0.7)
        )

        return StylisticAlignment(
            length_ratio=length_ratio,
            length_similarity=length_similarity,
            complexity_similarity=complexity_similarity,
            formality_similarity=formality_similarity,
            style_consistency_score=style_score,
            has_human_like_imperfections=has_imperfections
        )

    def evaluate_batch(self,
                      human_answers: List[str],
                      ai_answers: List[str]) -> List[StylisticAlignment]:
        """
        Evaluate multiple pairs.

        Args:
            human_answers: List of human responses
            ai_answers: List of AI responses

        Returns:
            List of StylisticAlignment objects
        """
        results = []
        for h_ans, a_ans in zip(human_answers, ai_answers):
            h_features = self.extract_features(h_ans)
            a_features = self.extract_features(a_ans)
            alignment = self.compare_styles(h_features, a_features)
            results.append(alignment)

        return results

    def get_aggregate_stats(self, alignments: List[StylisticAlignment]) -> Dict[str, float]:
        """Get aggregate statistics from alignment results."""
        return {
            'mean_length_ratio': np.mean([a.length_ratio for a in alignments]),
            'mean_length_similarity': np.mean([a.length_similarity for a in alignments]),
            'mean_complexity_similarity': np.mean([a.complexity_similarity for a in alignments]),
            'mean_formality_similarity': np.mean([a.formality_similarity for a in alignments]),
            'mean_style_score': np.mean([a.style_consistency_score for a in alignments]),
            'pct_with_imperfections': np.mean([a.has_human_like_imperfections for a in alignments]) * 100
        }
