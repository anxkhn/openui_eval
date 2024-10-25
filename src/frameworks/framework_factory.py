"""Framework factory for creating framework instances."""

from typing import Dict, List, Type

from frameworks.angular_framework import AngularFramework
from frameworks.base_framework import BaseFramework
from frameworks.nextjs_framework import NextJSFramework
from frameworks.react_framework import ReactFramework
from frameworks.svelte_framework import SvelteFramework
from frameworks.vue_framework import VueFramework


class FrameworkFactory:
    """Factory for creating framework instances."""

    _frameworks: Dict[str, Type[BaseFramework]] = {
        "react": ReactFramework,
        "nextjs": NextJSFramework,
        "vue": VueFramework,
        "angular": AngularFramework,
        "svelte": SvelteFramework,
    }

    @classmethod
    def create_framework(cls, framework_name: str) -> BaseFramework:
        """
        Create a framework instance.

        Args:
            framework_name: Name of the framework

        Returns:
            Framework instance

        Raises:
            FrameworkError: If framework is not supported
        """
        framework_name = framework_name.lower()

        if framework_name not in cls._frameworks:
            supported = ", ".join(cls._frameworks.keys())
            raise ValueError(
                f"Unsupported framework: {framework_name}. Supported: {supported}"
            )

        framework_class = cls._frameworks[framework_name]
        return framework_class()

    @classmethod
    def get_supported_frameworks(cls) -> List[str]:
        """Get list of supported framework names."""
        return list(cls._frameworks.keys())

    @classmethod
    def is_supported(cls, framework_name: str) -> bool:
        """Check if a framework is supported."""
        return framework_name.lower() in cls._frameworks

    @classmethod
    def register_framework(cls, name: str, framework_class: Type[BaseFramework]):
        """
        Register a custom framework.

        Args:
            name: Framework name
            framework_class: Framework class
        """
        cls._frameworks[name.lower()] = framework_class

    @classmethod
    def get_framework_versions(cls) -> Dict[str, str]:
        """Get versions of all supported frameworks."""
        versions = {}
        for name in cls._frameworks:
            framework = cls.create_framework(name)
            versions[name] = framework.version
        return versions

    @classmethod
    def get_framework_info(cls, framework_name: str) -> Dict[str, any]:
        """
        Get information about a specific framework.

        Args:
            framework_name: Name of the framework

        Returns:
            Dictionary with framework information
        """
        framework = cls.create_framework(framework_name)
        return {
            "name": framework.name,
            "version": framework.version,
            "default_port": framework.default_port,
            "build_dir": framework.build_dir,
            "install_command": " ".join(framework.get_install_command()),
            "dev_command": " ".join(framework.get_dev_command()),
            "build_command": " ".join(framework.get_build_command()),
        }
