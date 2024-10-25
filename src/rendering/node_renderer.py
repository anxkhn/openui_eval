"""Node.js project renderer for capturing screenshots of framework applications."""

import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from core.config import RenderingConfig
from core.logger import get_logger
from frameworks.project_manager import ProjectManager
from rendering.renderer import WebRenderer


class NodeProjectRenderer:
    """Renderer for Node.js projects with framework support."""

    def __init__(self, config: RenderingConfig, work_dir: str = "temp_projects"):
        self.config = config
        self.work_dir = Path(work_dir)
        self.logger = get_logger()

        # Initialize project manager and base renderer
        self.project_manager = ProjectManager(self.work_dir)
        self.web_renderer = WebRenderer(config)

        # Keep track of active projects
        self.active_projects = {}

    def render_project(
        self,
        framework: str,
        project_name: str,
        task_description: str,
        generated_content: Dict[str, str],
        screenshot_path: str,
        create_llm_version: bool = True,
    ) -> Dict[str, Any]:
        """
        Render a complete framework project and capture screenshot.

        Args:
            framework: Framework name (react, vue, etc.)
            project_name: Name of the project
            task_description: Description of the task
            generated_content: Generated files from LLM
            screenshot_path: Path to save screenshot
            create_llm_version: Whether to create LLM-optimized version

        Returns:
            Dictionary with rendering results
        """
        start_time = time.time()
        project_dir = None
        server_process = None

        try:
            self.logger.info(f"Rendering {framework} project: {project_name}")

            # Create project
            project_dir = self.project_manager.create_project(
                framework, project_name, task_description, generated_content
            )

            # Install dependencies
            self.logger.info("Installing dependencies...")
            install_success = self.project_manager.install_dependencies(project_dir)
            if not install_success:
                raise RuntimeError("Failed to install dependencies")

            # Start development server
            self.logger.info("Starting development server...")
            server_process, server_url = self.project_manager.start_dev_server(
                project_dir
            )

            # Give the server a moment to fully start
            time.sleep(3)

            # Capture screenshot using web renderer
            self.logger.info(f"Capturing screenshot from {server_url}")
            screenshot_result = self.web_renderer.render_url(
                server_url, screenshot_path, create_llm_version
            )

            # Stop the server
            self.project_manager.stop_server(server_process)
            server_process = None

            duration = time.time() - start_time

            result = {
                "success": screenshot_result["success"],
                "project_dir": str(project_dir),
                "server_url": server_url,
                "full_screenshot_path": screenshot_result.get("full_screenshot_path"),
                "llm_screenshot_path": screenshot_result.get("llm_screenshot_path"),
                "duration": duration,
                "framework": framework,
                "install_success": install_success,
            }

            if not screenshot_result["success"]:
                result["error"] = screenshot_result.get(
                    "error", "Screenshot capture failed"
                )

            self.logger.info(f"Project rendering completed in {duration:.2f}s")
            return result

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Failed to render {framework} project {project_name}: {e}"
            self.logger.error(error_msg)

            # Cleanup on error
            if server_process:
                try:
                    self.project_manager.stop_server(server_process)
                except Exception:
                    pass

            return {
                "success": False,
                "project_dir": str(project_dir) if project_dir else None,
                "error": str(e),
                "duration": duration,
                "framework": framework,
                "install_success": False,
            }

    def render_existing_project(
        self,
        project_dir: Path,
        screenshot_path: str,
        create_llm_version: bool = True,
        rebuild: bool = False,
    ) -> Dict[str, Any]:
        """
        Render an existing project.

        Args:
            project_dir: Path to existing project
            screenshot_path: Path to save screenshot
            create_llm_version: Whether to create LLM-optimized version
            rebuild: Whether to rebuild the project

        Returns:
            Dictionary with rendering results
        """
        start_time = time.time()
        server_process = None

        try:
            self.logger.info(f"Rendering existing project: {project_dir}")

            # Validate project
            is_valid, errors = self.project_manager.validate_project(project_dir)
            if not is_valid:
                raise RuntimeError(f"Invalid project: {', '.join(errors)}")

            # Install dependencies if node_modules doesn't exist
            node_modules = project_dir / "node_modules"
            if not node_modules.exists():
                self.logger.info("Installing dependencies...")
                install_success = self.project_manager.install_dependencies(project_dir)
                if not install_success:
                    raise RuntimeError("Failed to install dependencies")

            # Rebuild if requested
            if rebuild:
                self.logger.info("Rebuilding project...")
                build_success = self.project_manager.build_project(project_dir)
                if not build_success:
                    self.logger.warning("Build failed, continuing with dev server")

            # Start development server
            self.logger.info("Starting development server...")
            server_process, server_url = self.project_manager.start_dev_server(
                project_dir
            )

            # Give the server a moment to fully start
            time.sleep(3)

            # Capture screenshot
            self.logger.info(f"Capturing screenshot from {server_url}")
            screenshot_result = self.web_renderer.render_url(
                server_url, screenshot_path, create_llm_version
            )

            # Stop the server
            self.project_manager.stop_server(server_process)
            server_process = None

            duration = time.time() - start_time

            result = {
                "success": screenshot_result["success"],
                "project_dir": str(project_dir),
                "server_url": server_url,
                "full_screenshot_path": screenshot_result.get("full_screenshot_path"),
                "llm_screenshot_path": screenshot_result.get("llm_screenshot_path"),
                "duration": duration,
            }

            if not screenshot_result["success"]:
                result["error"] = screenshot_result.get(
                    "error", "Screenshot capture failed"
                )

            self.logger.info(f"Existing project rendering completed in {duration:.2f}s")
            return result

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Failed to render existing project {project_dir}: {e}"
            self.logger.error(error_msg)

            # Cleanup on error
            if server_process:
                try:
                    self.project_manager.stop_server(server_process)
                except Exception:
                    pass

            return {
                "success": False,
                "project_dir": str(project_dir),
                "error": str(e),
                "duration": duration,
            }

    def cleanup(self):
        """Clean up renderer resources."""
        try:
            self.logger.info("Cleaning up Node project renderer")

            # Stop all active servers
            self.project_manager.cleanup_all_servers()

            # Cleanup web renderer
            self.web_renderer.cleanup()

            # Clear active projects
            self.active_projects.clear()

        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()

    def get_project_info(self, project_name: str) -> Dict[str, Any]:
        """Get information about a project."""
        if project_name in self.active_projects:
            return self.active_projects[project_name]

        project_dir = self.work_dir / project_name
        return self.project_manager.get_project_info(project_dir)

    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects in the work directory."""
        projects = []

        if not self.work_dir.exists():
            return projects

        for item in self.work_dir.iterdir():
            if item.is_dir():
                info = self.project_manager.get_project_info(item)
                info["name"] = item.name
                projects.append(info)

        return projects

    def remove_project(self, project_name: str) -> bool:
        """
        Remove a project directory.

        Args:
            project_name: Name of the project to remove

        Returns:
            True if successful
        """
        try:
            project_dir = self.work_dir / project_name

            if not project_dir.exists():
                self.logger.warning(f"Project does not exist: {project_name}")
                return True

            # Stop any servers for this project
            if project_name in self.active_projects:
                # This would need to be implemented if we track servers per project
                pass

            # Remove the directory
            import shutil

            shutil.rmtree(project_dir)

            # Remove from active projects
            self.active_projects.pop(project_name, None)

            self.logger.info(f"Removed project: {project_name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to remove project {project_name}: {e}")
            return False
