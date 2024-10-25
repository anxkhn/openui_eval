"""HTML generator with iterative improvement capabilities."""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from core.config import TaskConfig
from core.logger import get_logger
from models.model_manager import ModelManager
from generation.html_processor import HTMLProcessor


class HTMLGenerator:
    """Generates HTML content with iterative improvement using visual feedback."""

    def __init__(self, model_manager: ModelManager, output_dir: str = "results"):
        self.model_manager = model_manager
        self.output_dir = Path(output_dir)
        self.html_processor = HTMLProcessor()
        self.logger = get_logger()
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_initial_html(
        self, model_name: str, task: TaskConfig
    ) -> Dict[str, Any]:
        """
        Generate initial HTML for a task.
        Args:
            model_name: Name of the model to use
            task: Task configuration
        Returns:
            Dictionary with generation results
        """
        try:
            self.logger.log_task_operation("generate_initial", task.name, iteration=1)
            # Clear any existing conversation history for this model
            self.model_manager.clear_conversation(model_name)
            # Generate initial response
            start_time = time.time()
            response = self.model_manager.generate(
                model_name=model_name, prompt=task.prompt
            )
            duration = time.time() - start_time
            # Extract HTML from response
            html_content = self.html_processor.extract_html(response["content"])
            if not html_content:
                raise ValueError("No valid HTML found in model response")
            # Validate HTML
            validation_results = self.html_processor.validate_html(html_content)
            html_stats = self.html_processor.get_html_stats(html_content)
            # Prepare result
            result = {
                "iteration": 1,
                "model_name": model_name,
                "task_name": task.name,
                "timestamp": datetime.now().isoformat(),
                "html_content": html_content,
                "raw_response": response["content"],
                "generation_duration": duration,
                "model_stats": response,
                "validation_results": validation_results,
                "html_stats": html_stats,
                "success": validation_results["is_valid"],
            }
            self.logger.log_task_operation(
                "generate_initial_complete",
                task.name,
                iteration=1,
                duration=duration,
                success=result["success"],
                html_size=len(html_content),
            )
            return result
        except Exception as e:
            error_msg = f"Failed to generate initial HTML for {task.name} with {model_name}: {e}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

    def improve_html(
        self,
        model_name: str,
        task: TaskConfig,
        iteration: int,
        previous_html: str,
        screenshot_path: str,
    ) -> Dict[str, Any]:
        """
        Improve HTML based on visual feedback from screenshot.
        Args:
            model_name: Name of the model to use
            task: Task configuration
            iteration: Current iteration number
            previous_html: Previous HTML content
            screenshot_path: Path to screenshot of previous HTML
        Returns:
            Dictionary with improvement results
        """
        try:
            self.logger.log_task_operation(
                "improve_html", task.name, iteration=iteration
            )
            # Create improvement prompt
            improvement_prompt = self._create_improvement_prompt(task, iteration)
            # Generate improved HTML using conversation history and screenshot
            start_time = time.time()
            response = self.model_manager.generate_with_conversation(
                model_name=model_name,
                prompt=improvement_prompt,
                image_path=screenshot_path,
            )
            duration = time.time() - start_time
            # Extract HTML from response
            html_content = self.html_processor.extract_html(response["content"])
            if not html_content:
                self.logger.warning(
                    f"No HTML found in improvement iteration {iteration}, using previous HTML"
                )
                html_content = previous_html
            # Validate HTML
            validation_results = self.html_processor.validate_html(html_content)
            html_stats = self.html_processor.get_html_stats(html_content)
            # Prepare result
            result = {
                "iteration": iteration,
                "model_name": model_name,
                "task_name": task.name,
                "timestamp": datetime.now().isoformat(),
                "html_content": html_content,
                "raw_response": response["content"],
                "generation_duration": duration,
                "model_stats": response,
                "validation_results": validation_results,
                "html_stats": html_stats,
                "screenshot_path": screenshot_path,
                "success": validation_results["is_valid"],
                "improvement_prompt": improvement_prompt,
            }
            self.logger.log_task_operation(
                "improve_html_complete",
                task.name,
                iteration=iteration,
                duration=duration,
                success=result["success"],
                html_size=len(html_content),
            )
            return result
        except Exception as e:
            error_msg = f"Failed to improve HTML for {task.name} iteration {iteration} with {model_name}: {e}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

    def _create_improvement_prompt(self, task: TaskConfig, iteration: int) -> str:
        """Create improvement prompt for iterative refinement."""
        base_prompt = f"""This is iteration {iteration}. You are provided with the previous code's visual output. Please use this to analyze and self improve and meet the previously requested requirements.
Look at the screenshot of your previous HTML output and improve the code based on what you see. Focus on:
1. **Visual Issues**: Fix any layout problems, styling issues, or visual inconsistencies
2. **Responsiveness**: Ensure the design works well on different screen sizes
3. **User Experience**: Improve usability, accessibility, and overall user experience
4. **Code Quality**: Clean up the HTML, CSS, and JavaScript code
5. **Task Requirements**: Make sure all requirements from the original task are met
Original task: {task.description}
Please provide the complete improved HTML code with inline CSS and JavaScript. Make sure the code is clean, well-structured, and addresses any issues you can see in the screenshot."""
        return base_prompt

    def generate_complete_task(
        self, model_name: str, task: TaskConfig, iterations: int = 3, renderer=None
    ) -> List[Dict[str, Any]]:
        """
        Generate complete task with all iterations.
        Args:
            model_name: Name of the model to use
            task: Task configuration
            iterations: Number of iterations to perform
            renderer: Web renderer for screenshots (optional)
        Returns:
            List of generation results for each iteration
        """
        try:
            self.logger.info(
                f"Starting complete task generation: {task.name} with {model_name}"
            )
            results = []
            current_html = None
            # Create task output directory
            task_dir = (
                self.output_dir
                / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                / model_name
                / task.name
            )
            task_dir.mkdir(parents=True, exist_ok=True)
            for iteration in range(1, iterations + 1):
                self.logger.info(
                    f"Starting iteration {iteration}/{iterations} for {task.name}"
                )
                if iteration == 1:
                    # Generate initial HTML
                    result = self.generate_initial_html(model_name, task)
                else:
                    # Improve based on previous iteration
                    if not current_html:
                        raise ModelError("No HTML available for improvement")
                    # Get screenshot path from previous iteration
                    prev_result = results[-1]
                    # Use LLM-optimized screenshot for improvement if available, otherwise use full screenshot
                    screenshot_path = prev_result.get(
                        "llm_screenshot_path"
                    ) or prev_result.get("screenshot_path")
                    if not screenshot_path:
                        self.logger.warning(
                            f"No screenshot available for iteration {iteration}, skipping improvement"
                        )
                        break
                    result = self.improve_html(
                        model_name, task, iteration, current_html, screenshot_path
                    )
                # Save HTML to file
                html_filename = f"v{iteration}.html"
                html_path = task_dir / html_filename
                self.html_processor.save_html(result["html_content"], str(html_path))
                result["html_path"] = str(html_path)
                # Render screenshot if renderer is available
                if renderer:
                    try:
                        screenshot_path = task_dir / f"v{iteration}_screenshot.png"
                        render_result = renderer.render_html_file(
                            str(html_path), str(screenshot_path)
                        )
                        if render_result["success"]:
                            result["screenshot_path"] = render_result[
                                "full_screenshot_path"
                            ]
                            result["llm_screenshot_path"] = render_result[
                                "llm_screenshot_path"
                            ]
                            self.logger.info(f"Screenshots saved: {screenshot_path}")
                            if render_result["llm_screenshot_path"]:
                                self.logger.info(
                                    f"LLM-optimized screenshot: {render_result['llm_screenshot_path']}"
                                )
                        else:
                            self.logger.warning(
                                f"Failed to render screenshot for iteration {iteration}"
                            )
                    except Exception as e:
                        self.logger.error(
                            f"Error rendering screenshot for iteration {iteration}: {e}"
                        )
                # Save metadata
                metadata_path = task_dir / f"v{iteration}_metadata.json"
                with open(metadata_path, "w") as f:
                    # Create a copy without the HTML content for metadata
                    metadata = {k: v for k, v in result.items() if k != "html_content"}
                    json.dump(metadata, f, indent=2, default=str)
                result["metadata_path"] = str(metadata_path)
                results.append(result)
                current_html = result["html_content"]
                self.logger.info(
                    f"Completed iteration {iteration}/{iterations} for {task.name}"
                )
            # Save complete results summary
            summary_path = task_dir / "summary.json"
            summary = {
                "task_name": task.name,
                "model_name": model_name,
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
                        "html_size": len(r["html_content"]),
                        "validation_errors": len(
                            r["validation_results"].get("errors", [])
                        ),
                        "validation_warnings": len(
                            r["validation_results"].get("warnings", [])
                        ),
                    }
                    for r in results
                ],
            }
            with open(summary_path, "w") as f:
                json.dump(summary, f, indent=2, default=str)
            self.logger.info(
                f"Completed task generation: {task.name} with {model_name}"
            )
            return results
        except Exception as e:
            error_msg = (
                f"Failed to generate complete task {task.name} with {model_name}: {e}"
            )
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

    def get_generation_stats(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics from generation results."""
        if not results:
            return {}
        total_duration = sum(r["generation_duration"] for r in results)
        successful_iterations = sum(1 for r in results if r["success"])
        html_sizes = [len(r["html_content"]) for r in results]
        return {
            "total_iterations": len(results),
            "successful_iterations": successful_iterations,
            "success_rate": successful_iterations / len(results),
            "total_duration": total_duration,
            "average_duration": total_duration / len(results),
            "html_size_progression": html_sizes,
            "final_html_size": html_sizes[-1] if html_sizes else 0,
            "task_name": results[0]["task_name"],
            "model_name": results[0]["model_name"],
        }
