#!/usr/bin/env python3
"""
Multimodal LLM Benchmark System - Main CLI Interface
A comprehensive benchmarking system for evaluating multimodal LLMs on HTML generation tasks
with iterative improvement and structured evaluation.
"""
import argparse
import sys
from pathlib import Path
from typing import List, Optional

from src.core.config import Config
from src.core.logger import setup_logger
from src.pipeline.benchmark_pipeline import BenchmarkPipeline


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Multimodal LLM Benchmark System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default configuration
  python main.py
  # Run specific models and tasks
  python main.py --models gemma3n:e2b gemma3:4b qwen2.5vl:7b --tasks calculator portfolio
  # Run with custom iterations and judges
  python main.py --iterations 5 --judges gemma3n:e2b gemma3:4b llama3.2-vision:11b
  # Resume from a specific checkpoint
  python main.py --resume-from results/benchmark_20241201_143022
  # Run in evaluation-only mode
  python main.py --mode evaluation --resume-from results/benchmark_20241201_143022
  # Use custom configuration file
  python main.py --config custom_config.yaml
        """,
    )
    # Model configuration
    parser.add_argument(
        "--models",
        nargs="+",
        help="List of models to benchmark (default: all supported models)",
    )
    # Task configuration
    parser.add_argument(
        "--tasks",
        nargs="+",
        help="List of tasks to run (default: all predefined tasks)",
    )
    # Generation configuration
    parser.add_argument(
        "--iterations",
        type=int,
        default=3,
        help="Number of iterative improvement iterations (default: 3)",
    )
    # Evaluation configuration
    parser.add_argument(
        "--judges",
        nargs="+",
        help="List of models to use as judges (default: all models)",
    )
    # Execution mode
    parser.add_argument(
        "--mode",
        choices=["full", "generation", "evaluation"],
        default="full",
        help="Execution mode: full (generation + evaluation), generation only, or evaluation only",
    )
    # Resume functionality
    parser.add_argument(
        "--resume-from",
        type=str,
        help="Resume from a previous benchmark run (provide results directory path)",
    )
    # Configuration file
    parser.add_argument(
        "--config", type=str, help="Path to configuration file (YAML or JSON)"
    )
    # Output directory
    parser.add_argument(
        "--output-dir",
        type=str,
        default="results",
        help="Output directory for results (default: results)",
    )
    # Logging level
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)",
    )
    # Parallel execution
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Enable parallel task execution where possible",
    )
    # Dry run mode
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run without actually executing tasks",
    )
    return parser.parse_args()


def create_config_from_args(args: argparse.Namespace) -> Config:
    """Create benchmark configuration from command line arguments."""
    # Load base configuration from file if provided
    if args.config:
        config = Config.from_yaml(args.config)
    else:
        config = Config()
    # Store the original judges list before potentially overriding models
    original_judges = config.judges[:]
    # Override with command line arguments
    if args.models:
        from src.core.config import ModelConfig

        config.models = [ModelConfig(name=model) for model in args.models]
    if args.tasks:
        # Filter existing tasks or create new ones
        from src.core.config import TaskConfig
        from src.tasks.task_definitions import get_task_by_name

        filtered_tasks = []
        for task_name in args.tasks:
            task_def = get_task_by_name(task_name)
            if task_def:
                filtered_tasks.append(
                    TaskConfig(
                        name=task_def.name,
                        description=task_def.description,
                        prompt_template=task_def.prompt,
                    )
                )
        if filtered_tasks:
            config.tasks = filtered_tasks
    if args.iterations:
        config.iterations = args.iterations
    # If judges are explicitly specified via CLI, use those
    # Otherwise, preserve the original judges setting (which may be "all" meaning all available models)
    if args.judges:
        config.judges = args.judges
    else:
        # Keep the original judges list - this allows "all" to work with all available models,
        # not just the models specified for generation
        config.judges = original_judges
    if args.output_dir:
        config.output_dir = args.output_dir
    # Set resume configuration
    if args.resume_from:
        config.resume_from = args.resume_from
    # Set execution mode (map CLI values to config values)
    mode_mapping = {
        "full": "full-pipeline",
        "generation": "generation-only",
        "evaluation": "judging-only",
    }
    config.mode = mode_mapping.get(args.mode, args.mode)
    return config


def main():
    """Main entry point for the benchmark system."""
    logger = None
    try:
        # Parse command line arguments
        args = parse_arguments()
        # Create configuration
        config = create_config_from_args(args)
        # Initialize logger
        logger = setup_logger(__name__, level=args.log_level)
        logger.info("Starting Multimodal LLM Benchmark System")
        logger.info(f"Configuration: {config.to_dict()}")
        # Validate configuration
        config.validate()
        # Create and run benchmark pipeline
        pipeline = BenchmarkPipeline(config)
        if args.dry_run:
            logger.info("Dry run mode - validating configuration and setup")
            # pipeline.validate_setup()  # TODO: Implement validate_setup method
            logger.info("Dry run completed successfully")
            return
        # Execute the benchmark
        if config.mode == "generation-only":
            results = pipeline.run_generation_phase()
        elif config.mode == "judging-only":
            results = pipeline.run_evaluation_phase()
        else:  # full-pipeline
            results = pipeline.run_full_pipeline()
        logger.info("Benchmark completed successfully")
        logger.info(f"Results saved to: {config.output_dir}")
        # Print summary
        print("\n" + "=" * 80)
        print("BENCHMARK SUMMARY")
        print("=" * 80)
        print(f"Total models tested: {len(config.models)}")
        print(f"Total tasks completed: {len(config.tasks)}")
        print(f"Execution mode: {config.mode}")
        print(f"Iterations per task: {config.iterations}")
        print(f"Results directory: {config.output_dir}")
        print("=" * 80)
    except KeyboardInterrupt:
        if logger:
            logger.warning("Benchmark interrupted by user")
        else:
            print("Benchmark interrupted by user")
        sys.exit(1)
    except RuntimeError as e:
        if logger:
            logger.error(f"Benchmark error: {e}")
        else:
            print(f"Benchmark error: {e}")
        sys.exit(1)
    except Exception as e:
        if logger:
            logger.error(f"Unexpected error: {e}", exc_info=True)
        else:
            print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
