# GenAI Human Simulation Evaluation

Professional evaluation framework for assessing LLM-based human simulations against real human responses.

## Overview

This solution evaluates how accurately AI-generated human simulations mimic real human behavior in market research interviews. It uses a **multi-dimensional evaluation framework** inspired by the paper "Generative Agent Simulations of 1,000 People" (arXiv:2411.10109).

### Evaluation Results

<p align="center">
  <img src="outputs/figures/dimension_comparison.png" alt="Performance Across Dimensions" width="700"/>
  <br>
  <em>Performance comparison across semantic, stylistic, and LLM-as-judge evaluation dimensions</em>
</p>

<p align="center">
  <img src="outputs/figures/category_performance.png" alt="Performance by Category" width="700"/>
  <br>
  <em>Performance breakdown across different question categories</em>
</p>

## Evaluation Framework

### Core Dimensions

1. **Semantic Similarity** - Content alignment using sentence embeddings
   - Cosine similarity between response embeddings
   - Captures whether the AI conveys the same meaning

2. **Stylistic Analysis** - Linguistic feature comparison
   - Response length patterns
   - Readability and complexity metrics
   - Formality levels
   - Presence of human-like imperfections (typos, casual language)

3. **LLM-as-Judge** - Holistic expert assessment
   - Claude-based evaluation across multiple dimensions
   - Semantic, style, personality, and naturalness scoring
   - Identification of specific AI weaknesses

### Aggregate Analysis

- Per-person performance tracking
- Per-category performance analysis
- Identification of weakest simulation matches
- Statistical significance testing

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Download required NLTK data
python -c "import nltk; nltk.download('punkt')"
```

## Usage

### Quick Start

```bash
# Run complete evaluation pipeline
python run_full_evaluation.py
```

This will:
1. Load and validate the dataset
2. Run multi-dimensional evaluation
3. Generate visualizations
4. Save results to JSON

### Individual Components

```bash
# Run evaluation only
python evaluate.py

# Generate visualizations (requires evaluation results)
python src/visualizations.py
```

### Configuration

Set environment variable for LLM judge evaluation:

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

**Note:** LLM judge evaluation is optional. If no API key is provided, the system will skip this component and proceed with semantic and stylistic evaluation.

## Output Files

```
outputs/
├── evaluation_results.json     # Raw evaluation data
└── figures/                    # Visualization charts
    ├── overview_scores.png
    ├── dimension_comparison.png
    ├── person_performance.png
    ├── category_performance.png
    ├── score_distributions.png
    └── length_analysis.png
```

## Architecture

```
├── data/
│   └── RB_GenAI_Datatest.xlsx      # Input dataset (3 people × 10 questions)
├── src/
│   ├── data_loader.py               # Data loading and structuring
│   ├── evaluators/
│   │   ├── semantic_similarity.py   # Embedding-based similarity
│   │   ├── stylistic_analysis.py    # Linguistic feature analysis
│   │   └── llm_judge.py            # Claude-based evaluation
│   └── visualizations.py            # Chart generation
├── evaluate.py                      # Main evaluation script
└── run_full_evaluation.py          # Master pipeline orchestrator
```

## Key Features

✅ **Async I/O**: Concurrent LLM API calls with rate limiting  
✅ **Professional Code**: Type hints, docstrings, clean architecture  
✅ **Robust Metrics**: Multi-dimensional evaluation beyond simple similarity  
✅ **Small Dataset Handling**: Appropriate statistics for 30 samples  
✅ **Beautiful Visualizations**: Publication-quality charts  
✅ **Comprehensive Documentation**: Clear code and usage instructions

## Methodology Highlights

### Why Multi-Dimensional?

Single metrics miss critical nuances:
- High semantic similarity but wrong style = unconvincing simulation
- Perfect length but wrong content = failure
- Polished responses without human quirks = detectably artificial

Our framework captures all these dimensions.

### Benchmark Context

The referenced paper achieved **85% accuracy** vs. human test-retest reliability on the General Social Survey. We use this as a gold standard (8.5/10 score) for comparison.

### Small Dataset Considerations

With only 30 samples (3 people × 10 questions):
- Use robust, interpretable metrics
- Provide per-person and per-category breakdowns
- Report confidence intervals where appropriate
- Focus on practical insights over statistical significance

## Example Results

```
EVALUATION SUMMARY
================================================================

📊 SEMANTIC SIMILARITY
  Mean: 0.723
  Range: [0.524, 0.891]

✍️  STYLISTIC ALIGNMENT
  Mean style score: 0.612
  Length ratio (AI/Human): 1.84x
  Responses with human-like imperfections: 23.3%

🤖 LLM JUDGE ASSESSMENT
  Overall score: 6.2/10
  Semantic match: 7.1/10
  Style match: 5.8/10
  Personality match: 5.4/10
  Naturalness: 5.7/10
```

## References

- Park, J. S., et al. (2024). "Generative Agent Simulations of 1,000 People" arXiv:2411.10109
- [Paper Link](https://arxiv.org/abs/2411.10109)

---

*Multi-dimensional evaluation framework for AI-generated human simulations*
