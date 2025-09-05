"""
Loader for predefined tasks from JSON files.
This module loads the traditional task definitions from JSON format instead of hardcoded Python.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

from tasks.task_definitions import TaskDefinition, TaskCategory, DifficultyLevel


class PredefinedTaskLoader:
    """Loads predefined tasks from JSON files."""

    def __init__(self, tasks_dir: str = "tasks"):
        """Initialize with tasks directory path."""
        self.tasks_dir = Path(tasks_dir)
        self._loaded_tasks: Dict[str, TaskDefinition] = {}

    def _map_string_to_category(self, category_str: str) -> TaskCategory:
        """Map string category to TaskCategory enum."""
        category_mapping = {
            "calculator": TaskCategory.CALCULATOR,
            "website": TaskCategory.WEBSITE,
            "portfolio": TaskCategory.PORTFOLIO,
            "dashboard": TaskCategory.DASHBOARD,
            "game": TaskCategory.GAME,
            "form": TaskCategory.FORM,
            "visualization": TaskCategory.VISUALIZATION,
            "interactive": TaskCategory.INTERACTIVE,
        }

        normalized = category_str.lower().strip()
        return category_mapping.get(normalized, TaskCategory.INTERACTIVE)

    def _map_string_to_difficulty(self, difficulty_str: str) -> DifficultyLevel:
        """Map string difficulty to DifficultyLevel enum."""
        difficulty_mapping = {
            "beginner": DifficultyLevel.BEGINNER,
            "intermediate": DifficultyLevel.INTERMEDIATE,
            "advanced": DifficultyLevel.ADVANCED,
            "expert": DifficultyLevel.EXPERT,
        }

        normalized = difficulty_str.lower().strip()
        return difficulty_mapping.get(normalized, DifficultyLevel.INTERMEDIATE)

    def _convert_to_task_definition(self, task_data: Dict) -> TaskDefinition:
        """Convert JSON task data to TaskDefinition object."""
        return TaskDefinition(
            name=task_data["name"],
            category=self._map_string_to_category(task_data["category"]),
            difficulty=self._map_string_to_difficulty(task_data["difficulty"]),
            prompt=task_data["prompt"],
            description=task_data["description"],
            requirements=task_data["requirements"],
            evaluation_criteria=task_data["evaluation_criteria"],
            expected_features=task_data["expected_features"],
            time_estimate_minutes=task_data["time_estimate_minutes"],
            tags=task_data["tags"],
            project_type=task_data.get("project_type", "html"),
            framework_version=task_data.get("framework_version"),
        )

    def load_predefined_tasks(self) -> Dict[str, TaskDefinition]:
        """Load predefined tasks from JSON file."""
        if self._loaded_tasks:
            return self._loaded_tasks

        predefined_file = self.tasks_dir / "predefined_tasks.json"

        if not predefined_file.exists():
            print(f"Warning: Predefined tasks file not found at {predefined_file}")
            return {}

        try:
            with open(predefined_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            if "predefined_tasks" not in data:
                print(f"Warning: 'predefined_tasks' key not found in {predefined_file}")
                return {}

            for task_name, task_data in data["predefined_tasks"].items():
                try:
                    task = self._convert_to_task_definition(task_data)
                    self._loaded_tasks[task_name] = task
                except Exception as e:
                    print(f"Error loading task {task_name}: {e}")
                    continue

            print(
                f"Loaded {len(self._loaded_tasks)} predefined tasks from {predefined_file}"
            )
            return self._loaded_tasks

        except Exception as e:
            print(f"Error loading predefined tasks: {e}")
            return {}

    def get_task(self, task_name: str) -> Optional[TaskDefinition]:
        """Get a specific predefined task by name."""
        if not self._loaded_tasks:
            self.load_predefined_tasks()
        return self._loaded_tasks.get(task_name)

    def get_all_tasks(self) -> Dict[str, TaskDefinition]:
        """Get all predefined tasks."""
        return self.load_predefined_tasks()

    def get_tasks_by_category(self, category: TaskCategory) -> List[TaskDefinition]:
        """Get all predefined tasks in a specific category."""
        tasks = self.get_all_tasks()
        return [task for task in tasks.values() if task.category == category]

    def get_tasks_by_difficulty(
        self, difficulty: DifficultyLevel
    ) -> List[TaskDefinition]:
        """Get all predefined tasks at a specific difficulty level."""
        tasks = self.get_all_tasks()
        return [task for task in tasks.values() if task.difficulty == difficulty]
