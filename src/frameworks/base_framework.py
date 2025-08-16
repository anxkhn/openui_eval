"""Base framework interface for project generation and management."""

import json
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


from ..core.logger import get_logger


class BaseFramework(ABC):
    """Base class for all framework implementations."""

    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
        self.logger = get_logger()
        self.node_version = "22.12.0"  # Node v22 LTS

    @abstractmethod
    def get_project_template(self) -> Dict[str, str]:
        """
        Get the project template files.

        Returns:
            Dict mapping file paths to file contents
        """
        pass

    @abstractmethod
    def get_package_json(self) -> Dict[str, Any]:
        """
        Get the package.json configuration.

        Returns:
            Package.json content as dictionary
        """
        pass

    @abstractmethod
    def get_build_command(self) -> List[str]:
        """
        Get the build command for the project.

        Returns:
            List of command parts
        """
        pass

    @abstractmethod
    def get_dev_command(self) -> List[str]:
        """
        Get the development server command.

        Returns:
            List of command parts
        """
        pass

    @abstractmethod
    def get_install_command(self) -> List[str]:
        """
        Get the dependency installation command.

        Returns:
            List of command parts
        """
        pass

    @property
    @abstractmethod
    def default_port(self) -> int:
        """Get the default development server port."""
        pass

    @property
    @abstractmethod
    def build_dir(self) -> str:
        """Get the build output directory."""
        pass

    def create_project(
        self,
        project_dir: Path,
        task_description: str,
        generated_content: Dict[str, str],
    ) -> bool:
        """
        Create a complete project from generated content.

        Args:
            project_dir: Directory to create project in
            task_description: Description of the task
            generated_content: Generated files from LLM

        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Creating {self.name} project in {project_dir}")

            # Create project directory
            project_dir.mkdir(parents=True, exist_ok=True)

            # Get base template
            template_files = self.get_project_template()

            # Merge generated content with template
            all_files = {**template_files, **generated_content}

            # Create package.json
            package_json = self.get_package_json()
            all_files["package.json"] = json.dumps(package_json, indent=2)

            # Write all files
            for file_path, content in all_files.items():
                full_path = project_dir / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)

                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)

            self.logger.info(f"Created {len(all_files)} files for {self.name} project")
            return True

        except Exception as e:
            self.logger.error(f"Failed to create {self.name} project: {e}")
            return False

    def install_dependencies(self, project_dir: Path) -> Tuple[bool, str]:
        """
        Install project dependencies.

        Args:
            project_dir: Project directory

        Returns:
            Tuple of (success, output)
        """
        try:
            cmd = self.get_install_command()
            self.logger.info(f"Installing dependencies: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes timeout
            )

            success = result.returncode == 0
            output = result.stdout + result.stderr

            if success:
                self.logger.info("Dependencies installed successfully")
            else:
                self.logger.error(f"Failed to install dependencies: {output}")

            return success, output

        except subprocess.TimeoutExpired:
            error_msg = "Dependency installation timed out"
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error installing dependencies: {e}"
            self.logger.error(error_msg)
            return False, error_msg

    def build_project(self, project_dir: Path) -> Tuple[bool, str]:
        """
        Build the project.

        Args:
            project_dir: Project directory

        Returns:
            Tuple of (success, output)
        """
        try:
            cmd = self.get_build_command()
            self.logger.info(f"Building project: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes timeout
            )

            success = result.returncode == 0
            output = result.stdout + result.stderr

            if success:
                self.logger.info("Project built successfully")
            else:
                self.logger.error(f"Build failed: {output}")

            return success, output

        except subprocess.TimeoutExpired:
            error_msg = "Build timed out"
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error building project: {e}"
            self.logger.error(error_msg)
            return False, error_msg

    def start_dev_server(
        self, project_dir: Path, port: Optional[int] = None
    ) -> subprocess.Popen:
        """
        Start the development server.

        Args:
            project_dir: Project directory
            port: Port to use (optional)

        Returns:
            Subprocess object
        """
        try:
            cmd = self.get_dev_command()
            if port:
                # Add port configuration to command if supported
                cmd = self._add_port_to_command(cmd, port)

            self.logger.info(f"Starting dev server: {' '.join(cmd)}")

            process = subprocess.Popen(
                cmd,
                cwd=project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            self.logger.info(f"Dev server started with PID {process.pid}")
            return process

        except Exception as e:
            self.logger.error(f"Failed to start dev server: {e}")
            raise RuntimeError(f"Failed to start dev server: {e}")

    def _add_port_to_command(self, cmd: List[str], port: int) -> List[str]:
        """
        Add port configuration to command (framework-specific).
        Default implementation does nothing.
        """
        return cmd

    def get_server_url(self, port: Optional[int] = None) -> str:
        """Get the development server URL."""
        actual_port = port or self.default_port
        return f"http://localhost:{actual_port}"

    def validate_project(self, project_dir: Path) -> Tuple[bool, List[str]]:
        """
        Validate that the project is properly structured.

        Args:
            project_dir: Project directory

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check if package.json exists
        package_json_path = project_dir / "package.json"
        if not package_json_path.exists():
            errors.append("package.json not found")

        # Check if node_modules exists (after install)
        node_modules_path = project_dir / "node_modules"
        if not node_modules_path.exists():
            errors.append("node_modules not found - dependencies may not be installed")

        # Framework-specific validation
        framework_errors = self._validate_framework_specific(project_dir)
        errors.extend(framework_errors)

        return len(errors) == 0, errors

    def _validate_framework_specific(self, project_dir: Path) -> List[str]:
        """
        Perform framework-specific validation.
        Override in subclasses.
        """
        return []

    def cleanup_project(self, project_dir: Path) -> bool:
        """
        Clean up project resources.

        Args:
            project_dir: Project directory

        Returns:
            True if successful
        """
        try:
            # Remove node_modules and build directories
            dirs_to_remove = ["node_modules", self.build_dir, ".next", "dist", "build"]

            for dir_name in dirs_to_remove:
                dir_path = project_dir / dir_name
                if dir_path.exists() and dir_path.is_dir():
                    import shutil

                    shutil.rmtree(dir_path)
                    self.logger.debug(f"Removed {dir_path}")

            return True

        except Exception as e:
            self.logger.error(f"Error cleaning up project: {e}")
            return False
