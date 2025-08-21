## OpenUI Eval

## Weeks 1 to 11 Progress (GSoC work log)

This document records my work over the first half of the 22‑week plan. I spent the first 3–4 weeks on research, architecture, and alignment, then implemented Single File Evaluation, basic Ollama setup follwed by JS framework setup, and provider adapters. Everything listed here runs locally. I am on track for the remaining half.

### What I built so far

- **Core pipeline**: End‑to‑end generation → rendering → judging with iterative improvement and structured outputs
- **Single File Evaluation**: Complete, multi‑iteration with screenshot feedback loop
- **Framework projects**: React 19, Next.js 15, Vue 3.5, Angular 20, Svelte 5 project creation and rendering
- **Providers**: Adapters for `ollama`, `vLLM`, and `OpenRouter` integrated and working locally
- **Judging**: Multi‑model judge with Pydantic schemas and summary reporting
- **Config + CLI**: Reproducible runs via `config.yaml`, `main.py`, `evaluate_run.py`
- **Artifacts**: Timestamped generations, screenshots (full + LLM‑optimized), per‑task summaries, final benchmark summary

### Codebase notes (hexagonal ports and adapters)

- **Config**: `src/core/config.py` provides typed configs for models, tasks, rendering, projects, providers, and evaluation, with YAML support and env overrides.
- **Logging**: `src/core/logger.py` produces rich console logs and structured JSONL with rotating, compressed files and API call stats.
- **Pipeline**: `src/pipeline/benchmark_pipeline.py` orchestrates setup, iterative HTML generation or framework project generation, rendering, judging, and summaries.
- **Providers**: `src/models/{ollama_provider.py,vllm_provider.py,openrouter_provider.py}` behind `LLMProvider` and `provider_factory.py` with conversation history support and structured calls.
- **Model manager**: `src/models/model_manager.py` handles model lifecycle, memory guardrails, retries, and per‑model statistics.
- **Generation**: `src/generation/html_generator.py` and `project_generator.py` handle initial and improved outputs across iterations with screenshot‑guided prompts.
- **HTML processing**: `src/generation/html_processor.py` extracts, validates, saves, and analyzes HTML content.
- **Rendering**: `src/rendering/renderer.py` (Selenium/Chrome) and `src/rendering/node_renderer.py` for framework projects, including LLM‑optimized screenshots.
- **Frameworks**: `src/frameworks/*` base and implementations for React, Next.js, Vue, Angular, Svelte with project templates, install/build/dev commands, and validation.
- **Evaluation**: `src/evaluation/judge.py` and `evaluation_schemas.py` define criteria, compute per‑iteration and task summaries, and aggregate reports.
- **Tasks**: `src/tasks/task_definitions.py` contains a rich taxonomy across calculators, websites, dashboards, games, forms, interactive apps, and framework‑specific tasks.

### Data and artifacts convention

- Results live under `results/<timestamp>/<model>/<task>/v{n}.{html,metadata.json,screenshot.png,_llm.png}`
- Per‑task evaluation JSONs saved next to generations; per‑task summary and global `benchmark_summary.json` produced by the pipeline

---

## Weeks 1–11: what I did

### Week 1: kickoff and scope

- Finalized scope to build a benchmark (not a leaderboard)
- Collected resources and prior work for UI and SWE evaluation
- Wrote success criteria and split the 22 weeks

### Week 2: architecture alignment

- Chose a hexagonal setup with providers as adapters
- Defined module boundaries for config, providers, generation, rendering, evaluation
- Designed artifact layout and reproducible runs

### Week 3: research pass I

- Read prior work on LLM‑as‑judge, screenshot feedback, and iterative refinement,
- Learn more about Multi-SWE-bench and WebDev Arena, and their tasks and datasets
- Drafted a first task taxonomy for single‑file HTML
- Wrote initial criteria and scoring scale for judging

### Week 4: research and meetings

- After having meeting with mentors, decided on framework: React 19, Next.js 15, Vue 3.5, Angular 20, Svelte 5
- Also decided on task taxonomy and evaluation criteria
- Wrote minimal templates and validated install/build/dev flows
- Finalized prompt shapes for initial and improvement iterations

### Week 5: configuration and CLI

- Implemented `Config` with typed dataclasses and YAML round‑trip
- Added `main.py` CLI for full, generation‑only, or judging‑only modes
- Added `evaluate_run.py` to re‑judge a past run and write summaries there
- Added working POC for single file evaluation using Ollama and HTML generation.

### Week 6: providers and model manager

- ~Implemented Gemini as provider~ (reverted for now)
- Implemented more adapters eg `vLLM`, and `OpenRouter`
- Built `ModelManager` with memory thresholds, LRU unload, retries, and history
- Verified local runs across multiple models (gemma3n:e4b, gemma3:4b, qwen2.5vl:7b, granite3.2-vision:2b, llama3.2-vision:11b, minicpm-v:8b, llava-phi3:3.8b)

### Week 7: Single File Evaluation with iterations

- Built `HTMLGenerator`: extract → validate → render → screenshot → improve
- Implemented `HTMLProcessor` to clean and validate varied outputs
- Saved per‑iteration metadata and LLM‑optimized screenshots for judges (using `gemma3n:e4b` as judge)

### Week 8: judging and summaries

- Implemented evaluation prompt and per‑iteration evaluation across multiple judges
- Wrote benchmark summary with model scores and task difficulty

### Week 9: framework project path

- Implemented `ProjectGenerator` and `NodeProjectRenderer` for create → install → dev → screenshot
- Validated React, Next.js, Vue, Angular, Svelte flows on Node 22 LTS (local)

### Week 10: results, logging, and resilience

- Added structured JSONL logs and API call stats (for debugging)
- Saved system info and standardized result folders
- Improved error handling so partial progress is kept

### Week 11: stabilization and docs pass

- Cleaned up `config.yaml` with defaults and examples
- Ran end‑to‑end jobs to populate `results/` and `summaries/`
- Wrote this progress log

Mentor inputs: I met with Paige Bailey and Vaibhav Tulsyan
(GSoC mentors) and incorporated feedback on scope and judging.

---

## Current capabilities

- Single HTML file tasks with iterative improvement and screenshot‑guided prompts
- Multi‑file JS frameworks: project creation, install, run, and screenshot albeit not all models are capable of handling all of the frameworks without documentation and support.
- Multiple providers: `ollama`, `vLLM`, `OpenRouter` working locally
- Multi‑judge structured scoring with criteria and blind evaluation prompt
- Re‑evaluation of past runs, per‑task and summaries

## Task taxonomy (first set)

- Calculators, websites, dashboards, games, forms, interactive apps
- Framework variants for React, Vue, Next.js, Angular, Svelte
- Emphasis on visual quality, responsiveness, and clear UI structure (not interaction, stat emanagement and other website metrics so far)

## Plan for weeks 12–22 (also detailed in the doc)

### High‑level objectives

- Improve judges (use a single big model as judge) and reliability
- Expand task difficulty (2-3 good tasks) and data sources
- Add responsiveness and interaction‑based checks
- Normalize scores across tasks and models
- Harden sandboxing and reproducibility
- Documentation, dockerization, and publishing

---
