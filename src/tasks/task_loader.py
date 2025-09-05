"""
Task loader for JSON-based task definitions.
Supports loading tasks from external JSON files alongside traditional Python-defined tasks.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Python < 3.7 fallback
    import importlib_resources as pkg_resources

from tasks.task_definitions import TaskDefinition, TaskCategory, DifficultyLevel


@dataclass
class TaskConfig:
    """Configuration for task loading."""

    tasks_dir: str = "tasks"
    include_default_tasks: bool = True
    include_artifactsbench: bool = True
    include_webgen_bench: bool = True
    include_frontendbench: bool = True
    include_astra: bool = True
    include_frontend_tasks: bool = True
    custom_task_files: List[str] = field(default_factory=list)


class TaskLoader:
    """Loads tasks from JSON files and combines them with Python-defined tasks."""

    def __init__(self, config: Optional[TaskConfig] = None):
        """Initialize task loader with configuration."""
        self.config = config or TaskConfig()

        # Find the tasks directory using multiple fallback strategies
        possible_paths = [
            Path(self.config.tasks_dir),  # Configured path
            Path("tasks"),  # Current directory
            Path("../tasks"),  # Parent directory
        ]

        # Try to find the package directory and add tasks path
        try:
            import openui_eval

            package_path = Path(openui_eval.__file__).parent
            possible_paths.extend(
                [
                    package_path / "tasks",  # In package directory
                    package_path.parent / "tasks",  # Next to package directory
                ]
            )
        except ImportError:
            pass

        # Find the first existing path
        self.tasks_dir = None
        for path in possible_paths:
            if path.exists() and any(path.glob("*.json")):
                self.tasks_dir = path
                break

        # If still not found, use the default and let it fail gracefully
        if self.tasks_dir is None:
            self.tasks_dir = Path(self.config.tasks_dir)

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
            "frontend": TaskCategory.WEBSITE,
            "backend": TaskCategory.INTERACTIVE,
            "fullstack": TaskCategory.INTERACTIVE,
            "general": TaskCategory.INTERACTIVE,
        }

        # Handle various string formats
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

    def _convert_json_to_task(self, task_data: Dict[str, Any]) -> TaskDefinition:
        """Convert JSON task data to TaskDefinition object."""
        # Handle various time estimate field formats
        time_estimate = task_data.get(
            "time_estimate_minutes",
            task_data.get(
                "estimated_time_minutes", task_data.get("estimated_time", 30)
            ),
        )

        # If estimated_time is a string like "45-90 minutes", extract a number
        if isinstance(time_estimate, str):
            import re

            numbers = re.findall(r"\d+", time_estimate)
            if numbers:
                time_estimate = int(numbers[0])
            else:
                time_estimate = 45  # Default for ASTRA tasks

        # Handle basic requirements field - ASTRA uses list format
        requirements = task_data.get("requirements", {})
        if isinstance(requirements, list):
            # Convert list to dict format for TaskDefinition
            requirements = {"functional": requirements, "design": [], "technical": []}
        elif not isinstance(requirements, dict):
            requirements = {
                "functional": [requirements] if requirements else [],
                "design": [],
                "technical": [],
            }

        return TaskDefinition(
            name=task_data["name"],
            category=self._map_string_to_category(task_data["category"]),
            difficulty=self._map_string_to_difficulty(task_data["difficulty"]),
            prompt=task_data["prompt"],
            description=task_data["description"],
            requirements=requirements,
            evaluation_criteria=task_data["evaluation_criteria"],
            expected_features=task_data["expected_features"],
            time_estimate_minutes=time_estimate,
            tags=task_data["tags"],
            project_type=task_data.get("project_type", "html"),
            framework_version=task_data.get("framework_version"),
        )

    def _load_json_file(self, file_path: Path) -> List[TaskDefinition]:
        """Load tasks from a JSON file."""
        if not file_path.exists():
            return []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list):
                return [self._convert_json_to_task(task) for task in data]
            elif isinstance(data, dict):
                # Handle both single task dict and multiple tasks dict (like ASTRA)
                if "name" in data and "prompt" in data:
                    # Single task in dict format
                    return [self._convert_json_to_task(data)]
                else:
                    # Multiple tasks in dict format (key: task_name, value: task_data)
                    return [
                        self._convert_json_to_task(task_data)
                        for task_data in data.values()
                    ]
            else:
                print(f"Warning: Unexpected data format in {file_path}")
                return []

        except Exception as e:
            print(f"Error loading tasks from {file_path}: {e}")
            return []

    def _load_artifactsbench_tasks(self) -> Dict[str, TaskDefinition]:
        """Load ArtifactsBench tasks from JSON files."""
        tasks = {}
        artifactsbench_files = [
            "artifactsbench_combined.json"  # Only use combined file to avoid duplicates
        ]

        for filename in artifactsbench_files:
            file_path = self.tasks_dir / filename
            if file_path.exists():
                print(f"Loading ArtifactsBench tasks from {filename}")
                loaded_tasks = self._load_json_file(file_path)
                for task in loaded_tasks:
                    if task.name not in tasks:
                        tasks[task.name] = task
                    else:
                        print(
                            f"Warning: Duplicate task name {task.name} from {filename}"
                        )

        return tasks

    def _load_webgen_bench_tasks(self) -> Dict[str, TaskDefinition]:
        """Load WebGen-Bench tasks from JSON file."""
        tasks = {}
        webgen_files = ["webgen_bench_tasks.json"]

        for filename in webgen_files:
            file_path = self.tasks_dir / filename
            if file_path.exists():
                print(f"Loading WebGen-Bench tasks from {filename}")
                loaded_tasks = self._load_json_file(file_path)
                for task in loaded_tasks:
                    if task.name not in tasks:
                        tasks[task.name] = task
                    else:
                        print(
                            f"Warning: Duplicate task name {task.name} from {filename}"
                        )

        return tasks

    def _load_frontendbench_tasks(self) -> Dict[str, TaskDefinition]:
        """Load FrontendBench tasks from JSON file."""
        tasks = {}
        frontendbench_files = ["frontendbench_tasks.json"]

        for filename in frontendbench_files:
            file_path = self.tasks_dir / filename
            if file_path.exists():
                print(f"Loading FrontendBench tasks from {filename}")
                loaded_tasks = self._load_json_file(file_path)
                for task in loaded_tasks:
                    if task.name not in tasks:
                        tasks[task.name] = task
                    else:
                        print(
                            f"Warning: Duplicate task name {task.name} from {filename}"
                        )

        return tasks

    def _load_astra_tasks(self) -> Dict[str, TaskDefinition]:
        """Load ASTRA tasks from JSON file."""
        tasks = {}
        astra_files = ["astra_tasks.json"]

        for filename in astra_files:
            file_path = self.tasks_dir / filename
            if file_path.exists():
                print(f"Loading ASTRA tasks from {filename}")
                loaded_tasks = self._load_json_file(file_path)
                for task in loaded_tasks:
                    if task.name not in tasks:
                        tasks[task.name] = task
                    else:
                        print(
                            f"Warning: Duplicate task name {task.name} from {filename}"
                        )

        return tasks

    def _load_frontend_tasks(self) -> Dict[str, TaskDefinition]:
        """Load frontend framework tasks from JSON files."""
        tasks = {}
        frontend_files = [
            "frontend_additional_tasks.json",
            "frontend_expanded_tasks.json",
            "frontend_comprehensive_tasks.json",
            "frontend_final_tasks.json",
        ]

        for filename in frontend_files:
            file_path = self.tasks_dir / filename
            if file_path.exists():
                print(f"Loading frontend tasks from {filename}")
                loaded_tasks = self._load_json_file(file_path)
                for task in loaded_tasks:
                    if task.name not in tasks:
                        tasks[task.name] = task
                    else:
                        print(
                            f"Warning: Duplicate task name {task.name} from {filename}"
                        )

        return tasks

    def _load_custom_tasks(self) -> Dict[str, TaskDefinition]:
        """Load custom task files specified in configuration."""
        tasks = {}

        for filename in self.config.custom_task_files:
            file_path = self.tasks_dir / filename
            if file_path.exists():
                print(f"Loading custom tasks from {filename}")
                loaded_tasks = self._load_json_file(file_path)
                for task in loaded_tasks:
                    if task.name not in tasks:
                        tasks[task.name] = task
                    else:
                        print(
                            f"Warning: Duplicate task name {task.name} from {filename}"
                        )
            else:
                print(f"Warning: Custom task file {filename} not found")

        return tasks

    def load_all_tasks(self) -> Dict[str, TaskDefinition]:
        """Load all tasks from various sources."""
        self._loaded_tasks.clear()

        # Load predefined tasks from JSON
        if self.config.include_default_tasks:
            from .predefined_loader import PredefinedTaskLoader

            predefined_loader = PredefinedTaskLoader(self.config.tasks_dir)
            predefined_tasks = predefined_loader.get_all_tasks()
            self._loaded_tasks.update(predefined_tasks)
            print(f"Loaded {len(predefined_tasks)} predefined tasks")

        # Load ArtifactsBench tasks
        if self.config.include_artifactsbench:
            artifactsbench_tasks = self._load_artifactsbench_tasks()
            self._loaded_tasks.update(artifactsbench_tasks)
            print(f"Loaded {len(artifactsbench_tasks)} ArtifactsBench tasks")

        # Load WebGen-Bench tasks
        if self.config.include_webgen_bench:
            webgen_tasks = self._load_webgen_bench_tasks()
            self._loaded_tasks.update(webgen_tasks)
            print(f"Loaded {len(webgen_tasks)} WebGen-Bench tasks")

        # Load FrontendBench tasks
        if self.config.include_frontendbench:
            frontendbench_tasks = self._load_frontendbench_tasks()
            self._loaded_tasks.update(frontendbench_tasks)
            print(f"Loaded {len(frontendbench_tasks)} FrontendBench tasks")

        # Load ASTRA tasks
        if self.config.include_astra:
            astra_tasks = self._load_astra_tasks()
            self._loaded_tasks.update(astra_tasks)
            print(f"Loaded {len(astra_tasks)} ASTRA tasks")

        # Load Frontend framework tasks
        if self.config.include_frontend_tasks:
            frontend_tasks = self._load_frontend_tasks()
            self._loaded_tasks.update(frontend_tasks)
            print(f"Loaded {len(frontend_tasks)} frontend framework tasks")

        # Load custom tasks
        custom_tasks = self._load_custom_tasks()
        self._loaded_tasks.update(custom_tasks)
        if custom_tasks:
            print(f"Loaded {len(custom_tasks)} custom tasks")

        return self._loaded_tasks

    def get_task(self, task_name: str) -> Optional[TaskDefinition]:
        """Get a specific task by name."""
        if not self._loaded_tasks:
            self.load_all_tasks()
        return self._loaded_tasks.get(task_name)

    def get_tasks_by_category(self, category: TaskCategory) -> List[TaskDefinition]:
        """Get all tasks in a specific category."""
        if not self._loaded_tasks:
            self.load_all_tasks()

        return [
            task for task in self._loaded_tasks.values() if task.category == category
        ]

    def get_tasks_by_difficulty(
        self, difficulty: DifficultyLevel
    ) -> List[TaskDefinition]:
        """Get all tasks at a specific difficulty level."""
        if not self._loaded_tasks:
            self.load_all_tasks()

        return [
            task
            for task in self._loaded_tasks.values()
            if task.difficulty == difficulty
        ]

    def get_task_names(self) -> List[str]:
        """Get all available task names."""
        if not self._loaded_tasks:
            self.load_all_tasks()
        return list(self._loaded_tasks.keys())

    def get_available_categories(self) -> List[TaskCategory]:
        """Get all available categories with tasks."""
        if not self._loaded_tasks:
            self.load_all_tasks()

        categories = set()
        for task in self._loaded_tasks.values():
            categories.add(task.category)
        return sorted(list(categories))

    def get_available_difficulties(self) -> List[DifficultyLevel]:
        """Get all available difficulty levels with tasks."""
        if not self._loaded_tasks:
            self.load_all_tasks()

        difficulties = set()
        for task in self._loaded_tasks.values():
            difficulties.add(task.difficulty)
        return sorted(list(difficulties))

    def search_tasks(self, query: str) -> List[TaskDefinition]:
        """Search tasks by name, description, or tags."""
        if not self._loaded_tasks:
            self.load_all_tasks()

        query_lower = query.lower()
        results = []

        for task in self._loaded_tasks.values():
            if (
                query_lower in task.name.lower()
                or query_lower in task.description.lower()
                or any(query_lower in tag.lower() for tag in task.tags)
            ):
                results.append(task)

        return results

    def print_task_summary(self):
        """Print a summary of loaded tasks."""
        if not self._loaded_tasks:
            self.load_all_tasks()

        print(f"\nTask Summary:")
        print(f"Total tasks: {len(self._loaded_tasks)}")

        # Count by category
        category_counts = {}
        for task in self._loaded_tasks.values():
            category = task.category.value
            category_counts[category] = category_counts.get(category, 0) + 1

        print("Tasks by category:")
        for category, count in sorted(category_counts.items()):
            print(f"  {category}: {count}")

        # Count by difficulty
        difficulty_counts = {}
        for task in self._loaded_tasks.values():
            difficulty = task.difficulty.value
            difficulty_counts[difficulty] = difficulty_counts.get(difficulty, 0) + 1

        print("Tasks by difficulty:")
        for difficulty, count in sorted(difficulty_counts.items()):
            print(f"  {difficulty}: {count}")

        # Count by project type
        project_counts = {}
        for task in self._loaded_tasks.values():
            project_type = task.project_type
            project_counts[project_type] = project_counts.get(project_type, 0) + 1

        print("Tasks by project type:")
        for project_type, count in sorted(project_counts.items()):
            print(f"  {project_type}: {count}")


# Global task loader instance
_task_loader: Optional[TaskLoader] = None


def get_task_loader(config: Optional[TaskConfig] = None) -> TaskLoader:
    """Get the global task loader instance."""
    global _task_loader
    if _task_loader is None:
        _task_loader = TaskLoader(config)
    return _task_loader


def load_tasks(config: Optional[TaskConfig] = None) -> Dict[str, TaskDefinition]:
    """Load all tasks using the global task loader."""
    return get_task_loader(config).load_all_tasks()


def get_task(
    task_name: str, config: Optional[TaskConfig] = None
) -> Optional[TaskDefinition]:
    """Get a specific task using the global task loader."""
    return get_task_loader(config).get_task(task_name)
