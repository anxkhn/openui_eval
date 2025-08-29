#!/usr/bin/env python3
"""
OpenUI Eval CLI - Command Line Interface for the Multimodal LLM Benchmark System
"""

import os
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich import print as rprint

from core.config import Config
from core.logger import setup_logger
from pipeline.benchmark_pipeline import BenchmarkPipeline

app = typer.Typer(
    name="openui-eval",
    help="OpenUI Eval: Multimodal LLM Benchmark System",
    add_completion=False,
)

console = Console()


@app.command()
def init():
    """
    Initialize OpenUI Eval with default configuration files.

    Creates config.yaml and .env files in the current directory if they don't exist.
    """
    rprint("[bold blue]Initializing OpenUI Eval...[/bold blue]")

    # Check and create config.yaml
    config_path = Path("config.yaml")
    if not config_path.exists():
        default_config = """# OpenUI Eval: Default Configuration
provider:
  provider_type: "ollama"  # (ollama, openrouter, gemini)
  ollama_host: "http://localhost:11434"
  openrouter_api_key: null # Set in .env
  gemini_api_key: null     # Set in .env

models:
  - "gemma3n:e4b" # Example Ollama model

tasks:
  task_names:
    - "basic_calculator"
    - "personal_portfolio"

generation:
  max_iterations: 3

evaluation:
  judge_models:
    - "gemma3n:e4b" # Use a small model as a default judge

output_dir: "results"
logging:
  level: "INFO"
"""
        config_path.write_text(default_config)
        rprint("Created default [green]config.yaml[/green]")
    else:
        rprint("[yellow]config.yaml[/yellow] already exists")

    # Check and create .env
    env_path = Path(".env")
    if not env_path.exists():
        default_env = """OPENROUTER_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
"""
        env_path.write_text(default_env)
        rprint("Created default [green].env[/green]")
    else:
        rprint("[yellow].env[/yellow] already exists")

    rprint("[bold green]Initialization complete![/bold green]")
    rprint("\nNext steps:")
    rprint("1. Edit [cyan].env[/cyan] to add your API keys")
    rprint("2. Edit [cyan]config.yaml[/cyan] to configure models and tasks")
    rprint("3. Run: [cyan]openui-eval start[/cyan]")


def check_provider_availability(config: Config) -> bool:
    """Check if the configured provider is available."""
    from models.provider_factory import create_provider
    from models.base_provider import LLMProvider

    try:
        provider_type = config.provider.provider_type
        rprint(f"Checking {provider_type} provider availability...")

        provider_config = {
            "gemini_api_key": getattr(config.provider, "gemini_api_key", None),
            "provider_type": config.provider.provider_type,
            "timeout": 60,  # Increase timeout to 60 seconds
        }
        provider: LLMProvider = create_provider(provider_type, provider_config)

        if not provider.is_available():
            rprint(f"Cannot connect to {provider_type} provider")
            if provider_type == "ollama":
                rprint(f"   Is Ollama running at {config.provider.ollama_host}?")
            elif provider_type == "openrouter":
                rprint("   Check your OPENROUTER_API_KEY in .env")
            elif provider_type == "gemini":
                rprint("   Check your GEMINI_API_KEY in .env")
                if hasattr(provider, "_last_error") and provider._last_error:
                    rprint(f"   Detailed error: {provider._last_error}")
            return False

        rprint(f"{provider_type.title()} provider is available")

        # Check model availability
        available_models = provider.list_models()
        requested_models = [model.name for model in config.models]

        missing_models = []
        for model_name in requested_models:
            if model_name not in available_models:
                missing_models.append(model_name)

        if missing_models:
            rprint("[yellow]Warning:[/yellow] Some models not found:")
            for model in missing_models:
                rprint(f"   • {model}")
            rprint("   Please pull these models first or update config.yaml")
        else:
            rprint("All requested models are available")

        return True

    except Exception as e:
        rprint(f"Error checking provider availability: {e}")
        return False


@app.command()
def start(
    config: Optional[str] = typer.Option(
        "config.yaml", "--config", "-c", help="Path to configuration file"
    )
):
    """
    Start the OpenUI Eval benchmark pipeline.

    Loads configuration from config.yaml and runs the full benchmark.
    """
    rprint("[bold blue]Starting OpenUI Eval...[/bold blue]")

    # Validate config file exists
    config_path = Path(config)
    if not config_path.exists():
        rprint(f"Configuration file [red]{config}[/red] not found")
        rprint("Run [cyan]openui-eval init[/cyan] to create default configuration")
        raise typer.Exit(1)

    try:
        # Load configuration
        rprint(f"Loading configuration from {config}...")
        app_config = Config.from_yaml(config_path)

        # Apply environment overrides
        app_config.apply_env_overrides()

        # Setup logging
        logger = setup_logger(__name__, level=app_config.log_level, log_dir="logs")
        logger.info("Starting OpenUI Eval CLI")

        # Pre-flight checks
        rprint("Performing pre-flight checks...")
        if not check_provider_availability(app_config):
            rprint("Pre-flight checks failed")
            raise typer.Exit(1)

        rprint("All pre-flight checks passed")

        # Initialize and run pipeline
        rprint("Initializing benchmark pipeline...")
        pipeline = BenchmarkPipeline(app_config)

        rprint("Running benchmark pipeline...")
        results = pipeline.run_full_pipeline()

        rprint("[bold green]Benchmark completed successfully![/bold green]")
        rprint(f"Results saved to: [cyan]{app_config.output_dir}[/cyan]")

    except KeyboardInterrupt:
        rprint("\n[red]Benchmark interrupted by user[/red]")
        raise typer.Exit(1)

    except Exception as e:
        rprint(f"[red]Error running benchmark: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def evaluate(
    run_timestamp: str = typer.Argument(
        ..., help="Run timestamp (e.g., 20250821_182200)"
    ),
    judges: Optional[str] = typer.Option(
        None,
        "--judges",
        "-j",
        help="Comma-separated list of judge models (default: all available models)",
    ),
    models: Optional[str] = typer.Option(
        None,
        "--models",
        "-m",
        help="Comma-separated list of models to evaluate (default: all models in run)",
    ),
    tasks: Optional[str] = typer.Option(
        None,
        "--tasks",
        "-t",
        help="Comma-separated list of tasks to evaluate (default: all tasks in run)",
    ),
    config: Optional[str] = typer.Option(
        "config.yaml", "--config", "-c", help="Path to configuration file"
    ),
):
    """
    Evaluate an existing benchmark run.

    Evaluates results from a previous benchmark run using the configured judge models.
    """
    rprint(f"[bold blue]Evaluating benchmark run: {run_timestamp}[/bold blue]")

    # Parse comma-separated options
    judge_models = None
    if judges:
        judge_models = [j.strip() for j in judges.split(",")]

    models_to_evaluate = None
    if models:
        models_to_evaluate = [m.strip() for m in models.split(",")]

    tasks_to_evaluate = None
    if tasks:
        tasks_to_evaluate = [t.strip() for t in tasks.split(",")]

    try:
        # Validate config file exists
        config_path = Path(config)
        if not config_path.exists():
            rprint(f"Configuration file [red]{config}[/red] not found")
            rprint("Run [cyan]openui-eval init[/cyan] to create default configuration")
            raise typer.Exit(1)

        # Load configuration
        rprint(f"Loading configuration from {config}...")
        app_config = Config.from_yaml(config_path)
        app_config.apply_env_overrides()

        # Setup logging
        logger = setup_logger(__name__, level=app_config.log_level, log_dir="logs")
        logger.info(f"Evaluating benchmark run: {run_timestamp}")

        # Construct run path
        run_path = Path(app_config.output_dir) / run_timestamp

        if not run_path.exists():
            rprint(f"Run directory not found: [red]{run_path}[/red]")
            raise typer.Exit(1)

        # Discover run contents
        run_contents = _discover_run_contents(run_path)
        if not run_contents["models"]:
            rprint(f"No models found in run: {run_timestamp}")
            raise typer.Exit(1)

        rprint(f"Found models: {', '.join(run_contents['models'])}")

        # Filter models if specified
        models_to_evaluate = models_to_evaluate or run_contents["models"]
        models_to_evaluate = [
            m for m in models_to_evaluate if m in run_contents["models"]
        ]

        if not models_to_evaluate:
            rprint("No valid models found to evaluate")
            raise typer.Exit(1)

        # Set up judges
        judge_models = judge_models or run_contents["models"]

        # Initialize components
        from models.model_manager import ModelManager
        from evaluation.judge import Judge

        model_manager = ModelManager(config=app_config)
        judge = Judge(model_manager, app_config.evaluation, app_config.output_dir)

        rprint(f"Using judges: {', '.join(judge_models)}")

        # Evaluate each model and task
        for model in models_to_evaluate:
            model_tasks = run_contents["tasks"].get(model, [])
            # Filter tasks if specified
            if tasks_to_evaluate:
                model_tasks = [t for t in model_tasks if t in tasks_to_evaluate]

            if not model_tasks:
                rprint(f"No tasks found for model {model}")
                continue

            rprint(f"Evaluating model: {model}")
            for task in model_tasks:
                rprint(f"  Evaluating task: {task}")
                # Get iterations for this task
                iterations = run_contents["generations"][model][task]
                if not iterations:
                    rprint(f"    No iterations found for {task}")
                    continue

                # Load generation results
                generation_results = _load_generation_results(
                    run_path, model, task, iterations
                )

                if not generation_results:
                    rprint(f"    No generation results found for {task}")
                    continue

                rprint(f"    Found {len(generation_results)} iterations")

                # Run evaluation
                try:
                    evaluations = judge.evaluate_all_iterations(
                        judge_models=judge_models,
                        target_model=model,
                        task_name=task,
                        generation_results=generation_results,
                        save_to_timestamp_folder=str(run_path),
                    )

                    # Create task summary and save it in the timestamp folder
                    if evaluations:
                        task_path = run_path / model / task
                        summary = judge.create_task_summary(model, task, evaluations)
                        summary_path = task_path / "evaluation_summary.json"

                        import json

                        with open(summary_path, "w") as f:
                            json.dump(summary.model_dump(), f, indent=2, default=str)
                        rprint(f"      Saved: evaluation_summary.json")

                    rprint(f"    Completed evaluation: {len(evaluations)} evaluations")

                except Exception as e:
                    rprint(f"    Failed to evaluate {task}: {e}")
                    continue

        # Cleanup
        model_manager.cleanup()
        rprint("[bold green]Evaluation completed successfully![/bold green]")
        rprint(f"Results saved to: [cyan]{app_config.output_dir}/evaluations/[/cyan]")

    except KeyboardInterrupt:
        rprint("\n[red]Evaluation interrupted by user[/red]")
        raise typer.Exit(1)

    except Exception as e:
        rprint(f"[red]Error evaluating benchmark: {e}[/red]")
        raise typer.Exit(1)


def _discover_run_contents(run_path: Path) -> dict:
    """Discover models and tasks in a benchmark run."""
    run_contents = {
        "models": [],
        "tasks": {},  # model -> [tasks]
        "generations": {},  # model -> task -> [iterations]
    }

    if not run_path.exists():
        raise FileNotFoundError(f"Run directory not found: {run_path}")

    # Discover models
    for model_dir in run_path.iterdir():
        if model_dir.is_dir() and model_dir.name not in [".", ".."]:
            model_name = model_dir.name
            run_contents["models"].append(model_name)
            run_contents["tasks"][model_name] = []
            run_contents["generations"][model_name] = {}

            # Discover tasks for this model
            for task_dir in model_dir.iterdir():
                if task_dir.is_dir():
                    task_name = task_dir.name
                    run_contents["tasks"][model_name].append(task_name)

                    # Discover iterations for this task
                    iterations = []
                    for file in task_dir.iterdir():
                        if file.name.startswith("v") and file.name.endswith(".html"):
                            # Extract iteration number (v1.html -> 1)
                            iteration = int(file.name[1:].split(".")[0])
                            iterations.append(iteration)

                    run_contents["generations"][model_name][task_name] = sorted(
                        iterations
                    )

    return run_contents


def _load_generation_results(
    run_path: Path, model: str, task: str, iterations: list
) -> list:
    """Load generation results for evaluation."""
    results = []
    task_path = run_path / model / task

    for iteration in iterations:
        html_file = task_path / f"v{iteration}.html"
        screenshot_file = task_path / f"v{iteration}_screenshot.png"
        metadata_file = task_path / f"v{iteration}_metadata.json"

        if html_file.exists():
            with open(html_file, "r", encoding="utf-8") as f:
                html_content = f.read()

            result = {
                "iteration": iteration,
                "html_content": html_content,
                "html_path": str(html_file),
                "screenshot_path": (
                    str(screenshot_file) if screenshot_file.exists() else None
                ),
            }

            # Load metadata if available
            if metadata_file.exists():
                import json

                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
                result["metadata"] = metadata

            results.append(result)

    return results


if __name__ == "__main__":
    app()
