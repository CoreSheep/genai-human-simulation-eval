"""
Data loading and preprocessing module for GenAI simulation evaluation.

This module handles loading the human vs AI response dataset and provides
structured access to the data for evaluation.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class ResponsePair:
    """Represents a paired human and AI response to a question."""

    id: int
    person_id: str
    question_category: str
    question: str
    human_answer: str
    ai_answer: str

    def __repr__(self) -> str:
        return (f"ResponsePair(id={self.id}, person={self.person_id}, "
                f"category={self.question_category})")


class DataLoader:
    """Loads and structures the evaluation dataset."""

    def __init__(self, data_path: str = "data/RB_GenAI_Datatest.xlsx"):
        """
        Initialize the data loader.

        Args:
            data_path: Path to the Excel file containing the dataset
        """
        self.data_path = Path(data_path)
        self.df: pd.DataFrame = None
        self.response_pairs: List[ResponsePair] = []

    def load(self) -> 'DataLoader':
        """
        Load the dataset from Excel file.

        Returns:
            Self for method chaining
        """
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data file not found: {self.data_path}")

        self.df = pd.read_excel(self.data_path)
        self._validate_schema()
        self._create_response_pairs()

        return self

    def _validate_schema(self) -> None:
        """Validate that the DataFrame has expected columns."""
        required_cols = {'id', 'person_id', 'question_category',
                        'question', 'human_answers', 'ai_answers'}
        missing_cols = required_cols - set(self.df.columns)

        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

    def _create_response_pairs(self) -> None:
        """Convert DataFrame rows to ResponsePair objects."""
        self.response_pairs = [
            ResponsePair(
                id=row['id'],
                person_id=row['person_id'],
                question_category=row['question_category'],
                question=row['question'],
                human_answer=row['human_answers'],
                ai_answer=row['ai_answers']
            )
            for _, row in self.df.iterrows()
        ]

    def get_by_person(self, person_id: str) -> List[ResponsePair]:
        """Get all response pairs for a specific person."""
        return [rp for rp in self.response_pairs if rp.person_id == person_id]

    def get_by_category(self, category: str) -> List[ResponsePair]:
        """Get all response pairs for a specific question category."""
        return [rp for rp in self.response_pairs if rp.question_category == category]

    def get_persons(self) -> List[str]:
        """Get list of unique person IDs."""
        return sorted(self.df['person_id'].unique())

    def get_categories(self) -> List[str]:
        """Get list of unique question categories."""
        return sorted(self.df['question_category'].unique())

    def get_summary_stats(self) -> Dict[str, any]:
        """Get summary statistics about the dataset."""
        return {
            'total_pairs': len(self.response_pairs),
            'num_persons': self.df['person_id'].nunique(),
            'num_questions': self.df['question'].nunique(),
            'persons': self.get_persons(),
            'categories': self.get_categories(),
            'category_counts': self.df['question_category'].value_counts().to_dict(),
            'avg_human_length': self.df['human_answers'].str.len().mean(),
            'avg_ai_length': self.df['ai_answers'].str.len().mean()
        }


if __name__ == "__main__":
    # Quick test
    loader = DataLoader().load()
    stats = loader.get_summary_stats()
    print("Dataset loaded successfully!")
    print(f"Total pairs: {stats['total_pairs']}")
    print(f"Persons: {stats['persons']}")
    print(f"Categories: {stats['categories']}")
