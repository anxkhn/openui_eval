# OpenUI Eval

## Installation & Setup

### Prerequisites

- **Python 3.11+**
- **Ollama** (for running LLM models)
- **Chrome/Chromium** (for web rendering)

### Quick Setup

1. **Clone the repository**:

   ```bash
   git clone https://github.com/anxkhn/openui_eval.git
   cd openui_eval
   ```

2. **Install dependencies in a virtual environment**:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # or
   .venv\Scripts\activate     # Windows
   pip install -r requirements.txt
   ```

   If you are using uv **(recommended)**:

      ```bash
      uv venv
      source .venv/bin/activate
      uv sync
      ```


3. **Install and start Ollama**:

   ```bash
   # Install Ollama from https://ollama.com/
   ollama serve
   ```

4. **Pull required models** (this may take time):
   ```bash
   ollama pull gemma3:4b
   ollama pull qwen2.5vl:7b
   ollama pull granite3.2-vision:2b
   ollama pull llama3.2-vision:11b
   ollama pull minicpm-v:8b
   ollama pull llava-phi3:3.8b
   ```

## Usage

### Basic Usage

Run a complete benchmark with default settings:

```bash
python main.py
```

### Advanced Usage

**Run specific models and tasks**:

```bash
python main.py --models gemma3:4b qwen2.5vl:7b --tasks basic_calculator personal_portfolio
```

**Customize iterations and judges**:

```bash
python main.py --iterations 5 --judges gemma3:4b llama3.2-vision:11b
```

**Resume from checkpoint**:

```bash
python main.py --resume-from results/benchmark_20241201_143022
```

**Run only evaluation on existing results**:

```bash
python main.py --mode evaluation --resume-from results/benchmark_20241201_143022
```

**Use custom configuration**:

```bash
python main.py --config custom_config.yaml
```

**Dry run to validate setup**:

```bash
python main.py --dry-run
```
