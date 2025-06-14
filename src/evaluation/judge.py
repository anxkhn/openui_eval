"""Judge system for evaluating generated HTML using structured output."""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.config import EvaluationConfig
from ..core.exceptions import EvaluationError
from ..core.logger import get_logger
from ..models.model_manager import ModelManager
from .evaluation_schemas import (CriteriaScore, EvaluationResult,
                                 TaskEvaluationSummary)


class Judge:
    """Evaluates generated HTML using multiple models as judges with structured output."""

    def __init__(
        self,
        model_manager: ModelManager,
        config: EvaluationConfig,
        output_dir: str = "results",
    ):
        self.model_manager = model_manager
        self.config = config
        self.output_dir = Path(output_dir)
        self.logger = get_logger()
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _create_evaluation_prompt(self, html_content: str) -> str:
        """Create evaluation prompt for judges (completely blind evaluation)."""
        prompt = f"""You are an expert frontend developer evaluating HTML code. Evaluate this implementation based on both the code structure and the visual output.
**HTML Code to Evaluate:**
```html
{html_content}
```
**Evaluation Criteria:**
Please evaluate based on the following criteria, providing scores from 0-10 (where 10 is excellent):
1. **Visual Appeal** (0-10): Assess the overall visual design, aesthetics, color scheme, typography, and visual hierarchy.
2. **Functionality** (0-10): Evaluate how well the code implements interactive features and apparent functional requirements.
3. **Responsiveness** (0-10): Assess how well the design adapts to different screen sizes and devices.
4. **Code Quality** (0-10): Evaluate the HTML structure, CSS organization, JavaScript implementation, and overall code cleanliness.
5. **Task Completion** (0-10): Based on what you can infer from the code and visual output, assess how complete and functional this implementation appears to be.
**Additional Analysis:**
- Identify key strengths and weaknesses
- Provide specific improvement suggestions
- Note any technical issues, accessibility concerns, or performance considerations
- Give an overall assessment and feedback"""
        return prompt

    def evaluate_html(
        self,
        judge_model: str,
        target_model: str,
        task_name: str,
        iteration: int,
        html_content: str,
        screenshot_path: Optional[str] = None,
    ) -> EvaluationResult:
        """
        Evaluate HTML content using a judge model (completely blind evaluation).
        Args:
            judge_model: Name of the model to use as judge
            target_model: Name of the model that generated the HTML
            task_name: Name of the task (for metadata only, not sent to judge)
            iteration: Current iteration number (for metadata only, not sent to judge)
            html_content: HTML content to evaluate
            screenshot_path: Optional path to screenshot
        Returns:
            Structured evaluation result
        """
        try:
            self.logger.log_evaluation_result(
                judge_model, task_name, iteration, {}, operation="start_evaluation"
            )
            # Create evaluation prompt (completely blind - only HTML code)
            prompt = self._create_evaluation_prompt(html_content)
            # Generate structured evaluation
            start_time = time.time()
            evaluation = self.model_manager.client.generate_structured(
                model_name=judge_model,
                prompt=prompt,
                response_model=EvaluationResult,
                image_path=screenshot_path,
                temperature=self.config.temperature,
            )
            duration = time.time() - start_time
            # Ensure metadata is correct
            evaluation.judge_model = judge_model
            evaluation.target_model = target_model
            evaluation.task_name = task_name
            evaluation.iteration = iteration
            # Calculate overall score from criteria if not provided
            if (
                not hasattr(evaluation, "overall_score")
                or evaluation.overall_score == 0
            ):
                criteria_scores = [
                    evaluation.visual_appeal.score,
                    evaluation.functionality.score,
                    evaluation.responsiveness.score,
                    evaluation.code_quality.score,
                    evaluation.task_completion.score,
                ]
                evaluation.overall_score = sum(
                    criteria_scores) / len(criteria_scores)
            # Ensure criteria_scores list is populated
            evaluation.criteria_scores = [
                evaluation.visual_appeal,
                evaluation.functionality,
                evaluation.responsiveness,
                evaluation.code_quality,
                evaluation.task_completion,
            ]
            # Log the evaluation result
            scores_dict = {
                "overall": evaluation.overall_score,
                "visual_appeal": evaluation.visual_appeal.score,
                "functionality": evaluation.functionality.score,
                "responsiveness": evaluation.responsiveness.score,
                "code_quality": evaluation.code_quality.score,
                "task_completion": evaluation.task_completion.score,
            }
            self.logger.log_evaluation_result(
                judge_model,
                task_name,
                iteration,
                scores_dict,
                duration=duration,
                target_model=target_model,
            )
            return evaluation
        except Exception as e:
            error_msg = f"Failed to evaluate HTML with {judge_model}: {e}"
            self.logger.error(error_msg)
            raise EvaluationError(error_msg)

    def evaluate_all_iterations(
        self,
        judge_models: List[str],
        target_model: str,
        task_name: str,
        generation_results: List[Dict[str, Any]],
        save_to_timestamp_folder: Optional[str] = None,
    ) -> List[EvaluationResult]:
        """
        Evaluate all iterations of a task using multiple judges.
        Args:
            judge_models: List of models to use as judges
            target_model: Model that generated the HTML
            task_name: Name of the task
            task_description: Description of the task
            generation_results: List of generation results from HTMLGenerator
        Returns:
            List of evaluation results
        """
        try:
            self.logger.info(
                f"Starting evaluation of {len(generation_results)} iterations for {task_name}"
            )
            all_evaluations = []
            for judge_model in judge_models:
                self.logger.info(f"Judge {judge_model} evaluating {task_name}")
                for i, result in enumerate(generation_results):
                    iteration = result["iteration"]
                    html_content = result["html_content"]
                    # Use LLM-optimized screenshot for evaluation if available, otherwise use full screenshot
                    screenshot_path = result.get("llm_screenshot_path") or result.get(
                        "screenshot_path"
                    )
                    try:
                        evaluation = self.evaluate_html(
                            judge_model=judge_model,
                            target_model=target_model,
                            task_name=task_name,
                            iteration=iteration,
                            html_content=html_content,
                            screenshot_path=screenshot_path,
                        )
                        all_evaluations.append(evaluation)
                        # Save individual evaluation
                        if save_to_timestamp_folder:
                            # Save in timestamp folder format: v1_result_judge.json
                            eval_dir = (
                                Path(save_to_timestamp_folder)
                                / target_model
                                / task_name
                            )
                            eval_dir.mkdir(parents=True, exist_ok=True)
                            eval_filename = f"v{iteration}_result_{judge_model}.json"
                            eval_path = eval_dir / eval_filename
                        else:
                            # Save in traditional evaluations folder
                            eval_dir = (
                                self.output_dir
                                / "evaluations"
                                / target_model
                                / task_name
                            )
                            eval_dir.mkdir(parents=True, exist_ok=True)
                            eval_filename = (
                                f"{judge_model}_iter{iteration}_evaluation.json"
                            )
                            eval_path = eval_dir / eval_filename
                        with open(eval_path, "w") as f:
                            json.dump(evaluation.model_dump(),
                                      f, indent=2, default=str)
                        self.logger.info(f"Saved evaluation: {eval_path}")
                    except Exception as e:
                        self.logger.error(
                            f"Failed to evaluate iteration {iteration} with {judge_model}: {e}"
                        )
                        continue
            self.logger.info(
                f"Completed evaluation for {task_name}: {len(all_evaluations)} evaluations"
            )
            return all_evaluations
        except Exception as e:
            error_msg = f"Failed to evaluate all iterations for {task_name}: {e}"
            self.logger.error(error_msg)
            raise EvaluationError(error_msg)

    def create_task_summary(
        self, target_model: str, task_name: str, evaluations: List[EvaluationResult]
    ) -> TaskEvaluationSummary:
        """
        Create a summary of all evaluations for a task.
        Args:
            target_model: Model that generated the HTML
            task_name: Name of the task
            evaluations: List of evaluation results
        Returns:
            Task evaluation summary
        """
        try:
            if not evaluations:
                raise EvaluationError("No evaluations provided for summary")
            # Group evaluations by iteration
            evaluations_by_iteration = {}
            for eval_result in evaluations:
                iteration = eval_result.iteration
                if iteration not in evaluations_by_iteration:
                    evaluations_by_iteration[iteration] = []
                evaluations_by_iteration[iteration].append(eval_result)
            # Calculate average scores by iteration
            score_progression = []
            average_scores_by_criteria = {
                "visual_appeal": [],
                "functionality": [],
                "responsiveness": [],
                "code_quality": [],
                "task_completion": [],
            }
            for iteration in sorted(evaluations_by_iteration.keys()):
                iter_evaluations = evaluations_by_iteration[iteration]
                # Average overall score for this iteration
                avg_overall = sum(e.overall_score for e in iter_evaluations) / len(
                    iter_evaluations
                )
                score_progression.append(avg_overall)
                # Average criteria scores
                for criteria in average_scores_by_criteria.keys():
                    scores = [
                        getattr(e, criteria).score for e in iter_evaluations]
                    avg_score = sum(scores) / len(scores)
                    average_scores_by_criteria[criteria].append(avg_score)
            # Find best and worst iterations
            best_iteration = score_progression.index(
                max(score_progression)) + 1
            worst_iteration = score_progression.index(
                min(score_progression)) + 1
            # Calculate judge agreement (variance-based measure)
            judge_agreement_scores = []
            for iteration in evaluations_by_iteration.keys():
                iter_evaluations = evaluations_by_iteration[iteration]
                if len(iter_evaluations) > 1:
                    scores = [e.overall_score for e in iter_evaluations]
                    variance = sum(
                        (s - sum(scores) / len(scores)) ** 2 for s in scores
                    ) / len(scores)
                    agreement = max(0, 1 - variance / 25)  # Normalize to 0-1
                    judge_agreement_scores.append(agreement)
            judge_agreement_score = (
                sum(judge_agreement_scores) / len(judge_agreement_scores)
                if judge_agreement_scores
                else 1.0
            )
            # Identify controversial criteria (high disagreement)
            controversial_criteria = []
            for criteria in average_scores_by_criteria.keys():
                criteria_variances = []
                for iteration in evaluations_by_iteration.keys():
                    iter_evaluations = evaluations_by_iteration[iteration]
                    if len(iter_evaluations) > 1:
                        scores = [
                            getattr(e, criteria).score for e in iter_evaluations]
                        variance = sum(
                            (s - sum(scores) / len(scores)) ** 2 for s in scores
                        ) / len(scores)
                        criteria_variances.append(variance)
                if (
                    criteria_variances
                    and sum(criteria_variances) / len(criteria_variances) > 2.0
                ):
                    controversial_criteria.append(criteria)
            # Calculate improvements
            overall_improvement = (
                score_progression[-1] - score_progression[0]
                if len(score_progression) > 1
                else 0
            )
            criteria_improvements = {}
            for criteria, scores in average_scores_by_criteria.items():
                if len(scores) > 1:
                    criteria_improvements[criteria] = scores[-1] - scores[0]
                else:
                    criteria_improvements[criteria] = 0
            # Collect strengths and weaknesses
            all_strengths = []
            all_weaknesses = []
            for evaluation in evaluations:
                all_strengths.extend(evaluation.strengths)
                all_weaknesses.extend(evaluation.weaknesses)
            # Get most common strengths and weaknesses
            strength_counts = {}
            weakness_counts = {}
            for strength in all_strengths:
                strength_counts[strength] = strength_counts.get(
                    strength, 0) + 1
            for weakness in all_weaknesses:
                weakness_counts[weakness] = weakness_counts.get(
                    weakness, 0) + 1
            key_strengths = sorted(
                strength_counts.keys(), key=lambda x: strength_counts[x], reverse=True
            )[:5]
            key_weaknesses = sorted(
                weakness_counts.keys(), key=lambda x: weakness_counts[x], reverse=True
            )[:5]
            # Priority improvements (from most recent evaluations)
            recent_evaluations = evaluations_by_iteration.get(
                max(evaluations_by_iteration.keys()), []
            )
            priority_improvements = []
            for evaluation in recent_evaluations:
                priority_improvements.extend(
                    evaluation.improvement_suggestions)
            # Remove duplicates while preserving order
            priority_improvements = list(
                dict.fromkeys(priority_improvements))[:10]
            # Create summary
            summary = TaskEvaluationSummary(
                task_name=task_name,
                target_model=target_model,
                total_iterations=len(evaluations_by_iteration),
                judge_models=list(set(e.judge_model for e in evaluations)),
                total_evaluations=len(evaluations),
                score_progression=score_progression,
                average_scores_by_criteria=average_scores_by_criteria,
                final_overall_score=score_progression[-1] if score_progression else 0,
                best_iteration=best_iteration,
                worst_iteration=worst_iteration,
                judge_agreement_score=judge_agreement_score,
                controversial_criteria=controversial_criteria,
                overall_improvement=overall_improvement,
                criteria_improvements=criteria_improvements,
                key_strengths=key_strengths,
                key_weaknesses=key_weaknesses,
                priority_improvements=priority_improvements,
            )
            # Save summary
            summary_dir = self.output_dir / "summaries" / target_model
            summary_dir.mkdir(parents=True, exist_ok=True)
            summary_path = summary_dir / f"{task_name}_summary.json"
            with open(summary_path, "w") as f:
                json.dump(summary.model_dump(), f, indent=2, default=str)
            self.logger.info(f"Created task summary: {summary_path}")
            return summary
        except Exception as e:
            error_msg = f"Failed to create task summary for {task_name}: {e}"
            self.logger.error(error_msg)
            raise EvaluationError(error_msg)

    def get_evaluation_stats(
        self, evaluations: List[EvaluationResult]
    ) -> Dict[str, Any]:
        """Get statistics from evaluation results."""
        if not evaluations:
            return {}
        # Overall statistics
        overall_scores = [e.overall_score for e in evaluations]
        # Criteria statistics
        criteria_stats = {}
        for criteria in [
            "visual_appeal",
            "functionality",
            "responsiveness",
            "code_quality",
            "task_completion",
        ]:
            scores = [getattr(e, criteria).score for e in evaluations]
            criteria_stats[criteria] = {
                "average": sum(scores) / len(scores),
                "min": min(scores),
                "max": max(scores),
                "variance": sum((s - sum(scores) / len(scores)) ** 2 for s in scores)
                / len(scores),
            }
        # Judge statistics
        judge_stats = {}
        for evaluation in evaluations:
            judge = evaluation.judge_model
            if judge not in judge_stats:
                judge_stats[judge] = {"count": 0, "total_score": 0}
            judge_stats[judge]["count"] += 1
            judge_stats[judge]["total_score"] += evaluation.overall_score
        for judge in judge_stats:
            judge_stats[judge]["average_score"] = (
                judge_stats[judge]["total_score"] / judge_stats[judge]["count"]
            )
        return {
            "total_evaluations": len(evaluations),
            "average_overall_score": sum(overall_scores) / len(overall_scores),
            "min_overall_score": min(overall_scores),
            "max_overall_score": max(overall_scores),
            "score_variance": sum(
                (s - sum(overall_scores) / len(overall_scores)) ** 2
                for s in overall_scores
            )
            / len(overall_scores),
            "criteria_stats": criteria_stats,
            "judge_stats": judge_stats,
            "unique_judges": len(set(e.judge_model for e in evaluations)),
            "unique_tasks": len(set(e.task_name for e in evaluations)),
            "unique_models": len(set(e.target_model for e in evaluations)),
        }
