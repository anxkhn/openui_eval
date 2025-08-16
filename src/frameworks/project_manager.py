"""Project manager for handling multi-file JavaScript projects."""

import json
import signal
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .framework_factory import FrameworkFactory

from ..core.logger import get_logger


class ProjectManager:
    """Manager for creating, building, and serving JavaScript projects."""

    def __init__(self, work_dir: Path):
        self.work_dir = Path(work_dir)
        self.logger = get_logger()
        self.active_servers: List[subprocess.Popen] = []

        # Ensure work directory exists
        self.work_dir.mkdir(parents=True, exist_ok=True)

    def create_project(
        self,
        framework: str,
        project_name: str,
        task_description: str,
        generated_content: Dict[str, str],
    ) -> Path:
        """
        Create a new project.

        Args:
            framework: Framework name (react, vue, etc.)
            project_name: Name of the project
            task_description: Description of the task
            generated_content: Generated files from LLM

        Returns:
            Path to the created project

        Raises:
            ProjectError: If project creation fails
        """
        try:
            self.logger.info(f"Creating {framework} project: {project_name}")

            # Create framework instance
            framework_instance = FrameworkFactory.create_framework(framework)

            # Create project directory
            project_dir = self.work_dir / project_name
            if project_dir.exists():
                self.logger.warning(
                    f"Project directory exists, removing: {project_dir}"
                )
                import shutil

                shutil.rmtree(project_dir)

            # Create the project
            success = framework_instance.create_project(
                project_dir, task_description, generated_content
            )

            if not success:
                raise RuntimeError(f"Failed to create {framework} project")

            self.logger.info(f"Successfully created project at {project_dir}")
            return project_dir

        except Exception as e:
            error_msg = f"Failed to create project {project_name}: {e}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

    def install_dependencies(self, project_dir: Path) -> bool:
        """
        Install project dependencies.

        Args:
            project_dir: Project directory

        Returns:
            True if successful
        """
        try:
            # Detect framework from project structure
            framework_name = self._detect_framework(project_dir)
            framework_instance = FrameworkFactory.create_framework(framework_name)

            self.logger.info(f"Installing dependencies for {framework_name} project")
            success, output = framework_instance.install_dependencies(project_dir)

            if success:
                self.logger.info("Dependencies installed successfully")
            else:
                self.logger.error(f"Failed to install dependencies: {output}")

            return success

        except Exception as e:
            self.logger.error(f"Error installing dependencies: {e}")
            return False

    def build_project(self, project_dir: Path) -> bool:
        """
        Build the project.

        Args:
            project_dir: Project directory

        Returns:
            True if successful
        """
        try:
            # Detect framework from project structure
            framework_name = self._detect_framework(project_dir)
            framework_instance = FrameworkFactory.create_framework(framework_name)

            self.logger.info(f"Building {framework_name} project")
            success, output = framework_instance.build_project(project_dir)

            if success:
                self.logger.info("Project built successfully")
            else:
                self.logger.error(f"Build failed: {output}")

            return success

        except Exception as e:
            self.logger.error(f"Error building project: {e}")
            return False

    def start_dev_server(
        self, project_dir: Path, port: Optional[int] = None
    ) -> Tuple[subprocess.Popen, str]:
        """
        Start the development server.

        Args:
            project_dir: Project directory
            port: Port to use (optional)

        Returns:
            Tuple of (process, server_url)
        """
        try:
            # Detect framework from project structure
            framework_name = self._detect_framework(project_dir)
            framework_instance = FrameworkFactory.create_framework(framework_name)

            # Use framework default port if not specified
            actual_port = port or framework_instance.default_port

            self.logger.info(
                f"Starting {framework_name} dev server on port {actual_port}"
            )

            # Start the server
            process = framework_instance.start_dev_server(project_dir, actual_port)
            server_url = framework_instance.get_server_url(actual_port)

            # Keep track of active servers
            self.active_servers.append(process)

            # Wait for server to start
            self._wait_for_server(server_url)

            self.logger.info(f"Dev server started: {server_url}")
            return process, server_url

        except Exception as e:
            error_msg = f"Failed to start dev server: {e}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

    def stop_server(self, process: subprocess.Popen) -> bool:
        """
        Stop a development server.

        Args:
            process: Server process

        Returns:
            True if stopped successfully
        """
        try:
            if process.poll() is None:  # Process is still running
                # Send SIGTERM first
                process.terminate()

                # Wait up to 10 seconds for graceful shutdown
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    # Force kill if it doesn't stop gracefully
                    process.kill()
                    process.wait()

                self.logger.info(f"Stopped server process {process.pid}")

            # Remove from active servers
            if process in self.active_servers:
                self.active_servers.remove(process)

            return True

        except Exception as e:
            self.logger.error(f"Error stopping server: {e}")
            return False

    def cleanup_all_servers(self):
        """Stop all active development servers."""
        self.logger.info("Cleaning up all active servers")

        for process in self.active_servers[
            :
        ]:  # Copy list to avoid modification during iteration
            self.stop_server(process)

        self.active_servers.clear()

    def validate_project(self, project_dir: Path) -> Tuple[bool, List[str]]:
        """
        Validate project structure.

        Args:
            project_dir: Project directory

        Returns:
            Tuple of (is_valid, error_messages)
        """
        try:
            framework_name = self._detect_framework(project_dir)
            framework_instance = FrameworkFactory.create_framework(framework_name)

            return framework_instance.validate_project(project_dir)

        except Exception as e:
            return False, [f"Error validating project: {e}"]

    def get_project_info(self, project_dir: Path) -> Dict[str, Any]:
        """
        Get information about a project.

        Args:
            project_dir: Project directory

        Returns:
            Dictionary with project information
        """
        try:
            info = {
                "project_dir": str(project_dir),
                "exists": project_dir.exists(),
                "framework": None,
                "has_dependencies": False,
                "has_build": False,
            }

            if not project_dir.exists():
                return info

            # Detect framework
            try:
                framework_name = self._detect_framework(project_dir)
                framework_instance = FrameworkFactory.create_framework(framework_name)
                info["framework"] = framework_name

                # Check for dependencies
                node_modules = project_dir / "node_modules"
                info["has_dependencies"] = node_modules.exists()

                # Check for build output
                build_dir = project_dir / framework_instance.build_dir
                info["has_build"] = build_dir.exists()

            except Exception as e:
                info["error"] = str(e)

            return info

        except Exception as e:
            return {"error": str(e)}

    def _detect_framework(self, project_dir: Path) -> str:
        """
        Detect framework from project structure.

        Args:
            project_dir: Project directory

        Returns:
            Framework name

        Raises:
            FrameworkError: If framework cannot be detected
        """
        # Check for framework-specific files
        if (project_dir / "next.config.js").exists():
            return "nextjs"
        elif (project_dir / "angular.json").exists():
            return "angular"
        elif (project_dir / "svelte.config.js").exists():
            return "svelte"
        elif (project_dir / "vite.config.js").exists():
            # Could be Vue or Svelte - check package.json
            package_json_path = project_dir / "package.json"
            if package_json_path.exists():
                try:
                    with open(package_json_path, "r") as f:
                        package_data = json.load(f)

                    dependencies = package_data.get("dependencies", {})
                    dev_dependencies = package_data.get("devDependencies", {})
                    all_deps = {**dependencies, **dev_dependencies}

                    if "vue" in all_deps:
                        return "vue"
                    elif "svelte" in all_deps:
                        return "svelte"
                except Exception:
                    pass

        # Check for React (could be create-react-app or custom setup)
        package_json_path = project_dir / "package.json"
        if package_json_path.exists():
            try:
                with open(package_json_path, "r") as f:
                    package_data = json.load(f)

                dependencies = package_data.get("dependencies", {})

                if "react" in dependencies:
                    return "react"

            except Exception:
                pass

        raise ValueError(f"Cannot detect framework for project: {project_dir}")

    def _wait_for_server(self, server_url: str, timeout: int = 30):
        """
        Wait for server to become available.

        Args:
            server_url: Server URL to check
            timeout: Timeout in seconds
        """
        import requests

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(server_url, timeout=5)
                if response.status_code == 200:
                    return
            except requests.RequestException:
                pass

            time.sleep(1)

        raise TimeoutError(f"Server did not start within {timeout} seconds")

    def __del__(self):
        """Cleanup on destruction."""
        self.cleanup_all_servers()
