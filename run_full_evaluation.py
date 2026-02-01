#!/usr/bin/env python3
"""
Master script to run the complete evaluation pipeline.

This orchestrates:
1. Data loading and validation
2. Multi-dimensional evaluation
3. Results analysis
4. Visualization generation
5. Technical report creation
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from visualizations import ResultVisualizer
from report_generator import TechnicalReportGenerator


async def main():
    """Run the complete evaluation pipeline."""
    print("=" * 70)
    print("GenAI HUMAN SIMULATION EVALUATION PIPELINE")
    print("=" * 70)

    # Step 1: Run evaluation
    print("\n[1/4] Running multi-dimensional evaluation...")
    print("-" * 70)

    # Import and run main evaluation
    from evaluate import ComprehensiveEvaluator
    evaluator = ComprehensiveEvaluator()
    await evaluator.run_evaluation()
    evaluator.save_results()

    # Step 2: Generate visualizations
    print("\n[2/4] Generating visualizations...")
    print("-" * 70)
    visualizer = ResultVisualizer()
    visualizer.create_all_visualizations()

    # Step 3: Generate technical report
    print("\n[3/4] Creating technical report (PDF)...")
    print("-" * 70)
    report_gen = TechnicalReportGenerator()
    report_gen.generate_report()

    # Step 4: Summary
    print("\n[4/4] Pipeline complete!")
    print("=" * 70)
    print("\n📁 OUTPUT FILES:")
    print("  • outputs/evaluation_results.json - Raw evaluation data")
    print("  • outputs/figures/*.png - Visualization charts")
    print("  • outputs/technical_report.pdf - 2-page technical report")
    print("\n🎯 NEXT STEPS:")
    print("  • Review the technical report for key findings")
    print("  • Create pitch deck based on insights (manual step)")
    print("  • Validate results with stakeholders")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nEvaluation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
