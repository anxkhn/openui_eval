"""Vue 3.5 framework implementation."""

from pathlib import Path
from typing import Any, Dict, List

from .base_framework import BaseFramework


class VueFramework(BaseFramework):
    """Vue 3.5 framework implementation."""

    def __init__(self):
        super().__init__("Vue", "3.5.0")

    def get_project_template(self) -> Dict[str, str]:
        """Get Vue project template files."""
        return {
            "index.html": """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Vue App</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>""",
            "src/main.js": """import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

createApp(App).mount('#app')""",
            "src/style.css": """#app {
  max-width: 1280px;
  margin: 0 auto;
  padding: 2rem;
  text-align: center;
}

.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}

@media (prefers-color-scheme: light) {
  :root {
    color: #213547;
    background-color: #ffffff;
  }
  a:hover {
    color: #747bff;
  }
  button {
    background-color: #f9f9f9;
  }
}""",
            "vite.config.js": """import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173
  }
})""",
            ".gitignore": """# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

node_modules
dist
dist-ssr
*.local

# Editor directories and files
.vscode/*
!.vscode/extensions.json
.idea
.DS_Store
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?""",
            "README.md": """# Vue 3 + Vite

This template should help get you started developing with Vue 3 in Vite. The template uses Vue 3 `<script setup>` SFCs, check out the [script setup docs](https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup) to learn more.

## Recommended IDE Setup

- [VS Code](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur) + [TypeScript Vue Plugin (Volar)](https://marketplace.visualstudio.com/items?itemName=Vue.vscode-typescript-vue-plugin).

## Type Support for `.vue` Imports in TS

TypeScript cannot handle type information for `.vue` imports by default, so we replace the default `tsc` CLI with `vue-tsc` for type checking. In editors, we need [TypeScript Vue Plugin (Volar)](https://marketplace.visualstudio.com/items?itemName=Vue.vscode-typescript-vue-plugin) to make the TypeScript language service aware of `.vue` types.

If the standalone TypeScript plugin doesn't feel fast enough to you, Volar has also implemented a [Take Over Mode](https://github.com/johnsoncodehk/volar/discussions/471#discussioncomment-1361669) that is more performant. You can enable it by the following steps:

1. Disable the built-in TypeScript Extension
    1) Run `Extensions: Show Built-in Extensions` from VSCode's command palette
    2) Find `TypeScript and JavaScript Language Features`, right click and select `Disable (Workspace)`
2. Reload the VSCode window by running `Developer: Reload Window` from the command palette.
""",
        }

    def get_package_json(self) -> Dict[str, Any]:
        """Get Vue package.json configuration."""
        return {
            "name": "vue-app",
            "private": True,
            "version": "0.0.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview",
            },
            "dependencies": {"vue": "^3.5.0"},
            "devDependencies": {"@vitejs/plugin-vue": "^4.0.0", "vite": "^5.0.0"},
            "engines": {"node": ">=22.0.0"},
        }

    def get_build_command(self) -> List[str]:
        """Get Vue build command."""
        return ["npm", "run", "build"]

    def get_dev_command(self) -> List[str]:
        """Get Vue dev server command."""
        return ["npm", "run", "dev"]

    def get_install_command(self) -> List[str]:
        """Get dependency installation command."""
        return ["npm", "install"]

    @property
    def default_port(self) -> int:
        """Vue dev server default port."""
        return 5173

    @property
    def build_dir(self) -> str:
        """Vue build output directory."""
        return "dist"

    def _add_port_to_command(self, cmd: List[str], port: int) -> List[str]:
        """Add port configuration to Vue dev command."""
        if "dev" in cmd:
            return cmd + ["--port", str(port)]
        return cmd

    def _validate_framework_specific(self, project_dir: Path) -> List[str]:
        """Validate Vue-specific requirements."""
        errors = []

        # Check for required Vue files
        required_files = ["vite.config.js", "src/main.js", "src/App.vue"]

        for file_path in required_files:
            if not (project_dir / file_path).exists():
                errors.append(f"Required Vue file missing: {file_path}")

        return errors

    def create_app_component(
        self, template_content: str, script_content: str = "", style_content: str = ""
    ) -> str:
        """Create the main App.vue component."""
        script_section = (
            f"<script setup>\n{script_content}\n</script>"
            if script_content
            else "<script setup>\n// Vue component logic\n</script>"
        )
        style_section = (
            f"<style scoped>\n{style_content}\n</style>"
            if style_content
            else "<style scoped>\n/* Component styles */\n</style>"
        )

        return f"""{script_section}

<template>
  <div id="app">
    {template_content}
  </div>
</template>

{style_section}"""

    def create_component(
        self,
        name: str,
        template_content: str,
        script_content: str = "",
        style_content: str = "",
    ) -> str:
        """Create a Vue component."""
        script_section = (
            f"<script setup>\n{script_content}\n</script>"
            if script_content
            else "<script setup>\n// Component logic\n</script>"
        )
        style_section = (
            f"<style scoped>\n{style_content}\n</style>" if style_content else ""
        )

        return f"""{script_section}

<template>
  {template_content}
</template>

{style_section}"""
