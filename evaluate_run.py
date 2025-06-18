#!/usr/bin/env python3
"""
Evaluation script for specific benchmark runs.
This script allows you to evaluate a specific benchmark run by providing
its timestamp (e.g., 20250611_024703).
"""
import argparse
import sys
from pathlib import Path
from typing import List, Optional

from src.core.config import Config
from src.core.exceptions import BenchmarkError
from src.core.logger import setup_logger
from src.evaluation.judge import Judge
from src.models.model_manager import ModelManager


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Evaluate a specific benchmark run",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Evaluate a specific run
  python evaluate_run.py 20250611_024703
  # Evaluate with specific judges
  python evaluate_run.py 20250611_024703 --judges gemma3:4b qwen2.5vl:7b
  # Evaluate specific models/tasks from a run
  python evaluate_run.py 20250611_024703 --models gemma3:4b --tasks basic_calculator
        """,
    )
    parser.add_argument(
        "run_timestamp",
        type=str,
        help="Timestamp of the benchmark run to evaluate (e.g., 20250611_024703)",
    )
    parser.add_argument(
        "--judges",
        nargs="+",
        help="List of models to use as judges (default: all available models)",
    )
    parser.add_argument(
        "--models",
        nargs="+",
        help="Specific models to evaluate from the run (default: all models in run)",
    )
    parser.add_argument(
        "--tasks",
        nargs="+",
        help="Specific tasks to evaluate from the run (default: all tasks in run)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="results",
        help="Output directory for results (default: results)",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)",
    )
    return parser.parse_args()


def discover_run_contents(run_path: Path) -> dict:
    """Discover models and tasks in a benchmark run."""
    run_contents = {
        "models": [],
        "tasks": {},  # model -> [tasks]
        "generations": {},  # model -> task -> [iterations]
    }
    if not run_path.exists():
        raise BenchmarkError(f"Run directory not found: {run_path}")
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


def load_generation_results(
    run_path: Path, model: str, task: str, iterations: List[int]
) -> List[dict]:
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


def main():
    """Main entry point for the evaluation script."""
    logger = None
    try:
        # Parse command line arguments
        args = parse_arguments()
        # Initialize logger
        logger = setup_logger(__name__, level=args.log_level)
        logger.info(f"Evaluating benchmark run: {args.run_timestamp}")
        # Construct run path
        run_path = Path(args.output_dir) / args.run_timestamp
        # Discover run contents
        run_contents = discover_run_contents(run_path)
        if not run_contents["models"]:
            raise BenchmarkError(f"No models found in run: {args.run_timestamp}")
        logger.info(f"Found models: {run_contents['models']}")
        # Filter models if specified
        models_to_evaluate = args.models if args.models else run_contents["models"]
        models_to_evaluate = [
            m for m in models_to_evaluate if m in run_contents["models"]
        ]
        if not models_to_evaluate:
            raise BenchmarkError(f"No valid models found to evaluate")
        # Set up judges
        judge_models = args.judges if args.judges else run_contents["models"]
        # Create basic config for evaluation
        config = Config()
        config.output_dir = args.output_dir
        config.log_level = args.log_level
        # Initialize components
        model_manager = ModelManager(config)
        judge = Judge(model_manager, config.evaluation, config.output_dir)
        logger.info(f"Using judges: {judge_models}")
        # Evaluate each model and task
        for model in models_to_evaluate:
            model_tasks = run_contents["tasks"].get(model, [])
            # Filter tasks if specified
            if args.tasks:
                model_tasks = [t for t in model_tasks if t in args.tasks]
            if not model_tasks:
                logger.warning(f"No tasks found for model {model}")
                continue
            logger.info(f"Evaluating model: {model}")
            for task in model_tasks:
                logger.info(f"  Evaluating task: {task}")
                # Get iterations for this task
                iterations = run_contents["generations"][model][task]
                if not iterations:
                    logger.warning(f"    No iterations found for {task}")
                    continue
                # Load generation results
                generation_results = load_generation_results(
                    run_path, model, task, iterations
                )
                if not generation_results:
                    logger.warning(f"    No generation results found for {task}")
                    continue
                logger.info(f"    Found {len(generation_results)} iterations")
                # Run evaluation
                try:
                    # Use the Judge's evaluate_all_iterations method with timestamp folder saving
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
                        logger.info(f"      Saved: evaluation_summary.json")
                    logger.info(
                        f"    Completed evaluation: {len(evaluations)} evaluations"
                    )
                except Exception as e:
                    logger.error(f"    Failed to evaluate {task}: {e}")
                    continue
        # Cleanup
        model_manager.cleanup()
        logger.info("Evaluation completed successfully")
        logger.info(f"Results saved to: {args.output_dir}/evaluations/")
    except KeyboardInterrupt:
        if logger:
            logger.warning("Evaluation interrupted by user")
        else:
            print("Evaluation interrupted by user")
        sys.exit(1)
    except BenchmarkError as e:
        if logger:
            logger.error(f"Evaluation error: {e}")
        else:
            print(f"Evaluation error: {e}")
        sys.exit(1)
    except Exception as e:
        if logger:
            logger.error(f"Unexpected error: {e}", exc_info=True)
        else:
            print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
