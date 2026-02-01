"""
Stylistic analysis evaluator for linguistic feature comparison.

Measures how well the AI mimics the human's writing style, including
length, complexity, formality, natural imperfections, and emotional tone.
"""

import re
import textstat
import numpy as np
from typing import Dict, List
from dataclasses import dataclass
from collections import Counter
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# TextBlob is optional - use VADER as primary sentiment analyzer
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except:
    TEXTBLOB_AVAILABLE = False


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
    
    # Emotional/Sentiment features
    sentiment_polarity: float  # -1 (negative) to 1 (positive)
    sentiment_subjectivity: float  # 0 (objective) to 1 (subjective)
    emotional_intensity: float  # 0 to 1 (compound VADER score normalized)
    positive_emotion: float  # 0 to 1
    negative_emotion: float  # 0 to 1
    neutral_emotion: float  # 0 to 1

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
    
    # Emotional alignment
    sentiment_similarity: float  # How similar are the sentiment polarities
    emotional_tone_match: float  # Overall emotional alignment
    subjectivity_similarity: float  # How similar in objectivity/subjectivity

    def to_dict(self) -> Dict[str, any]:
        return self.__dict__


class StylisticAnalyzer:
    """
    Analyzes and compares stylistic features of responses.

    This evaluator is critical for human simulation because style often
    reveals more about authenticity than semantic content alone. Now includes
    emotional/sentiment analysis to capture the affective tone of responses.
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
    
    def __init__(self):
        """Initialize sentiment analyzers."""
        self.vader = SentimentIntensityAnalyzer()


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
                punctuation_density=0, vocabulary_richness=0,
                sentiment_polarity=0, sentiment_subjectivity=0,
                emotional_intensity=0, positive_emotion=0,
                negative_emotion=0, neutral_emotion=0
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
        
        # Emotional/Sentiment Analysis
        # Use TextBlob if available, otherwise use VADER for polarity estimation
        if TEXTBLOB_AVAILABLE:
            try:
                blob = TextBlob(text)
                polarity = blob.sentiment.polarity  # -1 to 1
                subjectivity = blob.sentiment.subjectivity  # 0 to 1
            except:
                polarity = 0
                subjectivity = 0.5
        else:
            # Estimate from VADER compound score
            polarity = 0
            subjectivity = 0.5
        
        # VADER for more nuanced emotion detection (works without downloads)
        try:
            vader_scores = self.vader.polarity_scores(text)
            emotional_intensity = (vader_scores['compound'] + 1) / 2  # Normalize to 0-1
            positive = vader_scores['pos']
            negative = vader_scores['neg']
            neutral = vader_scores['neu']
            # Use VADER compound for polarity if TextBlob not available
            if not TEXTBLOB_AVAILABLE:
                polarity = vader_scores['compound']
        except:
            emotional_intensity = 0.5
            positive = 0
            negative = 0
            neutral = 1.0

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
            vocabulary_richness=vocab_richness,
            sentiment_polarity=polarity,
            sentiment_subjectivity=subjectivity,
            emotional_intensity=emotional_intensity,
            positive_emotion=positive,
            negative_emotion=negative,
            neutral_emotion=neutral
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
 