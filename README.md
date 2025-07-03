# Ready Tensor Agentic AI Certification – Week 7

This repository contains lesson materials, code examples, and evaluation scripts for **Week 7** of the [Agentic AI Developer Certification Program](https://app.readytensor.ai/publications/HrJ0xWtLzLNt) by Ready Tensor. This week is all about **evaluating agentic systems** — how to measure performance, diagnose behavior, and build trust in AI that thinks and acts.

⚠️ Note: Code examples for Lessons 4, 5, and 6 will be added soon. We’re actively finalizing the evaluation scripts and datasets to ensure clarity and alignment with the lesson content. Stay tuned — updates coming shortly!

---

## What You'll Learn

- Why traditional evaluation breaks down for adaptive, agentic systems
- A practical toolkit of evaluation methods — from LLM-as-judge to red teaming
- How to select the right metrics based on your system’s goals and design
- How to use **RAGAS** for scoring retrieval-augmented generation pipelines
- How to use **DeepEval** for multi-step evaluation with custom metrics
- How to evaluate **multi-agent systems** — measuring coordination, not just components

---

## Lessons in This Repository

### 1. Evaluating Agentic AI: Beyond Traditional Testing

Learn why adaptive AI systems require new thinking in evaluation. We go beyond test cases and accuracy scores to ask: What does “success” look like for a system that reasons, adapts, and collaborates?

### 2. The Evaluation Toolkit: Methods for Testing Agentic AI

Explore seven hands-on methods — from human review to red teaming to automated scoring. Understand strengths, weaknesses, and best-fit use cases for each.

### 3. Your System, Your Metrics: A Practical Guide to Agentic Evaluation

Choose evaluation metrics that actually matter. We walk through seven design dimensions (like output type and interaction mode) to help you tailor metrics to your own system.

### 4. How to Evaluate LLM Applications: A Complete RAGAS Tutorial

Hands-on walkthrough of **RAGAS** — a framework for evaluating RAG pipelines. Learn how to generate test sets, define evaluation workflows, and create custom metrics.

### 5. How to Evaluate LLM Applications: A Complete DeepEval Tutorial

Dive into **DeepEval**, a flexible evaluation toolkit for real-world LLM apps. Learn how to create structured evaluation flows, define correctness and faithfulness, and integrate with your dev workflow.

### 6. Evaluating Multi-Agent AI Systems: A Comprehensive Case Study

A real case study for evaluating a multi-agent system using golden datasets, coordination metrics, and system-level scoring. Learn how to assess collaboration — not just component quality.

---

## Repository Structure

```txt
rt-agentic-ai-cert-week7/
├── code/
│   ├── llm.py                                  # LLM utility wrapper
│   ├── paths.py                                # Standardized file path management
│   ├── prompt_builder.py                       # Modular prompt construction functions
│   ├── run_lesson4_ragas_eval.py                 # Lesson 4: Example script for RAGAS-based evaluation
│   ├── run_lesson5_deepeval_demo.py              # Lesson 5: Evaluation pipeline using DeepEval
│   ├── run_lesson6_multiagent_case_study.py      # Lesson 6: Multi-agent evaluation case study
│   └── utils.py                                # Common utilities
├── config/                                       # Configuration files
├── data/                                         # Input data for code examples
├── outputs/                                      # Output files from code examples
├── lessons/                                      # Lesson content and assets
├── .env.example                                  # Sample environment file (e.g., for API keys)
├── .gitignore
├── LICENSE
├── README.md                                     # You are here
└── requirements.txt                              # Python dependencies for evaluation tools
```

---

## Installation & Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/readytensor/rt-agentic-ai-cert-week7.git
   cd rt-agentic-ai-cert-week7
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your environment variables:**

   Copy the `.env.example` to `.env` and fill in required values (e.g., OpenAI or Groq API keys):

   ```bash
   cp .env.example .env
   ```

---

## Running the Evaluation Examples

Each code example is runnable as a standalone script:

- **Lesson 4 – RAGAS Evaluation:**

  ```bash
  python code/run_lesson4_ragas_eval.py
  ```

- **Lesson 5 – DeepEval Evaluation:**

  ```bash
  python code/run_lesson5_deepeval_demo.py
  ```

- **Lesson 6 – Multi-Agent Evaluation:**

  ```bash
  python code/run_lesson6_multiagent_case_study.py
  ```

Evaluation reports will be saved to the `outputs/evaluation_reports/` folder.

---

## License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

---

## Contact

**Ready Tensor, Inc.**

- Email: contact at readytensor dot com
- Issues & Contributions: Open an issue or PR on this repo
- Website: [https://readytensor.ai](https://readytensor.ai)
