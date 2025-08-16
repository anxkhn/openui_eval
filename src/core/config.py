"""Configuration management for the benchmark system."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


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

    provider_type: str = "ollama"  # ollama, vllm, openrouter

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
    tasks: List[TaskConfig] = field(
        default_factory=lambda: [
            TaskConfig(
                name="responsive_calculator",
                description="Create a responsive calculator with modern UI",
                prompt_template="""Create a sophisticated, responsive calculator with modern UI design.
**Instructions:**
- The entire output must be a single HTML file with all CSS and JavaScript inline.
- Design a sleek, modern calculator interface with a dark theme using gradients of charcoal and deep blue.
- Include all basic arithmetic operations (+, -, *, /), number buttons (0-9), decimal point, equals, and clear/all-clear buttons.
- The display should be large and clearly readable with a subtle inner shadow effect showing "0" or a sample calculation.
- Style buttons with modern design - subtle gradients, proper spacing, and professional appearance.
- The calculator should be fully responsive, adapting beautifully from mobile (320px) to desktop (1200px+) screens.
- Use a clean, modern font like 'Segoe UI' or similar system fonts.
- Focus on visual design excellence - proper button sizing, consistent spacing, and professional color scheme.
- The layout should be intuitive with a clear visual hierarchy between display, numbers, and operations.""",
            ),
            TaskConfig(
                name="google_search_clone",
                description="Create a Google Search bar clone",
                prompt_template="""Create a pixel-perfect Google Search homepage clone with authentic styling.
**Instructions:**
- The entire output must be a single HTML file with all CSS and JavaScript inline.
- Replicate Google's clean, minimalist homepage design with accurate spacing, colors, and typography.
- Include the Google logo (use text-based logo with authentic colors), centered search input field, and both 'Google Search' and 'I'm Feeling Lucky' buttons.
- The search bar should have Google's characteristic rounded corners, subtle shadow, and proper styling.
- Style buttons to match Google's actual appearance with proper colors and spacing.
- Add the characteristic grid of apps icon in the top-right corner and Gmail/Images links.
- Include Google's footer with links like 'About', 'Advertising', 'Privacy', 'Terms', etc.
- The page must be fully responsive and maintain Google's clean aesthetic on all screen sizes.
- Include the microphone icon in the search bar with proper positioning.
- Focus on achieving pixel-perfect visual accuracy to Google's actual homepage design.""",
            ),
            TaskConfig(
                name="book_review_website",
                description="Create a book review website",
                prompt_template="""Create a comprehensive book review website with elegant design.
**Instructions:**
- The entire output must be a single HTML file with all CSS and JavaScript inline.
- Design a warm, literary-themed layout using a sophisticated color palette of deep burgundy, cream, and gold accents.
- Include a header with navigation (Home, Reviews, Genres, About, Contact), hero section with featured book of the month.
- Create sections for: Recent Reviews (with book covers, ratings, and excerpts), Top Rated Books, Browse by Genre, and Featured Authors.
- Each book review card should include: book cover placeholder, title, author, star rating display (★★★★☆), review excerpt, and 'Read Full Review' button.
- Display star ratings using visual star symbols or styled elements.
- Use elegant typography with serif fonts for headings and clean sans-serif for body text.
- Include a search bar and filter options display (by genre, rating, author) with proper styling.
- Add a newsletter signup section with attractive form styling.
- The design must be fully responsive with professional layout and visual hierarchy.
- Include book genre tags with color-coded styling for visual appeal.""",
            ),
            TaskConfig(
                name="portfolio_website",
                description="Create a portfolio website",
                prompt_template="""Create a stunning, professional portfolio website for a web developer with modern design.
**Instructions:**
- The entire output must be a single HTML file with all CSS and JavaScript inline.
- Design a modern, dark-themed portfolio with a sophisticated color scheme of deep navy, electric blue accents, and white text.
- Include a fixed navigation header with clean menu items linking to sections.
- Hero section: Large name/title, professional photo placeholder, role description text, and compelling call-to-action button.
- About section: Personal story, professional journey, and key achievements with professional layout.
- Skills section: Visual skill bars showing percentages, technology icons, and organized skill categories.
- Projects section: Grid of project cards with image placeholders, descriptions, tech stack tags, and 'View Project' buttons.
- Contact section: Professional contact form with proper styling and social media links with icons.
- Footer: Additional links and copyright information.
- Focus on professional visual design, proper spacing, and clear visual hierarchy throughout.
- The site must be fully responsive with mobile-first design approach.
- Include a theme toggle button (dark/light) with proper styling.""",
            ),
            TaskConfig(
                name="todo_list_app",
                description="Create a todo list application",
                prompt_template="""Create a feature-rich, modern todo list application with beautiful UI design.
**Instructions:**
- The entire output must be a single HTML file with all CSS and JavaScript inline.
- Design a clean, modern interface with a light theme using soft blues, whites, and subtle gray accents.
- Include a header with app title, add-new-task input field, and task statistics display.
- Show sample tasks in different states: active tasks, completed tasks (with strikethrough), and various priority levels.
- Display task filtering options: All, Active, Completed buttons with proper styling.
- Include a search bar with proper styling for task filtering.
- Show tasks with priority levels (High, Medium, Low) using color-coded indicators.
- Display due dates and show some tasks as overdue with visual indicators.
- Include task categories/tags with color coding for visual organization.
- Show edit and delete buttons for each task with proper icon styling.
- Design task items with checkboxes, task text, priority indicators, and action buttons.
- The app must be fully responsive with mobile-friendly layout and touch-friendly button sizes.""",
            ),
            TaskConfig(
                name="modern_landing_page",
                description="A dark-themed, futuristic landing page for a SaaS product",
                prompt_template="""Design a visually striking landing page for a fictional SaaS product called 'SynthWave'.
**Instructions:**
- The entire output must be a single HTML file with all CSS and JavaScript inline.
- The design should be dark-themed, using a palette of deep purples, electric blues, and neon pinks.
- Use a bold, futuristic font for the main headline and a clean, readable sans-serif font for the body text.
- The layout should be a single, centered column.
- It must include a hero section with the product name 'SynthWave' and a prominent call-to-action button.
- Add three distinct sections below the hero: 'Features', 'Pricing', and a simple 'Contact' layout.
- Style the call-to-action button with a subtle glowing effect and modern design.
- Ensure the page is fully responsive and looks polished on mobile, tablet, and desktop screens.""",
            ),
            TaskConfig(
                name="minimalist_blog_layout",
                description="A clean, minimalist, and content-focused blog layout",
                prompt_template="""Create the layout for a minimalist and elegant blog.
**Instructions:**
- The entire output must be a single HTML file with all CSS and JavaScript inline.
- The design must be clean and content-focused, with a light color scheme (primarily white and light gray) and a single accent color for links.
- Use a classic, highly readable serif font for the blog post body and a modern sans-serif for headings.
- The layout should feature a simple header with the blog's title, a main content area with a placeholder title and text for a single blog post, and a minimal footer.
- The page must be fully responsive, with typography and spacing that adapt beautifully to different screen sizes.""",
            ),
            TaskConfig(
                name="ecommerce_product_page",
                description="An elegant and luxurious product page for a high-end watch",
                prompt_template="""Construct a product detail page for a high-end wristwatch.
**Instructions:**
- The entire output must be a single HTML file with all CSS and JavaScript inline.
- The visual style should be luxurious and elegant, using a sophisticated color palette (e.g., charcoal, gold, and off-white).
- On a desktop, the layout should be a two-column grid: the left for a product image placeholder and the right for the watch's name, a short description, the price, and an 'Add to Cart' button.
- On mobile devices, these two columns should stack vertically.
- Use a classic serif font for headings and a clean sans-serif for body text.
- The 'Add to Cart' button should have a premium look with a subtle animation on click.
- The page must be fully responsive.""",
            ),
            TaskConfig(
                name="travel_website_hero",
                description="An immersive and visually beautiful hero section for a travel website",
                prompt_template="""Design a visually immersive hero section for a travel website.
**Instructions:**
- The entire output must be a single HTML file with all CSS and JavaScript inline.
- The design should evoke a sense of adventure, using a vibrant color scheme inspired by nature (e.g., deep blues, lush greens).
- The layout should feature a large, bold, and inspiring headline font over a placeholder for a full-width background image.
- A clean and modern search bar for destinations should be centered over the background.
- The entire section must be fully responsive, ensuring the text is always readable and the layout is well-balanced on all devices.""",
            ),
            TaskConfig(
                name="photography_portfolio_gallery",
                description="A minimalist, image-focused gallery for a photography portfolio",
                prompt_template="""Create a gallery page for a photography portfolio.
**Instructions:**
- The entire output must be a single HTML file with all CSS and JavaScript inline.
- The design should be image-centric and minimalist, with a dark background to make the (placeholder) images stand out.
- The gallery should be a responsive grid of placeholders for photos.
- On hover, each placeholder should have a subtle zoom effect.
- The page needs a simple header with the photographer's name and a footer with social media icon placeholders.
- The grid layout must be fluid, adapting from a single column on mobile to multiple columns on wider screens.""",
            ),
            TaskConfig(
                name="recipe_card_display",
                description="A warm and inviting, well-organized recipe card",
                prompt_template="""Design a single, visually appealing recipe card as a web page.
**Instructions:**
- The entire output must be a single HTML file with all CSS and JavaScript inline.
- The style should be warm and inviting, using a color palette reminiscent of a kitchen (e.g., warm browns, creamy whites, a splash of herbal green).
- The layout should be well-organized with clear sections for the recipe title, a short description, an ingredients list, and step-by-step instructions.
- Use a charming, slightly rustic font for headings and a clear, legible font for the body.
- The page must be fully responsive, so the recipe is easy to read on a phone or a larger screen.""",
            ),
            TaskConfig(
                name="event_announcement_page",
                description="A modern and stylish announcement page for a virtual tech conference",
                prompt_template="""Create a stylish announcement page for a virtual tech conference.
**Instructions:**
- The entire output must be a single HTML file with all CSS and JavaScript inline.
- The design should be modern and tech-savvy, with a dark theme that uses gradients of blue and purple.
- The typography should be clean and futuristic.
- The page should have a prominent headline with the event name and date.
- Below the headline, include sections for a keynote speaker (with a placeholder for their photo and bio) and a large 'Register Now' button.
- The 'Register Now' button should be a focal point with an eye-catching hover effect.
- The layout must be fully responsive and look professional on all devices.""",
            ),
        ]
    )
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
                    # Legacy format with just task names - use default tasks
                    task_names = data["tasks"]["task_names"]
                    # Filter default tasks to only include the specified ones
                    default_config = cls()
                    filtered_tasks = [
                        task for task in default_config.tasks if task.name in task_names
                    ]
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
            data["tasks"].append(
                {
                    "name": task.name,
                    "description": task.description,
                    "prompt_template": task.prompt_template,
                    "expected_elements": task.expected_elements,
                    "difficulty": task.difficulty,
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
