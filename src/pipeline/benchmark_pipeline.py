"""Main benchmark pipeline that orchestrates the entire evaluation process."""

import json
import platform
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil
from tqdm import tqdm

from ..core.config import Config
from ..core.exceptions import BenchmarkError
from ..core.logger import get_logger, setup_logger
from ..evaluation.evaluation_schemas import (
    BenchmarkSummary,
    ModelRanking,
    TaskDifficultyRanking,
)
from ..evaluation.judge import Judge
from ..generation.html_generator import HTMLGenerator
from ..models.model_manager import ModelManager
from ..rendering.renderer import WebRenderer


class BenchmarkPipeline:
    """Main pipeline for running multimodal LLM benchmarks."""

    def __init__(self, config: Config):
        self.config = config
        self.logger = setup_logger(
            name="benchmark_pipeline",
            log_dir="logs",
            level=config.log_level,
            enable_compression=config.compress_logs,
        )
        # Initialize components
        self.model_manager = None
        self.html_generator = None
        self.renderer = None
        self.judge = None
        # Results storage
        self.results = {
            "generation_results": {},  # model -> task -> iterations
            "evaluation_results": {},  # model -> task -> evaluations
            "task_summaries": {},  # model -> task -> summary
            "benchmark_summary": None,
        }
        # Progress tracking
        self.total_operations = 0
        self.completed_operations = 0
        self.logger.info("BenchmarkPipeline initialized")

    def _setup_components(self):
        """Initialize all pipeline components."""
        try:
            self.logger.info("Setting up pipeline components...")
            # Setup model manager
            self.model_manager = ModelManager(
                models=self.config.models,
                memory_threshold=self.config.memory_threshold,
                max_concurrent_models=self.config.max_concurrent_models,
            )
            # Setup HTML generator
            self.html_generator = HTMLGenerator(
                model_manager=self.model_manager, output_dir=self.config.output_dir
            )
            # Setup renderer
            self.renderer = WebRenderer(self.config.rendering)
            # Setup judge
            self.judge = Judge(
                model_manager=self.model_manager,
                config=self.config.evaluation,
                output_dir=self.config.output_dir,
            )
            self.logger.info("All components setup successfully")
        except Exception as e:
            error_msg = f"Failed to setup pipeline components: {e}"
            self.logger.error(error_msg)
            raise BenchmarkError(error_msg)

    def _log_system_info(self):
        """Log system information for reproducibility."""
        try:
            system_info = {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": psutil.virtual_memory().total / (1024**3),
                "timestamp": datetime.now().isoformat(),
                "config": self.config.to_dict(),
            }
            self.logger.log_system_info(system_info)
            # Save system info to file
            system_info_path = Path(self.config.output_dir) / "system_info.json"
            with open(system_info_path, "w") as f:
                json.dump(system_info, f, indent=2, default=str)
        except Exception as e:
            self.logger.warning(f"Failed to log system info: {e}")

    def _determine_judge_models(self) -> List[str]:
        """Determine which models to use as judges."""
        if "all" in self.config.judges:
            # Use all available judge models from evaluation config
            return self.config.evaluation.judge_models
        else:
            return self.config.judges

    def _calculate_total_operations(self):
        """Calculate total number of operations for progress tracking."""
        if self.config.mode == "generation-only":
            # Model x Task x Iterations
            self.total_operations = (
                len(self.config.models)
                * len(self.config.tasks)
                * self.config.iterations
            )
        elif self.config.mode == "judging-only":
            # Assume existing results, count evaluations
            # This would need to be calculated based on existing files
            self.total_operations = 100  # Placeholder
        else:  # full-pipeline
            # Generation + Evaluation
            generation_ops = (
                len(self.config.models)
                * len(self.config.tasks)
                * self.config.iterations
            )
            # Determine judge models using the new method
            judge_models = self._determine_judge_models()
            evaluation_ops = (
                len(self.config.models)
                * len(self.config.tasks)
                * self.config.iterations
                * len(judge_models)
            )
            self.total_operations = generation_ops + evaluation_ops
        self.logger.info(f"Total operations to perform: {self.total_operations}")

    def _update_progress(self, operation_name: str):
        """Update progress tracking."""
        self.completed_operations += 1
        progress = (self.completed_operations / self.total_operations) * 100
        self.logger.log_pipeline_progress(
            stage=operation_name,
            progress=progress,
            completed=self.completed_operations,
            total=self.total_operations,
        )

    def run_generation_phase(self) -> Dict[str, Any]:
        """Run the HTML generation phase."""
        try:
            self.logger.info("Starting generation phase...")
            generation_results = {}
            with tqdm(
                total=len(self.config.models) * len(self.config.tasks),
                desc="Generating HTML",
            ) as pbar:
                for model_config in self.config.models:
                    model_name = model_config.name
                    generation_results[model_name] = {}
                    self.logger.info(f"Starting generation with model: {model_name}")
                    for task in self.config.tasks:
                        task_name = task.name
                        try:
                            self.logger.info(f"Generating HTML for task: {task_name}")
                            # Generate HTML with iterations
                            task_results = self.html_generator.generate_complete_task(
                                model_name=model_name,
                                task=task,
                                iterations=self.config.iterations,
                                renderer=self.renderer,
                            )
                            generation_results[model_name][task_name] = task_results
                            # Update progress for each iteration
                            for _ in range(self.config.iterations):
                                self._update_progress(
                                    f"generate_{model_name}_{task_name}"
                                )
                            self.logger.info(
                                f"Completed generation for {model_name} on {task_name}"
                            )
                        except Exception as e:
                            self.logger.error(
                                f"Failed generation for {model_name} on {task_name}: {e}"
                            )
                            generation_results[model_name][task_name] = []
                            # Still update progress to maintain count
                            for _ in range(self.config.iterations):
                                self._update_progress(
                                    f"generate_{model_name}_{task_name}_failed"
                                )
                        pbar.update(1)
            self.results["generation_results"] = generation_results
            self.logger.info("Generation phase completed")
            return generation_results
        except Exception as e:
            error_msg = f"Generation phase failed: {e}"
            self.logger.error(error_msg)
            raise BenchmarkError(error_msg)

    def run_evaluation_phase(
        self, generation_results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run the evaluation phase."""
        try:
            self.logger.info("Starting evaluation phase...")
            if generation_results is None:
                generation_results = self.results.get("generation_results", {})
            if not generation_results:
                raise BenchmarkError("No generation results available for evaluation")
            # Determine judge models using the new method
            judge_models = self._determine_judge_models()
            self.logger.info(f"Using judge models: {judge_models}")
            evaluation_results = {}
            task_summaries = {}
            total_evaluations = sum(
                len(tasks) for tasks in generation_results.values()
            ) * len(judge_models)
            with tqdm(total=total_evaluations, desc="Evaluating HTML") as pbar:
                for model_name, model_tasks in generation_results.items():
                    evaluation_results[model_name] = {}
                    task_summaries[model_name] = {}
                    for task_name, task_results in model_tasks.items():
                        if not task_results:
                            self.logger.warning(
                                f"No results to evaluate for {model_name} on {task_name}"
                            )
                            continue
                        try:
                            # Find task config
                            task_config = next(
                                (
                                    task
                                    for task in self.config.tasks
                                    if task.name == task_name
                                ),
                                None,
                            )
                            if not task_config:
                                self.logger.error(
                                    f"Task config not found for {task_name}"
                                )
                                continue
                            self.logger.info(f"Evaluating {model_name} on {task_name}")
                            # Run evaluations with all judges
                            evaluations = self.judge.evaluate_all_iterations(
                                judge_models=judge_models,
                                target_model=model_name,
                                task_name=task_name,
                                generation_results=task_results,
                            )
                            evaluation_results[model_name][task_name] = evaluations
                            # Create task summary
                            summary = self.judge.create_task_summary(
                                target_model=model_name,
                                task_name=task_name,
                                evaluations=evaluations,
                            )
                            task_summaries[model_name][task_name] = summary
                            # Update progress
                            for _ in judge_models:
                                for _ in task_results:
                                    self._update_progress(
                                        f"evaluate_{model_name}_{task_name}"
                                    )
                            self.logger.info(
                                f"Completed evaluation for {model_name} on {task_name}"
                            )
                        except Exception as e:
                            self.logger.error(
                                f"Failed evaluation for {model_name} on {task_name}: {e}"
                            )
                            evaluation_results[model_name][task_name] = []
                            task_summaries[model_name][task_name] = None
                            # Still update progress
                            for _ in judge_models:
                                for _ in task_results:
                                    self._update_progress(
                                        f"evaluate_{model_name}_{task_name}_failed"
                                    )
                        pbar.update(1)
            self.results["evaluation_results"] = evaluation_results
            self.results["task_summaries"] = task_summaries
            self.logger.info("Evaluation phase completed")
            return evaluation_results
        except Exception as e:
            error_msg = f"Evaluation phase failed: {e}"
            self.logger.error(error_msg)
            raise BenchmarkError(error_msg)

    def create_benchmark_summary(self) -> BenchmarkSummary:
        """Create comprehensive benchmark summary."""
        try:
            self.logger.info("Creating benchmark summary...")
            task_summaries = self.results.get("task_summaries", {})
            if not task_summaries:
                raise BenchmarkError(
                    "No task summaries available for benchmark summary"
                )
            # Calculate model rankings and scores
            model_scores = {}
            model_strengths = {}
            model_weaknesses = {}
            for model_name, model_tasks in task_summaries.items():
                scores = []
                strengths = []
                weaknesses = []
                for task_name, summary in model_tasks.items():
                    if summary:
                        scores.append(summary.final_overall_score)
                        strengths.extend(summary.key_strengths)
                        weaknesses.extend(summary.key_weaknesses)
                if scores:
                    model_scores[model_name] = sum(scores) / len(scores)
                    # Get most common strengths and weaknesses
                    strength_counts = {}
                    weakness_counts = {}
                    for strength in strengths:
                        strength_counts[strength] = strength_counts.get(strength, 0) + 1
                    for weakness in weaknesses:
                        weakness_counts[weakness] = weakness_counts.get(weakness, 0) + 1
                    model_strengths[model_name] = sorted(
                        strength_counts.keys(),
                        key=lambda x: strength_counts[x],
                        reverse=True,
                    )[:5]
                    model_weaknesses[model_name] = sorted(
                        weakness_counts.keys(),
                        key=lambda x: weakness_counts[x],
                        reverse=True,
                    )[:5]
                else:
                    model_scores[model_name] = 0
                    model_strengths[model_name] = []
                    model_weaknesses[model_name] = []
            # Create model rankings
            model_rankings = [
                ModelRanking(model=model, score=score)
                for model, score in sorted(
                    model_scores.items(), key=lambda x: x[1], reverse=True
                )
            ]
            # Calculate task difficulty
            task_scores = {}
            for model_name, model_tasks in task_summaries.items():
                for task_name, summary in model_tasks.items():
                    if summary:
                        if task_name not in task_scores:
                            task_scores[task_name] = []
                        task_scores[task_name].append(summary.final_overall_score)
            task_difficulty_ranking = [
                TaskDifficultyRanking(
                    task=task, average_score=sum(scores) / len(scores)
                )
                for task, scores in task_scores.items()
                if scores
            ]
            task_difficulty_ranking.sort(key=lambda x: x.average_score)
            # Calculate improvement metrics
            average_improvement_by_model = {}
            for model_name, model_tasks in task_summaries.items():
                improvements = []
                for task_name, summary in model_tasks.items():
                    if summary:
                        improvements.append(summary.overall_improvement)
                if improvements:
                    average_improvement_by_model[model_name] = sum(improvements) / len(
                        improvements
                    )
                else:
                    average_improvement_by_model[model_name] = 0
            # Create benchmark summary
            summary = BenchmarkSummary(
                benchmark_timestamp=datetime.now().isoformat(),
                total_models=len(self.config.models),
                total_tasks=len(self.config.tasks),
                total_iterations_per_task=self.config.iterations,
                model_rankings=model_rankings,
                model_scores=model_scores,
                model_strengths=model_strengths,
                model_weaknesses=model_weaknesses,
                task_difficulty_ranking=task_difficulty_ranking,
                task_performance={},  # Would need more detailed calculation
                criteria_performance={},  # Would need more detailed calculation
                most_challenging_criteria=[],  # Would need analysis
                best_performing_criteria=[],  # Would need analysis
                models_with_best_improvement=sorted(
                    average_improvement_by_model.keys(),
                    key=lambda x: average_improvement_by_model[x],
                    reverse=True,
                )[:3],
                average_improvement_by_model=average_improvement_by_model,
                score_variance_by_model={},  # Would need calculation
                judge_reliability_scores={},  # Would need calculation
                top_performing_models=[r.model for r in model_rankings[:3]],
                most_improved_models=sorted(
                    average_improvement_by_model.keys(),
                    key=lambda x: average_improvement_by_model[x],
                    reverse=True,
                )[:3],
                recommended_model_for_tasks={},  # Would need task-specific analysis
            )
            # Save benchmark summary
            summary_path = Path(self.config.output_dir) / "benchmark_summary.json"
            with open(summary_path, "w") as f:
                json.dump(summary.model_dump(), f, indent=2, default=str)
            self.results["benchmark_summary"] = summary
            self.logger.info(f"Benchmark summary saved to {summary_path}")
            return summary
        except Exception as e:
            error_msg = f"Failed to create benchmark summary: {e}"
            self.logger.error(error_msg)
            raise BenchmarkError(error_msg)

    def run_full_pipeline(self) -> Dict[str, Any]:
        """Run the complete benchmark pipeline."""
        try:
            start_time = time.time()
            self.logger.info("Starting full benchmark pipeline...")
            # Setup
            self._setup_components()
            self._log_system_info()
            self._calculate_total_operations()
            # Run phases based on mode
            if self.config.mode == "generation-only":
                generation_results = self.run_generation_phase()
            elif self.config.mode == "judging-only":
                # Load existing generation results
                # This would need implementation to load from saved files
                generation_results = {}
                evaluation_results = self.run_evaluation_phase(generation_results)
            else:  # full-pipeline
                generation_results = self.run_generation_phase()
                evaluation_results = self.run_evaluation_phase(generation_results)
                benchmark_summary = self.create_benchmark_summary()
            # Cleanup
            if self.model_manager:
                self.model_manager.cleanup()
            if self.renderer:
                self.renderer.cleanup()
            total_duration = time.time() - start_time
            # Save final results
            final_results = {
                "config": self.config.to_dict(),
                "results": self.results,
                "total_duration": total_duration,
                "completed_operations": self.completed_operations,
                "total_operations": self.total_operations,
                "timestamp": datetime.now().isoformat(),
            }
            results_path = Path(self.config.output_dir) / "final_results.json"
            with open(results_path, "w") as f:
                json.dump(final_results, f, indent=2, default=str)
            # Save summary report
            self.logger.save_summary_report(
                str(Path(self.config.output_dir) / "summary_report.json")
            )
            self.logger.info(
                f"Benchmark pipeline completed in {total_duration:.2f} seconds"
            )
            return final_results
        except Exception as e:
            error_msg = f"Benchmark pipeline failed: {e}"
            self.logger.error(error_msg)
            raise BenchmarkError(error_msg)
        finally:
            # Ensure cleanup
            try:
                if self.model_manager:
                    self.model_manager.cleanup()
                if self.renderer:
                    self.renderer.cleanup()
            except Exception as e:
                self.logger.warning(f"Error during cleanup: {e}")

    def resume_from_checkpoint(self, checkpoint_path: str):
        """Resume benchmark from a checkpoint."""
        # This would need implementation based on saved state
        self.logger.info(f"Resuming from checkpoint: {checkpoint_path}")
        # Implementation would load saved state and continue from where it left off
        pass
