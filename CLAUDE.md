# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Roland Berger GenAI Assignment evaluating the performance of generative agent simulations (human simulations). The goal is to assess how accurately LLM-based human simulations mimic real human behavior based on interview responses.

**Context:**
- Client: Beauty & Wellbeing company targeting young business professionals
- Approach: Based on paper "Generative Agent Simulations of 1,000 People" (https://arxiv.org/pdf/2411.10109)
- Data: 3 human participants, 10 open-ended questions each
- Comparison: Human responses vs. AI-generated human simulation responses

## Dataset Structure

**File:** `RB_GenAI_Datatest.xlsx`

Columns:
- Question Category: Market research category (e.g., shopping behavior)
- Question Text: The open-ended question
- Person ID: Unique identifier (3 persons total)
- Human Answer: Real human response
- AI Answer: Human simulation response

## Deliverables

The assignment requires three outputs:

1. **Code**: Source code implementing evaluation methodology
2. **Technical Report**: 2-page PDF with evaluation concept, results, insights
3. **Pitch Slide Deck**: 3 core slides (+ intro/appendix) in strategy consultancy style for CEO presentation

**Submission:** hannes.gerstel@rolandberger.com within 24 hours (recommended: 8 hours)

## Evaluation Requirements

The solution must:
- Define specific evaluation criteria with measurement methods and rationale
- Measure alignment between AI and human responses
- Identify strengths/weaknesses of the approach
- Highlight areas where simulations fail to mimic humans
- Use any GenAI-based approach (LLM chains, graph agents, transformers, etc.)

## Development Commands

Since this is a new project, typical commands will depend on the chosen implementation approach:

**Python-based (recommended):**
```bash
# Install dependencies
pip install -r requirements.txt

# Run evaluation
python evaluate.py

# Run with specific metrics
python evaluate.py --metrics semantic,sentiment,style

# Generate report
python generate_report.py

# Run tests
pytest tests/
```

**Jupyter Notebook approach:**
```bash
jupyter notebook evaluation.ipynb
```

## Architecture Guidance

**Recommended Structure:**

```
├── data/
│   └── RB_GenAI_Datatest.xlsx          # Input dataset
├── src/
│   ├── data_loader.py                   # Load and parse Excel data
│   ├── evaluators/
│   │   ├── semantic_similarity.py       # Semantic alignment metrics
│   │   ├── sentiment_analysis.py        # Emotional tone matching
│   │   ├── linguistic_style.py          # Writing style comparison
│   │   └── content_coverage.py          # Topic/entity coverage
│   ├── llm_evaluator.py                 # LLM-as-judge evaluation
│   └── report_generator.py              # Generate results and insights
├── outputs/
│   ├── results.json                     # Evaluation scores
│   ├── technical_report.pdf             # 2-page report
│   └── pitch_deck.pptx                  # Executive presentation
├── tests/
│   └── test_evaluators.py
├── requirements.txt
└── evaluate.py                          # Main entry point
```

**Key Architectural Decisions:**

1. **Multi-dimensional Evaluation**: Don't rely on single metric. Combine:
   - Semantic similarity (embeddings, cosine similarity)
   - LLM-as-judge (GPT-4/Claude scoring alignment)
   - Linguistic features (length, complexity, formality)
   - Content analysis (named entities, topics, sentiment)

2. **Per-Person Analysis**: Track performance by Person ID to identify if simulations work better for certain individuals

3. **Question Category Analysis**: Evaluate performance across different question types (shopping behavior, product preferences, etc.)

4. **Statistical Aggregation**: Provide both aggregate metrics and per-question/per-person breakdowns

## Key Considerations

**Data Handling:**
- Only 30 data points (3 persons × 10 questions) - small dataset
- Need robust metrics that work with limited data
- Consider bootstrapping or cross-validation carefully

**Evaluation Challenges:**
- Open-ended responses have no "ground truth" beyond human answer
- Responses can be semantically similar but stylistically different
- Need to balance factual accuracy vs. personality/style mimicry
- Avoid over-reliance on exact string matching

**LLM API Usage:**
- If using OpenAI/Anthropic APIs, set API keys via environment variables
- Consider rate limits and costs when processing all responses
- Cache embeddings to avoid redundant API calls

**Report Generation:**
- Technical report must fit 2 pages - prioritize key findings
- Pitch deck requires strategy consultancy style (clear, visual, structured)
- Include concrete examples of good/bad simulation matches

## Important Notes

- This is an artificial test with no connection to real companies
- Focus on methodology rigor rather than perfect results
- Document limitations and potential improvements
- Consider practical scalability to 1,000+ simulations (per original paper)
