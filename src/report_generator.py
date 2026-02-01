"""
Technical report generator for evaluation results.

Creates a professional 2-page PDF report with visualizations and insights.
"""

import json
from pathlib import Path
from typing import Dict
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.patches as mpatches
import numpy as np


class TechnicalReportGenerator:
    """Generates a professional technical report as PDF."""

    def __init__(self, results_path: str = "outputs/evaluation_results.json"):
        """Initialize with results file."""
        self.results_path = Path(results_path)
        with open(self.results_path, 'r') as f:
            self.results = json.load(f)

        self.figures_dir = Path("outputs/figures")

    def generate_report(self, output_path: str = "outputs/technical_report.pdf"):
        """
        Generate the complete 2-page technical report.

        Args:
            output_path: Path for output PDF file
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with PdfPages(output_path) as pdf:
            # Page 1: Overview and Key Findings
            self._create_page_1(pdf)

            # Page 2: Detailed Analysis and Implications
            self._create_page_2(pdf)

            # Set PDF metadata
            d = pdf.infodict()
            d['Title'] = 'GenAI Human Simulation Evaluation - Technical Report'
            d['Author'] = 'GenAI Evaluation System'
            d['Subject'] = 'Assessment of Generative Agent Simulation Performance'
            d['CreationDate'] = datetime.now()

        print(f"Technical report generated: {output_path}")

    def _create_page_1(self, pdf):
        """Create page 1: Executive summary and overview."""
        fig = plt.figure(figsize=(8.5, 11))  # Letter size
        fig.patch.set_facecolor('white')

        # Title and header
        fig.text(0.5, 0.95, 'TECHNICAL REPORT', ha='center', fontsize=18, weight='bold')
        fig.text(0.5, 0.925, 'Evaluation of Generative Agent Human Simulations',
                ha='center', fontsize=14, style='italic')
        fig.text(0.5, 0.905, f'Evaluation Date: {datetime.now().strftime("%B %d, %Y")}',
                ha='center', fontsize=10, color='gray')

        # Separator line
        fig.add_artist(plt.Line2D([0.1, 0.9], [0.895, 0.895], color='black', linewidth=1.5))

        # Executive Summary
        y_pos = 0.86
        fig.text(0.1, y_pos, 'EXECUTIVE SUMMARY', fontsize=12, weight='bold')

        y_pos -= 0.025
        agg = self.results['aggregate_scores']
        meta = self.results['metadata']

        summary_text = f"""This report evaluates the performance of LLM-based human simulations created for a Beauty &
Wellbeing company's market research. The evaluation assessed {meta['total_pairs']} response pairs from {meta['num_persons']}
individuals across {meta['num_categories']} question categories using a multi-dimensional framework.

KEY FINDINGS:
• Semantic Alignment: {agg['semantic']['mean_cosine_similarity']:.3f} cosine similarity (0-1 scale)
• Stylistic Consistency: {agg['stylistic']['mean_style_score']:.3f} overall style match (0-1 scale)"""

        if agg['llm_judge']['count'] > 0:
            summary_text += f"\n• LLM Judge Assessment: {agg['llm_judge']['mean_overall_score']:.2f}/10 overall score"

        summary_text += f"""
• Critical Issue: AI responses are {agg['stylistic']['mean_length_ratio']:.0f}% longer than human responses
• Only {agg['stylistic']['pct_with_imperfections']:.0f}% of AI responses exhibit human-like imperfections

BENCHMARK CONTEXT:
The referenced paper "Generative Agent Simulations of 1,000 People" achieved 85% accuracy compared
to human test-retest reliability (equivalent to 8.5/10). Our evaluation uses this as a gold standard."""

        fig.text(0.1, y_pos, summary_text, fontsize=9, verticalalignment='top',
                linespacing=1.5, family='monospace')

        # Add overview visualization
        if (self.figures_dir / "overview_scores.png").exists():
            ax1 = fig.add_subplot(3, 2, 3)
            img1 = plt.imread(self.figures_dir / "overview_scores.png")
            ax1.imshow(img1)
            ax1.axis('off')

        # Add dimension comparison
        if (self.figures_dir / "dimension_comparison.png").exists():
            ax2 = fig.add_subplot(3, 2, 4)
            img2 = plt.imread(self.figures_dir / "dimension_comparison.png")
            ax2.imshow(img2)
            ax2.axis('off')

        # Add per-person performance
        if (self.figures_dir / "person_performance.png").exists():
            ax3 = fig.add_subplot(3, 1, 3)
            img3 = plt.imread(self.figures_dir / "person_performance.png")
            ax3.imshow(img3)
            ax3.axis('off')

        plt.tight_layout(rect=[0, 0, 1, 0.89])
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def _create_page_2(self, pdf):
        """Create page 2: Detailed analysis with two-column layout."""
        fig = plt.figure(figsize=(8.5, 11))
        fig.patch.set_facecolor('white')

        # Header
        fig.text(0.5, 0.975, 'DETAILED ANALYSIS & RECOMMENDATIONS', ha='center',
                fontsize=13, weight='bold')
        fig.add_artist(plt.Line2D([0.1, 0.9], [0.965, 0.965], color='black', linewidth=1.5))

        # Top section - Key visualizations (compact)
        # Category performance (left) and Length analysis (right)
        if (self.figures_dir / "category_performance.png").exists():
            ax1 = fig.add_subplot(4, 2, 1)
            img1 = plt.imread(self.figures_dir / "category_performance.png")
            ax1.imshow(img1)
            ax1.axis('off')

        if (self.figures_dir / "length_analysis.png").exists():
            ax2 = fig.add_subplot(4, 2, 2)
            img2 = plt.imread(self.figures_dir / "length_analysis.png")
            ax2.imshow(img2)
            ax2.axis('off')

        # TWO-COLUMN LAYOUT for insights and recommendations
        # Left column: Key Findings
        left_x = 0.08
        right_x = 0.52
        y_start = 0.52

        agg = self.results['aggregate_scores']
        weakest = self.results['weakest_matches']
        person_analysis = self.results['per_person_analysis']

        # === LEFT COLUMN: KEY FINDINGS ===
        y_pos = y_start
        fig.text(left_x, y_pos, 'KEY FINDINGS', fontsize=10, weight='bold')
        y_pos -= 0.025

        # Performance Summary Box
        fig.text(left_x, y_pos, 'Performance vs. Benchmark (85%)', fontsize=8, weight='bold', color='darkblue')
        y_pos -= 0.018

        perf_data = [
            f"Semantic: {agg['semantic']['mean_cosine_similarity']*10:.1f}/10 (Gap: {(8.5-agg['semantic']['mean_cosine_similarity']*10):.1f})",
            f"Stylistic: {agg['stylistic']['mean_style_score']*10:.1f}/10 (Gap: {(8.5-agg['stylistic']['mean_style_score']*10):.1f})",
        ]
        if agg['llm_judge']['count'] > 0:
            perf_data.append(f"LLM Judge: {agg['llm_judge']['mean_overall_score']:.1f}/10 (Gap: {(8.5-agg['llm_judge']['mean_overall_score']):.1f})")

        for item in perf_data:
            fig.text(left_x + 0.01, y_pos, f"• {item}", fontsize=7, family='sans-serif')
            y_pos -= 0.015

        y_pos -= 0.01

        # Critical Issues
        fig.text(left_x, y_pos, 'Critical Issues', fontsize=8, weight='bold', color='red')
        y_pos -= 0.018

        issues = [
            f"Length: {agg['stylistic']['mean_length_ratio']:.1f}× too verbose",
            f"Naturalness: {agg['stylistic']['pct_with_imperfections']:.0f}% authentic",
            "Style: Overly formal & polished"
        ]

        if agg['llm_judge']['count'] > 0:
            issues.append(f"Personality: {agg['llm_judge']['mean_personality_match']:.1f}/10 match")

        for issue in issues:
            fig.text(left_x + 0.01, y_pos, f"⚠ {issue}", fontsize=7, family='sans-serif')
            y_pos -= 0.015

        y_pos -= 0.01

        # Best/Worst Performers
        fig.text(left_x, y_pos, 'Individual Performance', fontsize=8, weight='bold', color='darkgreen')
        y_pos -= 0.018

        best_person = max(person_analysis.items(), key=lambda x: x[1]['mean_semantic_similarity'])
        worst_person = min(person_analysis.items(), key=lambda x: x[1]['mean_semantic_similarity'])

        fig.text(left_x + 0.01, y_pos, f"✓ Best: {best_person[0]} ({best_person[1]['mean_semantic_similarity']:.2f})",
                fontsize=7, family='sans-serif', color='green')
        y_pos -= 0.015
        fig.text(left_x + 0.01, y_pos, f"✗ Worst: {worst_person[0]} ({worst_person[1]['mean_semantic_similarity']:.2f})",
                fontsize=7, family='sans-serif', color='red')
        y_pos -= 0.02

        # LLM Judge Top Weaknesses (if available)
        if agg['llm_judge']['count'] > 0 and agg['llm_judge']['common_weaknesses']:
            fig.text(left_x, y_pos, 'Top AI Weaknesses (LLM Judge)', fontsize=8, weight='bold', color='darkorange')
            y_pos -= 0.018

            for weakness in agg['llm_judge']['common_weaknesses'][:3]:
                w_text = weakness['weakness'][:45] + "..." if len(weakness['weakness']) > 45 else weakness['weakness']
                fig.text(left_x + 0.01, y_pos, f"• {w_text}", fontsize=6.5, family='sans-serif')
                y_pos -= 0.014

        # === RIGHT COLUMN: RECOMMENDATIONS ===
        y_pos = y_start
        fig.text(right_x, y_pos, 'RECOMMENDED ACTIONS', fontsize=10, weight='bold')
        y_pos -= 0.025

        # Priority 1
        fig.text(right_x, y_pos, '1. Length Calibration (CRITICAL)', fontsize=7.5, weight='bold', color='darkred')
        y_pos -= 0.016
        fig.text(right_x + 0.01, y_pos,
                f"Target: 1.0-1.2× (Current: {agg['stylistic']['mean_length_ratio']:.1f}×)\nConstrain AI verbosity to match human patterns.",
                fontsize=6.5, linespacing=1.25)
        y_pos -= 0.035

        # Priority 2
        fig.text(right_x, y_pos, '2. Inject Naturalness', fontsize=7.5, weight='bold', color='darkorange')
        y_pos -= 0.016
        fig.text(right_x + 0.01, y_pos,
                "Add casual language, typos, filler words\n(e.g., 'kinda', 'like', occasional errors).",
                fontsize=6.5, linespacing=1.25)
        y_pos -= 0.035

        # Priority 3
        fig.text(right_x, y_pos, '3. Personality Tuning', fontsize=7.5, weight='bold', color='darkgreen')
        y_pos -= 0.016
        fig.text(right_x + 0.01, y_pos,
                f"Individual-specific prompting.\nFocus on: {worst_person[0]} (weakest performer).",
                fontsize=6.5, linespacing=1.25)
        y_pos -= 0.035

        # Priority 4
        fig.text(right_x, y_pos, '4. Category Optimization', fontsize=7.5, weight='bold', color='darkblue')
        y_pos -= 0.016

        # Find worst category
        cat_analysis = self.results['per_category_analysis']
        worst_cat = min(cat_analysis.items(), key=lambda x: x[1]['mean_semantic_similarity'])

        fig.text(right_x + 0.01, y_pos,
                f"Address '{worst_cat[0]}' weakness\n({worst_cat[1]['mean_semantic_similarity']:.2f} score).",
                fontsize=6.5, linespacing=1.25)
        y_pos -= 0.035

        # Priority 5
        fig.text(right_x, y_pos, '5. Iterative Refinement', fontsize=7.5, weight='bold', color='purple')
        y_pos -= 0.016
        fig.text(right_x + 0.01, y_pos,
                "Use this framework for feedback loop.\nTarget: 80%+ benchmark accuracy.",
                fontsize=6.5, linespacing=1.25)

        # Bottom: Example box with background rectangle
        y_pos = 0.135

        # Add background rectangle
        import matplotlib.patches as patches
        rect = patches.Rectangle((0.07, 0.04), 0.86, 0.09, linewidth=1,
                                edgecolor='gray', facecolor='lightyellow', alpha=0.3)
        fig.add_artist(rect)

        fig.text(0.08, y_pos, 'WORST MATCH EXAMPLE', fontsize=8, weight='bold', color='darkred')
        y_pos -= 0.015

        example_box_text = f"Q: {weakest[0]['question'][:85]}...\n"
        example_box_text += f"Human ({len(weakest[0]['human_answer'])} chars): \"{weakest[0]['human_answer'][:95]}...\"\n"
        example_box_text += f"AI ({len(weakest[0]['ai_answer'])} chars): \"{weakest[0]['ai_answer'][:95]}...\"\n"
        example_box_text += f"Score: {weakest[0]['composite_score']:.2f} | Category: {weakest[0]['category']}"

        fig.text(0.08, y_pos, example_box_text, fontsize=6, verticalalignment='top',
                family='monospace', linespacing=1.2)

        # Footer with conclusion - simple text, no bbox
        fig.text(0.5, 0.022,
                'CONCLUSION: Simulations need refinement. With targeted fixes, can close performance gap.',
                ha='center', fontsize=7, weight='bold', style='italic', color='darkblue')

        fig.text(0.5, 0.01, 'Page 2 of 2 | Confidential',
                ha='center', fontsize=7, color='gray', style='italic')

        plt.tight_layout(rect=[0, 0.03, 1, 0.96])
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()


if __name__ == "__main__":
    report_gen = TechnicalReportGenerator()
    report_gen.generate_report()
    print("Technical report generated successfully!")
