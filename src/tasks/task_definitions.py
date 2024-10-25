"""
Task definitions for the multimodal LLM benchmark system.
This module contains core data structures for defining tasks.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class TaskCategory(Enum):
    """Categories for organizing tasks."""

    CALCULATOR = "calculator"
    WEBSITE = "website"
    PORTFOLIO = "portfolio"
    DASHBOARD = "dashboard"
    GAME = "game"
    FORM = "form"
    VISUALIZATION = "visualization"
    INTERACTIVE = "interactive"


class DifficultyLevel(Enum):
    """Difficulty levels for tasks."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class TaskDefinition:
    """Definition of a benchmark task."""

    name: str
    category: TaskCategory
    difficulty: DifficultyLevel
    prompt: str
    description: str
    requirements: List[str]
    evaluation_criteria: List[str]
    expected_features: List[str]
    time_estimate_minutes: int
    tags: List[str]
    project_type: str = "html"  # html, react, vue, angular, nextjs, svelte
    framework_version: Optional[str] = None
