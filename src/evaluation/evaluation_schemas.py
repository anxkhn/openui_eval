"""Pydantic schemas for structured evaluation results."""

from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field


class CriteriaScore(BaseModel):
    """Score for a specific evaluation criteria."""

    criteria: str = Field(description="Name of the evaluation criteria")
    score: float = Field(ge=0, le=10, description="Score from 0 to 10")
    reasoning: str = Field(description="Detailed reasoning for the score")
    suggestions: Optional[str] = Field(
        default=None, description="Suggestions for improvement"
    )


class ModelRanking(BaseModel):
    """Model ranking entry."""

    model: str = Field(description="Model name")
    score: float = Field(description="Model score")


class TaskDifficultyRanking(BaseModel):
    """Task difficulty ranking entry."""

    task: str = Field(description="Task name")
    average_score: float = Field(description="Average score across models")


class EvaluationResult(BaseModel):
    """Complete evaluation result for a generated HTML."""

    # Metadata
    judge_model: str = Field(
        description="Name of the model that performed the evaluation"
    )
    target_model: str = Field(
        description="Name of the model that generated the HTML")
    task_name: str = Field(description="Name of the task being evaluated")
    iteration: int = Field(
        ge=1, description="Iteration number of the generated HTML")
    # Overall assessment
    overall_score: float = Field(
        ge=0, le=10, description="Overall score from 0 to 10")
    overall_feedback: str = Field(
        description="General feedback about the HTML generation"
    )
    # Detailed criteria scores
    criteria_scores: List[CriteriaScore] = Field(
        description="Scores for each evaluation criteria"
    )
    # Specific assessments
    visual_appeal: CriteriaScore = Field(
        description="Assessment of visual design and aesthetics"
    )
    functionality: CriteriaScore = Field(
        description="Assessment of functional requirements completion"
    )
    responsiveness: CriteriaScore = Field(
        description="Assessment of responsive design implementation"
    )
    code_quality: CriteriaScore = Field(
        description="Assessment of HTML/CSS/JS code quality"
    )
    task_completion: CriteriaScore = Field(
        description="Assessment of how well the task requirements were met"
    )
    # Additional insights
    strengths: List[str] = Field(
        description="List of strengths identified in the HTML")
    weaknesses: List[str] = Field(
        description="List of weaknesses identified in the HTML"
    )
    improvement_suggestions: List[str] = Field(
        description="Specific suggestions for improvement"
    )
    # Technical details
    technical_issues: List[str] = Field(
        default_factory=list, description="Technical issues found"
    )
    accessibility_notes: List[str] = Field(
        default_factory=list, description="Accessibility considerations"
    )
    performance_notes: List[str] = Field(
        default_factory=list, description="Performance considerations"
    )
    # Comparative assessment (if applicable)
    comparison_with_previous: Optional[str] = Field(
        default=None, description="Comparison with previous iteration"
    )
    improvement_from_previous: Optional[float] = Field(
        default=None,
        ge=-10,
        le=10,
        description="Improvement score compared to previous iteration",
    )


class TaskEvaluationSummary(BaseModel):
    """Summary of all evaluations for a specific task."""

    task_name: str = Field(description="Name of the task")
    target_model: str = Field(
        description="Name of the model that generated the HTML")
    total_iterations: int = Field(
        ge=1, description="Total number of iterations evaluated"
    )
    # Judge statistics
    judge_models: List[str] = Field(
        description="List of models that performed evaluations"
    )
    total_evaluations: int = Field(
        description="Total number of evaluations performed")
    # Score progression
    score_progression: List[float] = Field(
        description="Overall scores for each iteration"
    )
    average_scores_by_criteria: Dict[str, List[float]] = Field(
        description="Average scores by criteria across iterations"
    )
    # Final assessment
    final_overall_score: float = Field(
        ge=0, le=10, description="Final overall score (average across judges)"
    )
    best_iteration: int = Field(
        ge=1, description="Iteration number with the highest score"
    )
    worst_iteration: int = Field(
        ge=1, description="Iteration number with the lowest score"
    )
    # Consensus analysis
    judge_agreement_score: float = Field(
        ge=0, le=1, description="Agreement level between judges (0-1)"
    )
    controversial_criteria: List[str] = Field(
        description="Criteria with high disagreement between judges"
    )
    # Improvement analysis
    overall_improvement: float = Field(
        ge=-10, le=10, description="Overall improvement from first to last iteration"
    )
    criteria_improvements: Dict[str, float] = Field(
        description="Improvement by criteria from first to last iteration"
    )
    # Recommendations
    key_strengths: List[str] = Field(
        description="Key strengths identified across all evaluations"
    )
    key_weaknesses: List[str] = Field(
        description="Key weaknesses identified across all evaluations"
    )
    priority_improvements: List[str] = Field(
        description="Priority areas for improvement"
    )


class BenchmarkSummary(BaseModel):
    """Complete benchmark summary across all models and tasks."""

    # Metadata
    benchmark_timestamp: str = Field(
        description="Timestamp when benchmark was completed"
    )
    total_models: int = Field(description="Total number of models benchmarked")
    total_tasks: int = Field(description="Total number of tasks evaluated")
    total_iterations_per_task: int = Field(
        description="Number of iterations per task")
    # Model performance
    model_rankings: List[ModelRanking] = Field(
        description="Models ranked by overall performance"
    )
    model_scores: Dict[str, float] = Field(
        description="Average scores for each model")
    model_strengths: Dict[str, List[str]] = Field(
        description="Key strengths for each model"
    )
    model_weaknesses: Dict[str, List[str]] = Field(
        description="Key weaknesses for each model"
    )
    # Task analysis
    task_difficulty_ranking: List[TaskDifficultyRanking] = Field(
        description="Tasks ranked by difficulty (lowest average scores)"
    )
    task_performance: Dict[str, Dict[str, float]] = Field(
        description="Performance by task and model"
    )
    # Criteria analysis
    criteria_performance: Dict[str, Dict[str, float]] = Field(
        description="Performance by criteria and model"
    )
    most_challenging_criteria: List[str] = Field(
        description="Criteria with lowest average scores"
    )
    best_performing_criteria: List[str] = Field(
        description="Criteria with highest average scores"
    )
    # Improvement analysis
    models_with_best_improvement: List[str] = Field(
        description="Models showing best improvement over iterations"
    )
    average_improvement_by_model: Dict[str, float] = Field(
        description="Average improvement scores by model"
    )
    # Statistical insights
    score_variance_by_model: Dict[str, float] = Field(
        description="Score variance for each model (consistency measure)"
    )
    judge_reliability_scores: Dict[str, float] = Field(
        description="Reliability scores for each judge model"
    )
    # Recommendations
    top_performing_models: List[str] = Field(
        description="Top 3 performing models overall"
    )
    most_improved_models: List[str] = Field(
        description="Models with highest improvement rates"
    )
    recommended_model_for_tasks: Dict[str, str] = Field(
        description="Recommended model for each task type"
    )
