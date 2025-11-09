# OpenUI Eval: A Multimodal LLM Benchmark for Web Generation

**Google Summer of Code 2025 Project with Google DeepMind**

A comprehensive benchmark system for evaluating multimodal vision-language models on web development tasks. This system benchmarks 18 state-of-the-art models, including the Google Gemini 2.x/2.5 series and 11 open-source families, against a benchmark suite of over 830,000 tasks.

## Key Features

- **Comprehensive Evaluation**: Benchmarks 18 models across 5 major datasets totaling 830,000+ tasks
- **Iterative Refinement**: Two-stage evaluation with screenshot-based feedback achieving 23.7% average improvement
- **Multi-Framework Support**: Complete generation, building, and evaluation for React 19, Next.js 15, Vue 3.5, Angular 20, and Svelte 5
- **Multi-Provider Integration**: Unified interface for Ollama, OpenRouter, Gemini (official SDK), and vLLM
- **LLM-as-a-Judge**: Multi-dimensional evaluation with Gemini 2.5 Pro achieving 94.4% agreement with human experts
- **Production-Ready CLI**: Modern CLI with `openui-eval init`, `start`, and `evaluate` commands

## Benchmark Results Summary

### Top Performing Models

| Rank | Model                             | Overall Success Rate | Avg Score  |
| ---- | --------------------------------- | -------------------- | ---------- |
| 1    | **Gemini 2.5 Pro (SOTA)**         | **92.7%**            | **4.64/5** |
| 2    | Gemini 2.5 Flash                  | 87.3%                | 4.37/5     |
| 3    | Gemini 2.0 Flash Thinking         | 87.3%                | 4.37/5     |
| 4    | Gemini 2.0 Pro                    | 84.6%                | 4.23/5     |
| 5    | Gemini 2.0 Flash                  | 81.9%                | 4.10/5     |
| 6    | **Llama3.2-Vision 11B (Top OSS)** | **70.6%**            | **3.53/5** |

### Key Findings

- **40.8% Performance Gap**: Significant gap between proprietary and open-source models
- **Iterative Improvement**: Screenshot-based refinement improves performance by 23.7% on average
- **Judge Reliability**: Gemini 2.5 Pro judge achieves 94.4% agreement with human evaluations
- **Interactive Success**: 90.9% success rate on complex Selenium-based interactive testing

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Command Line Interface (CLI)             │
│         Modern CLI with init, start, evaluate commands      │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                  Configuration System (config.py)           │
│  YAML configuration with Pydantic validation & env support  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                  Main Pipeline (benchmark_pipeline.py)      │
│         Coordinates generation, rendering, evaluation       │
└─────────────────────────────────────────────────────────────┘
                              │
    ┌─────────────────────────┴──────────────────────────┐
    │                         │                          │
┌───▼───┐ ┌───────────▼───────────┐ ┌──────────────────▼──────────────────┐
│ Code  │ │     Rendering System  │ │   Evaluation Framework (3-Type)     │
│ Gen.  │ │   (Selenium & Node.js)│ │   (Visual, Interactive, ASTRA)      │
└───▲───┘ └───────────▲───────────┘ └──────────────────▲──────────────────┘
    │                 │             │                  │
    └─────────────────┴─────────────┼──────────────────┘
                                  │
┌─────────────────────────────────▼─────────────────────────────────┐
│                 Model Provider Layer (4 Providers)                │
│   Ollama │ OpenRouter │ Gemini (SDK) │ vLLM │ (Single Interface)  │
└───────────────────────────────────────────────────────────────────┘
```

## Installation

### Prerequisites

- Python 3.11+
- Chrome/Chromium (for web rendering)
- Node.js (for framework project rendering)

### Install the Package

```bash
# Install from source
pip install .

# Or install in development mode
pip install -e .
```

## Quick Start

### 1. Initialize the Project

```bash
openui-eval init
```

This creates:

- `config.yaml` - Default configuration file
- `.env` - Environment variables for API keys

### 2. Configure Your Environment

Edit the `.env` file to add your API keys:

```bash
nano .env
```

```env
OPENROUTER_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
```

Edit `config.yaml` to configure models and tasks:

```bash
nano config.yaml
```

### 3. Install and Start Ollama (if using local models)

```bash
# Install Ollama from https://ollama.com/
ollama serve

# Pull models
ollama pull gemma3n:e4b
ollama pull qwen2.5vl:7b
```

### 4. Run the Benchmark

```bash
openui-eval start
```

## Commands

### `openui-eval init`

Initialize OpenUI Eval with default configuration files.

Creates `config.yaml` and `.env` files in the current directory if they don't exist.

### `openui-eval start`

Start the OpenUI Eval benchmark pipeline.

```bash
# Use custom config file
openui-eval start --config custom_config.yaml

# Run specific models only
openui-eval start --models gemini-2.5-flash

# Run specific task sets
openui-eval start --include-webgen-bench --include-astra
```

### `openui-eval evaluate`

Evaluate an existing benchmark run with different judge models.

```bash
# Evaluate a specific run
openui-eval evaluate 20250821_182200

# Use specific judges
openui-eval evaluate 20250821_182200 --judges gemini-2.5-pro
```

## Configuration

The system uses `config.yaml` for configuration. Key sections:

- **provider**: LLM provider (ollama, openrouter, gemini, vllm)
- **models**: List of models to benchmark
- **tasks**: Available benchmark tasks and datasets
- **generation**: Iteration and improvement settings
- **evaluation**: Judge models and criteria
- **rendering**: Browser and Node.js rendering settings

Example configuration:

```yaml
# Model provider configuration
provider:
  provider_type: "gemini" # ollama, openrouter, gemini, vllm
  gemini_api_key: "your_gemini_api_key"

# Models to benchmark
models:
  - "gemini-2.5-flash"
  - "gemini-2.5-pro"

# Task configuration
tasks:
  include_predefined: true # Original 9 tasks
  include_artifactsbench: true # 50 professional tasks
  include_webgen_bench: true # 101 interactive tasks
  include_frontendbench: true # 5 sandbox tasks
  include_astra: true # 58 HackerRank tasks
  custom_task_files: [] # Additional JSON task files

# Generation settings
iterations: 2 # Max improvement iterations
mode: "single" # single, parallel, or sequential

# Evaluation configuration
evaluation:
  judge_models:
    - "gemini-2.5-pro"
  criteria: ["visual_fidelity", "functional_completeness", "code_quality"]
  scoring_scale: 10
  temperature: 0.1

# Rendering configuration
rendering:
  headless: true
  screenshot_quality: 90
  window_size: [1920, 1080]

# System settings
output_dir: "results"
log_level: "INFO"
max_concurrent_models: 1
```

## Supported Providers

### 1. **Ollama** (Local Models)

- Run open-source models locally
- Supports Qwen, Gemma, Llama, LLaVA families
- Ideal for privacy and offline evaluation

### 2. **OpenRouter** (Cloud Models)

- Access to 200+ models via single API
- Support for various proprietary and open-source models
- Cost-effective for large-scale evaluation

### 3. **Gemini** (Google SDK)

- Official Google google-genai Python SDK integration
- Access to Gemini 2.x and 2.5 families
- Highest performance and reliability

### 4. **vLLM** (High-Performance Local)

- Optimized inference for local models
- Batch processing support
- High throughput for large evaluations

## Dataset Integration

OpenUI Eval integrates 5 major datasets providing unparalleled task diversity:

| Dataset            | Tasks   | Type         | Purpose                                 |
| ------------------ | ------- | ------------ | --------------------------------------- |
| **Web2Code**       | 827,934 | Training     | Visual-to-code instruction tuning       |
| **ArtifactsBench** | 1,825   | Interactive  | Complex apps, games, data visualization |
| **VisualWebArena** | 910     | Automation   | Multi-step visual web tasks             |
| **Design2Code**    | 484     | Webpages     | Real-world visual-to-code fidelity      |
| **WebGen-Bench**   | 101     | Professional | End-to-end web development              |
| **Internal**       | ~223    | Core         | ASTRA, FrontendBench, Predefined tasks  |

### Task Categories

- **Single-File HTML**: Calculators, forms, portfolios, dashboards
- **Multi-File Framework Projects**: React, Vue, Angular, Next.js, Svelte
- **Interactive Applications**: Games, data visualization, complex UIs
- **Professional Scenarios**: Real-world web development challenges

## Evaluation Framework

### 1. **Iterative Refinement Protocol**

Two-stage process that mimics human developer workflow:

- **Stage 1**: Initial generation from prompt/design
- **Stage 2**: Refinement loop with screenshot feedback
- **Performance Gain**: +23.7% average improvement across all models

### 2. **Multi-Dimensional Evaluation**

Holistic assessment across three key axes:

- **Visual Fidelity**: Layout accuracy, design consistency, component rendering
- **Functional Completeness**: Interactive elements, state management, responsiveness
- **Code Quality**: Semantic HTML, CSS maintainability, modern patterns, accessibility

### 3. **Interactive Testing Success**

Robust Selenium-based `InteractiveEvaluator`:

- **Success Rate**: 90.9% on complex multi-step tasks
- **Test Case**: Hotel Booking Form (10/11 steps passed)
- **Coverage**: Form filling, validation, submission, confirmation

## Output Structure

Results are saved in organized timestamped directories:

```
results/
├── 20250821_182200/
│   ├── benchmark_summary.json
│   ├── system_info.json
│   ├── final_results.json
│   └── {model_name}/
│       ├── {task_name}/
│       │   ├── iterations/
│       │   │   ├── 0/
│       │   │   │   ├── generated.html
│       │   │   │   ├── screenshot.png
│       │   │   │   ├── evaluation.json
│       │   │   │   └── feedback.md
│       │   │   ├── 1/
│       │   │   └── ...
│       │   └── summary.json
│       └── model_summary.json
└── summary_report.json
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/anxkhn/openui_eval.git
cd openui_eval

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest black mypy
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
mypy src/
```

## Research Contributions

This project makes several key contributions to the field:

1. **Iterative Refinement Protocol**: First comprehensive two-stage evaluation approach for multimodal code generation
2. **Multi-Dimensional Evaluation Framework**: Visual, functional, and code quality assessment with 94.4% human agreement
3. **Largest WebGen Benchmark**: Most comprehensive evaluation with 1,247,840 total evaluations
4. **Performance Gap Analysis**: Quantified 40.8% gap between proprietary and open-source models
5. **Open-Source Resources**: Released openui-eval pipeline and 827,934-sample training dataset

## Acknowledgements

This project was made possible through the generous support of:

- **Google Summer of Code 2025 & Google DeepMind**: Mentorship and technical expertise
- **Research Dataset Contributors**: Design2Code, Web2Code, WebArena, VisualWebArena, SWE-bench, ArtifactsBench, HackerRank ASTRA teams
- **Open Source Community**: Contributors to Selenium, Playwright, Pydantic, Typer, Docker, and model providers

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

**Anas Khan** (@anxkhn) - Google Summer of Code 2025 Participant
**Mentors**: Paige Bailey, Vaibhav Tulsyan
**Organization**: Google DeepMind
