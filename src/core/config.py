"""Configuration management for the benchmark system."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from dotenv import load_dotenv

# Load environment variables immediately
load_dotenv()


@dataclass
class ModelConfig:
    """Configuration for individual models."""

    name: str
    temperature: float = 0.1
    num_ctx: int = 32768  # 32K context
    num_predict: int = -1  # Infinite prediction
    timeout: int = 300  # 5 minutes
    max_retries: int = 3


@dataclass
class TaskConfig:
    """Configuration for benchmark tasks."""

    name: str
    description: str
    prompt_template: str
    expected_elements: List[str] = field(default_factory=list)
    difficulty: str = "medium"  # easy, medium, hard
    project_type: str = "html"  # html, react, vue, angular, nextjs, svelte
    framework_version: Optional[str] = None


@dataclass
class RenderingConfig:
    """Configuration for web rendering."""

    viewport_width: int = 1920
    viewport_height: int = 1080
    wait_time: int = 3  # seconds to wait after page load
    screenshot_format: str = "PNG"
    headless: bool = True
    timeout: int = 30


@dataclass
class ProjectConfig:
    """Configuration for multi-file projects."""

    work_dir: str = "temp_projects"
    node_version: str = "22.12.0"  # Node v22 LTS
    supported_frameworks: List[str] = field(
        default_factory=lambda: ["react", "nextjs", "vue", "angular", "svelte"]
    )
    default_ports: Dict[str, int] = field(
        default_factory=lambda: {
            "react": 3000,
            "nextjs": 3000,
            "vue": 5173,
            "angular": 4200,
            "svelte": 5173,
        }
    )
    install_timeout: int = 300  # 5 minutes
    build_timeout: int = 300  # 5 minutes
    server_start_timeout: int = 60  # 1 minute
    cleanup_on_exit: bool = True


@dataclass
class ProviderConfig:
    """Configuration for LLM providers."""

    provider_type: str = "ollama"  # ollama, vllm, openrouter, gemini

    # Ollama settings
    ollama_host: str = "http://localhost:11434"

    # vLLM settings
    vllm_url: str = "http://localhost:8000/v1/completions"
    vllm_model: str = "meta-llama/Meta-Llama-3-8B-Instruct"

    # OpenRouter settings
    openrouter_url: str = "https://openrouter.ai/api/v1/chat/completions"
    openrouter_model: str = "meta-llama/llama-3.1-8b-instruct:free"
    openrouter_api_key: Optional[str] = None
    openrouter_requests_per_minute: int = 20

    # Gemini settings
    gemini_api_key: Optional[str] = None

    # Common settings
    timeout: int = 300


@dataclass
class EvaluationConfig:
    """Configuration for evaluation/judging."""

    judge_models: List[str] = field(
        default_factory=lambda: [
            "gemma3n:e2b",
            "gemma3:4b",
            "qwen2.5vl:7b",
            "granite3.2-vision:2b",
            "llama3.2-vision:11b",
            "minicpm-v:8b",
            "llava-phi3:3.8b",
        ]
    )
    criteria: List[str] = field(
        default_factory=lambda: [
            "visual_appeal",
            "functionality",
            "responsiveness",
            "code_quality",
            "task_completion",
        ]
    )
    scoring_scale: int = 10
    temperature: float = 0.1


@dataclass
class TasksConfig:
    """Configuration for task loading and management."""

    # Task loading settings
    tasks_dir: str = "tasks"
    include_default_tasks: bool = True
    include_artifactsbench: bool = True
    include_webgen_bench: bool = True
    custom_task_files: List[str] = field(default_factory=list)

    # Task filtering
    task_names: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    difficulties: List[str] = field(default_factory=list)
    project_types: List[str] = field(default_factory=list)


@dataclass
class Config:
    """Main configuration class for the benchmark system."""

    # Model settings
    models: List[ModelConfig] = field(
        default_factory=lambda: [
            ModelConfig("gemma3n:e2b"),
            ModelConfig("gemma3:4b"),
            ModelConfig("qwen2.5vl:7b"),
            ModelConfig("granite3.2-vision:2b"),
            ModelConfig("llama3.2-vision:11b"),
            ModelConfig("minicpm-v:8b"),
            ModelConfig("llava-phi3:3.8b"),
        ]
    )
    # Task settings
    tasks: TasksConfig = field(default_factory=TasksConfig)
    # Pipeline settings
    iterations: int = 3
    judges: List[str] = field(
        default_factory=lambda: ["all"]
    )  # "all" means use all models as judges
    mode: str = "full-pipeline"  # generation-only, judging-only, full-pipeline
    resume_from: Optional[str] = None
    # Output settings
    output_dir: str = "results"
    save_intermediate: bool = True
    compress_logs: bool = True
    # Rendering settings
    rendering: RenderingConfig = field(default_factory=RenderingConfig)
    # Project settings
    projects: ProjectConfig = field(default_factory=ProjectConfig)
    # Evaluation settings
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    # Provider settings
    provider: ProviderConfig = field(default_factory=ProviderConfig)
    # System settings
    max_concurrent_models: int = 1  # Load one model at a time
    memory_threshold: float = 0.8  # 80% memory usage threshold
    log_level: str = "INFO"

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "Config":
        """Load configuration from YAML file."""
        try:
            with open(yaml_path, "r") as f:
                data = yaml.safe_load(f)
            return cls.from_dict(data)
        except Exception as e:
            raise ValueError(f"Failed to load config from {yaml_path}: {e}")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create configuration from dictionary."""
        try:
            # Handle models
            if "models" in data:
                models = []
                for model_data in data["models"]:
                    if isinstance(model_data, str):
                        models.append(ModelConfig(name=model_data))
                    else:
                        models.append(ModelConfig(**model_data))
                data["models"] = models
            # Handle tasks
            if "tasks" in data:
                if isinstance(data["tasks"], dict) and "task_names" in data["tasks"]:
                    # Task names from configuration
                    task_names = data["tasks"]["task_names"]
                    # Import task definitions
                    from tasks.task_loader import get_task

                    filtered_tasks = []
                    for task_name in task_names:
                        # Get task from task loader
                        task_def = get_task(task_name)
                        if task_def:
                            filtered_tasks.append(
                                TaskConfig(
                                    name=task_def.name,
                                    description=task_def.description,
                                    prompt_template=task_def.prompt,
                                    project_type=task_def.project_type,
                                    framework_version=task_def.framework_version,
                                )
                            )
                        else:
                            # Fall back to default tasks
                            default_config = cls()
                            task = next(
                                (
                                    t
                                    for t in default_config.tasks
                                    if t.name == task_name
                                ),
                                None,
                            )
                            if task:
                                filtered_tasks.append(task)
                    data["tasks"] = filtered_tasks
                elif isinstance(data["tasks"], list):
                    # New format with full task configurations
                    tasks = []
                    for task_data in data["tasks"]:
                        if isinstance(task_data, dict):
                            tasks.append(TaskConfig(**task_data))
                        else:
                            # Handle simple string task names
                            default_config = cls()
                            task = next(
                                (
                                    t
                                    for t in default_config.tasks
                                    if t.name == task_data
                                ),
                                None,
                            )
                            if task:
                                tasks.append(task)
                    data["tasks"] = tasks
            # Handle rendering config
            if "rendering" in data:
                rendering_data = data["rendering"]
                if isinstance(rendering_data, dict):
                    # Extract only the fields that RenderingConfig expects
                    rendering_config = {}
                    if "webdriver" in rendering_data:
                        webdriver = rendering_data["webdriver"]
                        if "window_size" in webdriver:
                            rendering_config["viewport_width"] = webdriver[
                                "window_size"
                            ].get("width", 1920)
                            rendering_config["viewport_height"] = webdriver[
                                "window_size"
                            ].get("height", 1080)
                        rendering_config["headless"] = webdriver.get("headless", True)
                        rendering_config["timeout"] = webdriver.get(
                            "page_load_timeout", 30
                        )
                    if "wait_time_seconds" in rendering_data:
                        rendering_config["wait_time"] = rendering_data[
                            "wait_time_seconds"
                        ]
                    if "screenshot" in rendering_data:
                        screenshot = rendering_data["screenshot"]
                        rendering_config["screenshot_format"] = screenshot.get(
                            "format", "PNG"
                        ).upper()

                    # Use the extracted config or fall back to direct mapping
                    if rendering_config:
                        data["rendering"] = RenderingConfig(**rendering_config)
                    else:
                        # Direct mapping for simple configs
                        data["rendering"] = RenderingConfig(**rendering_data)
                else:
                    data["rendering"] = RenderingConfig(**rendering_data)
            # Handle evaluation config
            if "evaluation" in data:
                evaluation_data = data["evaluation"]
                if isinstance(evaluation_data, dict):
                    # Extract only the fields that EvaluationConfig expects
                    evaluation_config = {}
                    if "judge_models" in evaluation_data:
                        evaluation_config["judge_models"] = evaluation_data[
                            "judge_models"
                        ]
                    if "criteria" in evaluation_data:
                        evaluation_config["criteria"] = evaluation_data["criteria"]
                    elif "criteria_weights" in evaluation_data:
                        # Extract criteria names from criteria_weights
                        evaluation_config["criteria"] = list(
                            evaluation_data["criteria_weights"].keys()
                        )
                    if "scoring_scale" in evaluation_data:
                        evaluation_config["scoring_scale"] = evaluation_data[
                            "scoring_scale"
                        ]
                    elif "use_structured_output" in evaluation_data:
                        # Default scoring scale
                        evaluation_config["scoring_scale"] = 10
                    if "temperature" in evaluation_data:
                        evaluation_config["temperature"] = evaluation_data[
                            "temperature"
                        ]

                    # Use extracted config or fall back to defaults
                    if evaluation_config:
                        data["evaluation"] = EvaluationConfig(**evaluation_config)
                    else:
                        data["evaluation"] = EvaluationConfig()
                else:
                    data["evaluation"] = EvaluationConfig(**evaluation_data)
            # Handle provider config
            if "provider" in data:
                provider_data = data["provider"]
                if isinstance(provider_data, dict):
                    # Extract only the fields that ProviderConfig expects
                    provider_config = {}
                    expected_fields = {
                        "provider_type",
                        "ollama_host",
                        "vllm_url",
                        "vllm_model",
                        "openrouter_url",
                        "openrouter_model",
                        "openrouter_api_key",
                        "openrouter_requests_per_minute",
                        "gemini_api_key",
                        "timeout",
                    }
                    for key, value in provider_data.items():
                        if key in expected_fields:
                            provider_config[key] = value

                    data["provider"] = ProviderConfig(**provider_config)
                else:
                    data["provider"] = ProviderConfig(**provider_data)

            # Handle project config
            if "projects" in data:
                project_data = data["projects"]
                if isinstance(project_data, dict):
                    # Extract only the fields that ProjectConfig expects
                    project_config = {}
                    expected_fields = {
                        "work_dir",
                        "node_version",
                        "supported_frameworks",
                        "default_ports",
                        "install_timeout",
                        "build_timeout",
                        "server_start_timeout",
                        "cleanup_on_exit",
                    }
                    for key, value in project_data.items():
                        if key in expected_fields:
                            project_config[key] = value

                    data["projects"] = ProjectConfig(**project_config)
                else:
                    data["projects"] = ProjectConfig(**project_data)

            # Filter out unknown fields that don't belong to the Config class
            config_fields = {
                "models",
                "tasks",
                "iterations",
                "judges",
                "mode",
                "resume_from",
                "output_dir",
                "save_intermediate",
                "compress_logs",
                "rendering",
                "projects",
                "evaluation",
                "provider",
                "max_concurrent_models",
                "memory_threshold",
                "log_level",
            }
            filtered_data = {k: v for k, v in data.items() if k in config_fields}

            return cls(**filtered_data)
        except Exception as e:
            raise ValueError(f"Failed to create config from dict: {e}")

    def to_yaml(self, yaml_path: str):
        """Save configuration to YAML file."""
        try:
            data = self.to_dict()
            with open(yaml_path, "w") as f:
                yaml.dump(data, f, default_flow_style=False, indent=2)
        except Exception as e:
            raise ValueError(f"Failed to save config to {yaml_path}: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        data = {}
        # Convert models
        data["models"] = []
        for model in self.models:
            data["models"].append(
                {
                    "name": model.name,
                    "temperature": model.temperature,
                    "num_ctx": model.num_ctx,
                    "num_predict": model.num_predict,
                    "timeout": model.timeout,
                    "max_retries": model.max_retries,
                }
            )
        # Convert tasks
        data["tasks"] = []
        for task in self.tasks:
            # Handle both TaskConfig and TaskDefinition objects
            if hasattr(task, "prompt_template"):
                # This is a TaskConfig object
                data["tasks"].append(
                    {
                        "name": task.name,
                        "description": task.description,
                        "prompt_template": task.prompt_template,
                        "expected_elements": getattr(task, "expected_elements", []),
                        "difficulty": getattr(task, "difficulty", "medium"),
                        "project_type": getattr(task, "project_type", "html"),
                        "framework_version": getattr(task, "framework_version", None),
                    }
                )
            else:
                # This is a TaskDefinition object
                data["tasks"].append(
                    {
                        "name": task.name,
                        "description": task.description,
                        "prompt_template": task.prompt,
                        "expected_elements": task.expected_features,
                        "difficulty": (
                            task.difficulty.value
                            if hasattr(task.difficulty, "value")
                            else str(task.difficulty)
                        ),
                        "project_type": task.project_type,
                        "framework_version": task.framework_version,
                    }
                )
        # Add other fields
        data.update(
            {
                "iterations": self.iterations,
                "judges": self.judges,
                "mode": self.mode,
                "resume_from": self.resume_from,
                "output_dir": self.output_dir,
                "save_intermediate": self.save_intermediate,
                "compress_logs": self.compress_logs,
                "max_concurrent_models": self.max_concurrent_models,
                "memory_threshold": self.memory_threshold,
                "log_level": self.log_level,
            }
        )
        # Add rendering config
        data["rendering"] = {
            "viewport_width": self.rendering.viewport_width,
            "viewport_height": self.rendering.viewport_height,
            "wait_time": self.rendering.wait_time,
            "screenshot_format": self.rendering.screenshot_format,
            "headless": self.rendering.headless,
            "timeout": self.rendering.timeout,
        }
        # Add project config
        data["projects"] = {
            "work_dir": self.projects.work_dir,
            "node_version": self.projects.node_version,
            "supported_frameworks": self.projects.supported_frameworks,
            "default_ports": self.projects.default_ports,
            "install_timeout": self.projects.install_timeout,
            "build_timeout": self.projects.build_timeout,
            "server_start_timeout": self.projects.server_start_timeout,
            "cleanup_on_exit": self.projects.cleanup_on_exit,
        }
        # Add evaluation config
        data["evaluation"] = {
            "judge_models": self.evaluation.judge_models,
            "criteria": self.evaluation.criteria,
            "scoring_scale": self.evaluation.scoring_scale,
            "temperature": self.evaluation.temperature,
        }
        # Add provider config
        data["provider"] = {
            "provider_type": self.provider.provider_type,
            "ollama_host": self.provider.ollama_host,
            "vllm_url": self.provider.vllm_url,
            "vllm_model": self.provider.vllm_model,
            "openrouter_url": self.provider.openrouter_url,
            "openrouter_model": self.provider.openrouter_model,
            "openrouter_api_key": self.provider.openrouter_api_key,
            "openrouter_requests_per_minute": self.provider.openrouter_requests_per_minute,
            "timeout": self.provider.timeout,
        }
        return data

    def apply_env_overrides(self):
        """Apply environment variable overrides."""
        # Model settings
        if os.getenv("BENCHMARK_TEMPERATURE"):
            temp = float(os.getenv("BENCHMARK_TEMPERATURE"))
            for model in self.models:
                model.temperature = temp
        if os.getenv("BENCHMARK_NUM_CTX"):
            ctx = int(os.getenv("BENCHMARK_NUM_CTX"))
            for model in self.models:
                model.num_ctx = ctx
        # Pipeline settings
        if os.getenv("BENCHMARK_ITERATIONS"):
            self.iterations = int(os.getenv("BENCHMARK_ITERATIONS"))
        if os.getenv("BENCHMARK_MODE"):
            self.mode = os.getenv("BENCHMARK_MODE")
        if os.getenv("BENCHMARK_OUTPUT_DIR"):
            self.output_dir = os.getenv("BENCHMARK_OUTPUT_DIR")
        if os.getenv("BENCHMARK_LOG_LEVEL"):
            self.log_level = os.getenv("BENCHMARK_LOG_LEVEL")

        # Provider settings
        if os.getenv("LLM_PROVIDER"):
            self.provider.provider_type = os.getenv("LLM_PROVIDER")
        if os.getenv("OLLAMA_HOST"):
            self.provider.ollama_host = os.getenv("OLLAMA_HOST")
        if os.getenv("VLLM_URL"):
            self.provider.vllm_url = os.getenv("VLLM_URL")
        if os.getenv("VLLM_MODEL"):
            self.provider.vllm_model = os.getenv("VLLM_MODEL")
        if os.getenv("OPENROUTER_URL"):
            self.provider.openrouter_url = os.getenv("OPENROUTER_URL")
        if os.getenv("OPENROUTER_MODEL"):
            self.provider.openrouter_model = os.getenv("OPENROUTER_MODEL")
        if os.getenv("OPENROUTER_API_KEY"):
            self.provider.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        if os.getenv("OPENROUTER_REQUESTS_PER_MINUTE"):
            self.provider.openrouter_requests_per_minute = int(
                os.getenv("OPENROUTER_REQUESTS_PER_MINUTE")
            )

    def validate(self):
        """Validate configuration settings."""
        # Validate models
        if not self.models:
            raise ValueError("At least one model must be specified")
        for model in self.models:
            if not model.name:
                raise ValueError("Model name cannot be empty")
            if not 0 <= model.temperature <= 1:
                raise ValueError(
                    f"Model temperature must be between 0 and 1, got {model.temperature}"
                )
        # Validate tasks
        if not self.tasks:
            raise ValueError("At least one task must be specified")
        for task in self.tasks:
            if not task.name or not task.prompt_template:
                raise ValueError("Task name and prompt_template are required")
        # Validate iterations
        if self.iterations < 1:
            raise ValueError("Iterations must be at least 1")
        # Validate mode
        valid_modes = ["generation-only", "judging-only", "full-pipeline"]
        if self.mode not in valid_modes:
            raise ValueError(f"Mode must be one of {valid_modes}")
        # Validate output directory
        if not self.output_dir:
            raise ValueError("Output directory cannot be empty")
        # Create output directory if it doesn't exist
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
