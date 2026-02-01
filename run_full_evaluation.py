#!/usr/bin/env python3
"""
Master script to run the complete evaluation pipeline.

This orchestrates:
1. Data loading and validation
2. Multi-dimensional evaluation
3. Results analysis
4. Visualization generation
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from visualizations import ResultVisualizer


async def main():
    """Run the complete evaluation pipeline."""
    print("=" * 70)
    print("GenAI HUMAN SIMULATION EVALUATION PIPELINE")
    print("=" * 70)

    # Step 1: Run evaluation
    print("\n[1/3] Running multi-dimensional evaluation...")
    print("-" * 70)

    # Import and run main evaluation
    from evaluate import ComprehensiveEvaluator
    evaluator = ComprehensiveEvaluator()
    await evaluator.run_evaluation()
    evaluator.save_results()

    # Step 2: Generate visualizations
    print("\n[2/3] Generating visualizations...")
    print("-" * 70)
    visualizer = ResultVisualizer()
    visualizer.create_all_visualizations()

    # Step 3: Summary
    print("\n[3/3] Pipeline complete!")
    print("=" * 70)
    print("\n📁 OUTPUT FILES:")
    print("  • outputs/evaluation_results.json - Raw evaluation data")
    print("  • outputs/figures/*.png - Visualization charts (6 charts)")
    print("\n🎯 KEY METRICS:")
    print("  • Semantic similarity analysis")
    print("  • Stylistic alignment (with emotional analysis)")
    print("  • LLM-as-judge holistic assessment")
    print("  • Per-person and per-category breakdowns")
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
