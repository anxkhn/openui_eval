"""Multi-file project generator with iterative improvement capabilities."""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.config import TaskConfig
from core.logger import get_logger
from frameworks.framework_factory import FrameworkFactory
from models.model_manager import ModelManager
from rendering.node_renderer import NodeProjectRenderer
from generation.html_processor import HTMLProcessor


class ProjectGenerator:
    """Generates multi-file projects with iterative improvement using visual feedback."""

    def __init__(self, model_manager: ModelManager, output_dir: str = "results"):
        self.model_manager = model_manager
        self.output_dir = Path(output_dir)
        self.html_processor = HTMLProcessor()
        self.logger = get_logger()

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_initial_project(
        self, model_name: str, task: TaskConfig, framework: str
    ) -> Dict[str, Any]:
        """
        Generate initial project files for a framework.

        Args:
            model_name: Name of the model to use
            task: Task configuration
            framework: Framework name (react, vue, etc.)

        Returns:
            Dictionary with generation results
        """
        try:
            self.logger.log_task_operation(
                "generate_initial_project", task.name, iteration=1
            )

            # Clear any existing conversation history for this model
            self.model_manager.clear_conversation(model_name)

            # Create framework-specific prompt
            framework_prompt = self._create_framework_prompt(task, framework)

            # Generate initial response
            start_time = time.time()
            response = self.model_manager.generate(
                model_name=model_name, prompt=framework_prompt
            )
            duration = time.time() - start_time

            # Extract project files from response
            project_files = self._extract_project_files(response["content"], framework)

            if not project_files:
                raise ValueError("No valid project files found in model response")

            # Prepare result
            result = {
                "iteration": 1,
                "model_name": model_name,
                "task_name": task.name,
                "framework": framework,
                "timestamp": datetime.now().isoformat(),
                "project_files": project_files,
                "raw_response": response["content"],
                "generation_duration": duration,
                "model_stats": response,
                "success": len(project_files) > 0,
                "file_count": len(project_files),
            }

            self.logger.log_task_operation(
                "generate_initial_project_complete",
                task.name,
                iteration=1,
                duration=duration,
                success=result["success"],
                file_count=len(project_files),
            )

            return result

        except Exception as e:
            error_msg = f"Failed to generate initial project for {task.name} with {model_name} ({framework}): {e}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

    def improve_project(
        self,
        model_name: str,
        task: TaskConfig,
        framework: str,
        iteration: int,
        previous_files: Dict[str, str],
        screenshot_path: str,
    ) -> Dict[str, Any]:
        """
        Improve project based on visual feedback from screenshot.

        Args:
            model_name: Name of the model to use
            task: Task configuration
            framework: Framework name
            iteration: Current iteration number
            previous_files: Previous project files
            screenshot_path: Path to screenshot of previous project

        Returns:
            Dictionary with improvement results
        """
        try:
            self.logger.log_task_operation(
                "improve_project", task.name, iteration=iteration
            )

            # Create improvement prompt
            improvement_prompt = self._create_improvement_prompt(
                task, framework, iteration, previous_files
            )

            # Generate improved project using conversation history and screenshot
            start_time = time.time()
            response = self.model_manager.generate_with_conversation(
                model_name=model_name,
                prompt=improvement_prompt,
                image_path=screenshot_path,
            )
            duration = time.time() - start_time

            # Extract project files from response
            project_files = self._extract_project_files(response["content"], framework)

            if not project_files:
                self.logger.warning(
                    f"No project files found in improvement iteration {iteration}, using previous files"
                )
                project_files = previous_files

            # Prepare result
            result = {
                "iteration": iteration,
                "model_name": model_name,
                "task_name": task.name,
                "framework": framework,
                "timestamp": datetime.now().isoformat(),
                "project_files": project_files,
                "raw_response": response["content"],
                "generation_duration": duration,
                "model_stats": response,
                "screenshot_path": screenshot_path,
                "success": len(project_files) > 0,
                "file_count": len(project_files),
                "improvement_prompt": improvement_prompt,
            }

            self.logger.log_task_operation(
                "improve_project_complete",
                task.name,
                iteration=iteration,
                duration=duration,
                success=result["success"],
                file_count=len(project_files),
            )

            return result

        except Exception as e:
            error_msg = f"Failed to improve project for {task.name} iteration {iteration} with {model_name} ({framework}): {e}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

    def generate_complete_project(
        self,
        model_name: str,
        task: TaskConfig,
        framework: str,
        iterations: int = 3,
        renderer: Optional[NodeProjectRenderer] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate complete project with all iterations.

        Args:
            model_name: Name of the model to use
            task: Task configuration
            framework: Framework name
            iterations: Number of iterations to perform
            renderer: Node project renderer for screenshots (optional)

        Returns:
            List of generation results for each iteration
        """
        try:
            self.logger.info(
                f"Starting complete project generation: {task.name} with {model_name} ({framework})"
            )

            results = []
            current_files = None

            # Create task output directory
            task_dir = (
                self.output_dir
                / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                / model_name
                / f"{task.name}_{framework}"
            )
            task_dir.mkdir(parents=True, exist_ok=True)

            for iteration in range(1, iterations + 1):
                self.logger.info(
                    f"Starting iteration {iteration}/{iterations} for {task.name} ({framework})"
                )

                if iteration == 1:
                    # Generate initial project
                    result = self.generate_initial_project(model_name, task, framework)
                else:
                    # Improve based on previous iteration
                    if not current_files:
                        raise RuntimeError("No project files available for improvement")

                    # Get screenshot path from previous iteration
                    prev_result = results[-1]
                    screenshot_path = prev_result.get(
                        "llm_screenshot_path"
                    ) or prev_result.get("screenshot_path")

                    if not screenshot_path:
                        self.logger.warning(
                            f"No screenshot available for iteration {iteration}, skipping improvement"
                        )
                        break

                    result = self.improve_project(
                        model_name,
                        task,
                        framework,
                        iteration,
                        current_files,
                        screenshot_path,
                    )

                # Save project files
                project_name = f"v{iteration}"
                project_path = task_dir / project_name

                # Create project using framework generator
                if renderer:
                    try:
                        # Render the project and capture screenshot
                        render_result = renderer.render_project(
                            framework=framework,
                            project_name=f"{task.name}_{framework}_v{iteration}",
                            task_description=task.description,
                            generated_content=result["project_files"],
                            screenshot_path=str(
                                task_dir / f"v{iteration}_screenshot.png"
                            ),
                        )

                        if render_result["success"]:
                            result["project_path"] = render_result["project_dir"]
                            result["screenshot_path"] = render_result[
                                "full_screenshot_path"
                            ]
                            result["llm_screenshot_path"] = render_result[
                                "llm_screenshot_path"
                            ]
                            result["server_url"] = render_result["server_url"]
                            self.logger.info(
                                f"Project rendered successfully: {render_result['server_url']}"
                            )
                        else:
                            self.logger.warning(
                                f"Failed to render project: {render_result.get('error')}"
                            )

                    except Exception as e:
                        self.logger.error(
                            f"Error rendering project for iteration {iteration}: {e}"
                        )

                # Save project files to disk for reference
                files_dir = task_dir / f"v{iteration}_files"
                files_dir.mkdir(exist_ok=True)

                for file_path, content in result["project_files"].items():
                    full_path = files_dir / file_path
                    full_path.parent.mkdir(parents=True, exist_ok=True)

                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(content)

                # Save metadata
                metadata_path = task_dir / f"v{iteration}_metadata.json"
                with open(metadata_path, "w") as f:
                    # Create a copy without the project files for metadata
                    metadata = {k: v for k, v in result.items() if k != "project_files"}
                    json.dump(metadata, f, indent=2, default=str)

                result["metadata_path"] = str(metadata_path)
                result["files_dir"] = str(files_dir)

                results.append(result)
                current_files = result["project_files"]

                self.logger.info(
                    f"Completed iteration {iteration}/{iterations} for {task.name} ({framework})"
                )

            # Save complete results summary
            summary_path = task_dir / "summary.json"
            summary = {
                "task_name": task.name,
                "model_name": model_name,
                "framework": framework,
                "total_iterations": len(results),
                "start_time": results[0]["timestamp"] if results else None,
                "end_time": results[-1]["timestamp"] if results else None,
                "total_duration": sum(r["generation_duration"] for r in results),
                "final_success": results[-1]["success"] if results else False,
                "iterations": [
                    {
                        "iteration": r["iteration"],
                        "success": r["success"],
                        "duration": r["generation_duration"],
                        "file_count": r["file_count"],
                    }
                    for r in results
                ],
            }

            with open(summary_path, "w") as f:
                json.dump(summary, f, indent=2, default=str)

            self.logger.info(
                f"Completed project generation: {task.name} with {model_name} ({framework})"
            )

            return results

        except Exception as e:
            error_msg = f"Failed to generate complete project {task.name} with {model_name} ({framework}): {e}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

    def _create_framework_prompt(self, task: TaskConfig, framework: str) -> str:
        """Create framework-specific prompt for project generation."""
        framework_info = FrameworkFactory.get_framework_info(framework)

        base_prompt = f"""Create a complete {framework} {framework_info['version']} application for the following task:

{task.prompt}

**Important Instructions:**
- Generate a complete, working {framework} application with all necessary files
- Use {framework} {framework_info['version']} and the latest best practices
- Ensure the application is responsive and works on both desktop and mobile
- Include proper error handling and user feedback
- Use modern {framework} patterns and hooks/composition API where applicable
- Make sure all files are properly structured and follow {framework} conventions

**Required Output Format:**
Please provide the complete project files in the following format:

```filename: path/to/file.ext
file content here
```

Make sure to include:
1. All component files needed for the application
2. Proper styling (CSS/SCSS or styled-components)
3. Any utility functions or services
4. Configuration files if needed
5. Main entry point and routing (if applicable)

Focus on creating a polished, production-ready application that fully meets the task requirements."""

        return base_prompt

    def _create_improvement_prompt(
        self,
        task: TaskConfig,
        framework: str,
        iteration: int,
        previous_files: Dict[str, str],
    ) -> str:
        """Create improvement prompt for iterative refinement."""

        file_list = "\n".join([f"- {path}" for path in previous_files.keys()])

        base_prompt = f"""This is iteration {iteration}. You are provided with the previous {framework} application's visual output. Please analyze the screenshot and improve the application based on what you see.

**Current Project Files:**
{file_list}

**Original Task:**
{task.description}

**Analysis and Improvement Guidelines:**
1. **Visual Issues**: Fix any layout problems, styling inconsistencies, or visual bugs you can see
2. **User Experience**: Improve usability, accessibility, and overall user experience
3. **Responsiveness**: Ensure the design works well on different screen sizes
4. **Functionality**: Add missing features or fix broken functionality
5. **Code Quality**: Improve code organization, performance, and maintainability
6. **{framework} Best Practices**: Use the latest {framework} patterns and conventions

**Output Format:**
Please provide the updated project files in the following format:

```filename: path/to/file.ext
updated file content here
```

Only include files that need to be changed or added. If a file doesn't need changes, you don't need to include it.

Look carefully at the screenshot and make specific improvements based on what you observe. Focus on creating a polished, professional application that fully meets the original task requirements."""

        return base_prompt

    def _extract_project_files(self, response: str, framework: str) -> Dict[str, str]:
        """
        Extract project files from model response.

        Args:
            response: Model response text
            framework: Framework name for validation

        Returns:
            Dictionary mapping file paths to contents
        """
        project_files = {}

        # Look for code blocks with filename patterns
        import re

        # Pattern to match code blocks with filenames
        pattern = r"```(?:filename:\s*)?([^\n]+)\n(.*?)```"
        matches = re.findall(pattern, response, re.DOTALL)

        for filename, content in matches:
            # Clean up filename
            filename = filename.strip()
            # Remove any "filename:" prefix if present
            if filename.startswith("filename:"):
                filename = filename[9:].strip()

            # Clean up content
            content = content.strip()

            # Skip empty files
            if not content:
                continue

            project_files[filename] = content

        # If no code blocks found, try to extract from different patterns
        if not project_files:
            # Try alternative patterns
            alt_patterns = [
                r"```([^`]+)```",  # Simple code blocks
                r"File: ([^\n]+)\n```[^\n]*\n(.*?)```",  # File: prefix pattern
            ]

            for pattern in alt_patterns:
                matches = re.findall(pattern, response, re.DOTALL)
                for match in matches:
                    if len(match) == 2:
                        filename, content = match
                        filename = filename.strip()
                        content = content.strip()
                        if content and self._is_valid_filename(filename):
                            project_files[filename] = content

        # Validate files for framework
        validated_files = self._validate_framework_files(project_files, framework)

        return validated_files

    def _is_valid_filename(self, filename: str) -> bool:
        """Check if filename looks like a valid file path."""
        # Basic validation
        return (
            filename
            and not filename.startswith("```")
            and ("." in filename or "/" in filename)
            and len(filename) < 200
        )

    def _validate_framework_files(
        self, files: Dict[str, str], framework: str
    ) -> Dict[str, str]:
        """
        Validate files for specific framework requirements.

        Args:
            files: Project files
            framework: Framework name

        Returns:
            Validated files (may add missing files)
        """
        validated_files = files.copy()

        # Framework-specific validation and auto-generation
        framework_instance = FrameworkFactory.create_framework(framework)

        # Get required files from template
        template_files = framework_instance.get_project_template()

        # Add missing critical files
        for template_file, template_content in template_files.items():
            if template_file not in validated_files:
                # Only add critical files automatically
                critical_files = [
                    "package.json",
                    ".gitignore",
                    "README.md",
                ]

                if any(critical in template_file for critical in critical_files):
                    validated_files[template_file] = template_content
                    self.logger.debug(f"Added missing critical file: {template_file}")

        return validated_files

    def get_generation_stats(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics from generation results."""
        if not results:
            return {}

        total_duration = sum(r["generation_duration"] for r in results)
        successful_iterations = sum(1 for r in results if r["success"])
        file_counts = [r["file_count"] for r in results]

        return {
            "total_iterations": len(results),
            "successful_iterations": successful_iterations,
            "success_rate": successful_iterations / len(results),
            "total_duration": total_duration,
            "average_duration": total_duration / len(results),
            "file_count_progression": file_counts,
            "final_file_count": file_counts[-1] if file_counts else 0,
            "task_name": results[0]["task_name"],
            "model_name": results[0]["model_name"],
            "framework": results[0]["framework"],
        }
