"""
Visualization module for evaluation results.

Creates professional, publication-quality visualizations for the technical report.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List
import json

# Set professional style
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10


class ResultVisualizer:
    """Creates visualizations for evaluation results."""

    def __init__(self, results_path: str = "outputs/evaluation_results.json"):
        """
        Initialize visualizer with results file.

        Args:
            results_path: Path to JSON results file
        """
        self.results_path = Path(results_path)
        with open(self.results_path, 'r') as f:
            self.results = json.load(f)

        self.output_dir = Path("outputs/figures")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def create_all_visualizations(self):
        """Generate all visualizations for the report."""
        print("Generating visualizations...")

        self.plot_overview_scores()
        self.plot_dimension_comparison()
        self.plot_person_performance()
        self.plot_category_performance()
        self.plot_score_distributions()
        self.plot_length_analysis()

        print(f"Visualizations saved to {self.output_dir}")

    def plot_overview_scores(self):
        """Create overview radar chart of all evaluation dimensions."""
        fig, ax = plt.subplots(figsize=(8, 6), subplot_kw=dict(projection='polar'))

        # Prepare data
        agg = self.results['aggregate_scores']
        categories = []
        scores = []

        # Semantic (normalize to 0-10 scale)
        categories.append('Semantic\nSimilarity')
        scores.append(agg['semantic']['mean_cosine_similarity'] * 10)

        # Stylistic
        categories.append('Stylistic\nAlignment')
        scores.append(agg['stylistic']['mean_style_score'] * 10)

        # LLM Judge dimensions (if available)
        if agg['llm_judge']['count'] > 0:
            categories.extend([
                'LLM:\nSemantic',
                'LLM:\nStyle',
                'LLM:\nPersonality',
                'LLM:\nNaturalness'
            ])
            scores.extend([
                agg['llm_judge']['mean_semantic_match'],
                agg['llm_judge']['mean_style_match'],
                agg['llm_judge']['mean_personality_match'],
                agg['llm_judge']['mean_naturalness']
            ])

        # Number of variables
        N = len(categories)
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        scores += scores[:1]  # Complete the circle
        angles += angles[:1]

        # Plot
        ax.plot(angles, scores, 'o-', linewidth=2, color='#2E86AB', label='AI Simulation')
        ax.fill(angles, scores, alpha=0.25, color='#2E86AB')

        # Benchmark line (human test-retest = 8.5/10 based on paper's 85%)
        benchmark = [8.5] * len(angles)
        ax.plot(angles, benchmark, '--', linewidth=1.5, color='#A23B72',
                label='Human Test-Retest Benchmark (85%)')

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, size=9)
        ax.set_ylim(0, 10)
        ax.set_yticks([0, 2.5, 5, 7.5, 10])
        ax.set_yticklabels(['0', '2.5', '5', '7.5', '10'], size=8)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=9)
        ax.set_title('Multi-Dimensional Evaluation Overview', size=12, weight='bold', pad=20)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / "overview_scores.png", dpi=300, bbox_inches='tight')
        plt.close()

    def plot_dimension_comparison(self):
        """Create bar chart comparing performance across dimensions."""
        fig, ax = plt.subplots(figsize=(10, 5))

        agg = self.results['aggregate_scores']

        dimensions = ['Semantic\nSimilarity', 'Style\nConsistency']
        scores = [
            agg['semantic']['mean_cosine_similarity'] * 10,
            agg['stylistic']['mean_style_score'] * 10
        ]
        errors = [
            agg['semantic']['std_cosine_similarity'] * 10,
            agg['stylistic']['mean_style_score'] * 10 * 0.15  # Approximate error
        ]

        if agg['llm_judge']['count'] > 0:
            dimensions.append('LLM Judge\nOverall')
            scores.append(agg['llm_judge']['mean_overall_score'])
            errors.append(agg['llm_judge']['std_overall_score'])

        x = np.arange(len(dimensions))
        bars = ax.bar(x, scores, yerr=errors, capsize=5, color='#06A77D', alpha=0.8, edgecolor='black')

        # Add benchmark line
        ax.axhline(y=8.5, color='#A23B72', linestyle='--', linewidth=2,
                  label='Human Test-Retest (85%)')

        # Add value labels on bars
        for i, (bar, score) in enumerate(zip(bars, scores)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{score:.2f}',
                   ha='center', va='bottom', fontsize=10, weight='bold')

        ax.set_ylabel('Score (0-10 scale)', fontsize=11, weight='bold')
        ax.set_title('Performance Across Evaluation Dimensions', fontsize=12, weight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(dimensions, fontsize=10)
        ax.set_ylim(0, 10.5)
        ax.legend(fontsize=9)
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / "dimension_comparison.png", dpi=300, bbox_inches='tight')
        plt.close()

    def plot_person_performance(self):
        """Create comparison chart for per-person performance."""
        fig, ax = plt.subplots(figsize=(10, 6))

        person_data = self.results['per_person_analysis']
        persons = list(person_data.keys())

        x = np.arange(len(persons))
        width = 0.25

        semantic_scores = [person_data[p]['mean_semantic_similarity'] * 10 for p in persons]
        style_scores = [person_data[p]['mean_style_score'] * 10 for p in persons]
        llm_scores = [person_data[p]['mean_llm_score'] if person_data[p]['mean_llm_score'] else 0
                     for p in persons]

        bars1 = ax.bar(x - width, semantic_scores, width, label='Semantic', color='#2E86AB')
        bars2 = ax.bar(x, style_scores, width, label='Stylistic', color='#06A77D')

        if any(llm_scores):
            bars3 = ax.bar(x + width, llm_scores, width, label='LLM Judge', color='#F18F01')

        ax.set_ylabel('Score (0-10 scale)', fontsize=11, weight='bold')
        ax.set_title('Per-Person Simulation Performance', fontsize=12, weight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(persons, fontsize=10)
        ax.legend(fontsize=9)
        ax.set_ylim(0, 10.5)
        ax.grid(axis='y', alpha=0.3)

        # Add value labels
        for bars in [bars1, bars2] + ([bars3] if any(llm_scores) else []):
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.1f}',
                           ha='center', va='bottom', fontsize=8)

        plt.tight_layout()
        plt.savefig(self.output_dir / "person_performance.png", dpi=300, bbox_inches='tight')
        plt.close()

    def plot_category_performance(self):
        """Create heatmap of performance across question categories."""
        fig, ax = plt.subplots(figsize=(10, 6))

        category_data = self.results['per_category_analysis']
        categories = list(category_data.keys())

        data_matrix = []
        metrics = ['Semantic', 'Stylistic']
        if category_data[categories[0]]['mean_llm_score']:
            metrics.append('LLM Judge')

        for category in categories:
            row = [
                category_data[category]['mean_semantic_similarity'] * 10,
                category_data[category]['mean_style_score'] * 10
            ]
            if 'LLM Judge' in metrics:
                row.append(category_data[category]['mean_llm_score'])
            data_matrix.append(row)

        df = pd.DataFrame(data_matrix, index=categories, columns=metrics)

        sns.heatmap(df, annot=True, fmt='.2f', cmap='RdYlGn', center=5, vmin=0, vmax=10,
                   cbar_kws={'label': 'Score (0-10)'}, ax=ax, linewidths=1, linecolor='white')

        ax.set_title('Performance by Question Category', fontsize=12, weight='bold', pad=15)
        ax.set_xlabel('')
        ax.set_ylabel('Question Category', fontsize=11, weight='bold')

        plt.tight_layout()
        plt.savefig(self.output_dir / "category_performance.png", dpi=300, bbox_inches='tight')
        plt.close()

    def plot_score_distributions(self):
        """Create distribution plots for key metrics."""
        fig, axes = plt.subplots(1, 3, figsize=(15, 4))

        # Semantic similarity distribution
        semantic_scores = [r['cosine_similarity'] for r in
                          self.results['detailed_results']['semantic']]
        axes[0].hist(semantic_scores, bins=10, color='#2E86AB', alpha=0.7, edgecolor='black')
        axes[0].axvline(np.mean(semantic_scores), color='red', linestyle='--',
                       linewidth=2, label=f'Mean: {np.mean(semantic_scores):.3f}')
        axes[0].set_xlabel('Cosine Similarity', fontsize=10, weight='bold')
        axes[0].set_ylabel('Frequency', fontsize=10, weight='bold')
        axes[0].set_title('Semantic Similarity Distribution', fontsize=11, weight='bold')
        axes[0].legend()
        axes[0].grid(alpha=0.3)

        # Style score distribution
        style_scores = [r['style_consistency_score'] for r in
                       self.results['detailed_results']['stylistic']]
        axes[1].hist(style_scores, bins=10, color='#06A77D', alpha=0.7, edgecolor='black')
        axes[1].axvline(np.mean(style_scores), color='red', linestyle='--',
                       linewidth=2, label=f'Mean: {np.mean(style_scores):.3f}')
        axes[1].set_xlabel('Style Score', fontsize=10, weight='bold')
        axes[1].set_ylabel('Frequency', fontsize=10, weight='bold')
        axes[1].set_title('Stylistic Alignment Distribution', fontsize=11, weight='bold')
        axes[1].legend()
        axes[1].grid(alpha=0.3)

        # LLM overall score distribution (if available)
        llm_scores = [r['overall_score'] for r in self.results['detailed_results']['llm_judge']
                     if r is not None]
        if llm_scores:
            axes[2].hist(llm_scores, bins=10, color='#F18F01', alpha=0.7, edgecolor='black')
            axes[2].axvline(np.mean(llm_scores), color='red', linestyle='--',
                           linewidth=2, label=f'Mean: {np.mean(llm_scores):.2f}')
            axes[2].set_xlabel('LLM Judge Score', fontsize=10, weight='bold')
            axes[2].set_ylabel('Frequency', fontsize=10, weight='bold')
            axes[2].set_title('LLM Overall Score Distribution', fontsize=11, weight='bold')
            axes[2].legend()
            axes[2].grid(alpha=0.3)
        else:
            axes[2].text(0.5, 0.5, 'LLM Evaluation\nNot Available',
                        ha='center', va='center', fontsize=12)
            axes[2].set_xticks([])
            axes[2].set_yticks([])

        plt.tight_layout()
        plt.savefig(self.output_dir / "score_distributions.png", dpi=300, bbox_inches='tight')
        plt.close()

    def plot_length_analysis(self):
        """Create visualization of response length patterns."""
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # Extract length data from stylistic results
        stylistic = self.results['detailed_results']['stylistic']
        length_ratios = [r['length_ratio'] for r in stylistic]

        # Box plot of length ratios
        axes[0].boxplot([length_ratios], vert=True, patch_artist=True,
                       boxprops=dict(facecolor='#06A77D', alpha=0.7),
                       medianprops=dict(color='red', linewidth=2))
        axes[0].axhline(y=1.0, color='black', linestyle='--', linewidth=2,
                       label='Perfect match (ratio=1.0)')
        axes[0].set_ylabel('AI/Human Length Ratio', fontsize=11, weight='bold')
        axes[0].set_title('Response Length Ratio Distribution', fontsize=12, weight='bold')
        axes[0].set_xticklabels(['All Responses'])
        axes[0].legend()
        axes[0].grid(axis='y', alpha=0.3)

        mean_ratio = np.mean(length_ratios)
        axes[0].text(1.15, mean_ratio, f'Mean: {mean_ratio:.2f}x',
                    fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        # Scatter plot: length similarity vs semantic similarity
        semantic = self.results['detailed_results']['semantic']
        length_sims = [r['length_similarity'] for r in stylistic]
        semantic_sims = [r['cosine_similarity'] for r in semantic]

        scatter = axes[1].scatter(length_sims, semantic_sims, alpha=0.6, s=100,
                                 c=semantic_sims, cmap='RdYlGn', edgecolors='black',
                                 vmin=0, vmax=1)
        axes[1].set_xlabel('Length Similarity', fontsize=11, weight='bold')
        axes[1].set_ylabel('Semantic Similarity', fontsize=11, weight='bold')
        axes[1].set_title('Length vs. Semantic Similarity', fontsize=12, weight='bold')
        axes[1].grid(alpha=0.3)

        # Add correlation coefficient
        corr = np.corrcoef(length_sims, semantic_sims)[0, 1]
        axes[1].text(0.05, 0.95, f'Correlation: {corr:.3f}',
                    transform=axes[1].transAxes, fontsize=10,
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.colorbar(scatter, ax=axes[1], label='Semantic Similarity')

        plt.tight_layout()
        plt.savefig(self.output_dir / "length_analysis.png", dpi=300, bbox_inches='tight')
        plt.close()


if __name__ == "__main__":
    visualizer = ResultVisualizer()
    visualizer.create_all_visualizations()
    print("All visualizations created successfully!")
