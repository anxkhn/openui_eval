"""Svelte 5 framework implementation."""

from pathlib import Path
from typing import Any, Dict, List

from .base_framework import BaseFramework


class SvelteFramework(BaseFramework):
    """Svelte 5 framework implementation."""

    def __init__(self):
        super().__init__("Svelte", "5.0.0")

    def get_project_template(self) -> Dict[str, str]:
        """Get Svelte project template files."""
        return {
            "vite.config.js": '''import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [svelte()],
  server: {
    port: 5173
  }
})''',
            "svelte.config.js": '''import { vitePreprocess } from '@sveltejs/vite-plugin-svelte'

export default {
  // Consult https://svelte.dev/docs#compile-time-svelte-preprocess
  // for more information about preprocessors
  preprocess: vitePreprocess(),
}''',
            "index.html": '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Svelte App</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>''',
            "src/main.js": '''import './app.css'
import App from './App.svelte'

const app = new App({
  target: document.getElementById('app'),
})

export default app''',
            "src/app.css": ''':root {
  font-family: Inter, system-ui, Avenir, Helvetica, Arial, sans-serif;
  line-height: 1.5;
  font-weight: 400;

  color-scheme: light dark;
  color: rgba(255, 255, 255, 0.87);
  background-color: #242424;

  font-synthesis: none;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  -webkit-text-size-adjust: 100%;
}

a {
  font-weight: 500;
  color: #646cff;
  text-decoration: inherit;
}
a:hover {
  color: #535bf2;
}

body {
  margin: 0;
  display: flex;
  place-items: center;
  min-width: 320px;
  min-height: 100vh;
}

#app {
  max-width: 1280px;
  margin: 0 auto;
  padding: 2rem;
  text-align: center;
}

.card {
  padding: 2em;
}

.read-the-docs {
  color: #888;
}

button {
  border-radius: 8px;
  border: 1px solid transparent;
  padding: 0.6em 1.2em;
  font-size: 1em;
  font-weight: 500;
  font-family: inherit;
  background-color: #1a1a1a;
  color: white;
  cursor: pointer;
  transition: border-color 0.25s;
}
button:hover {
  border-color: #646cff;
}
button:focus,
button:focus-visible {
  outline: 4px auto -webkit-focus-ring-color;
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
    color: #213547;
  }
}''',
            ".gitignore": '''# Logs
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
*.sw?''',
            "README.md": '''# Svelte + Vite

This template should help get you started developing with Svelte in Vite.

## Recommended IDE Setup

[VS Code](https://code.visualstudio.com/) + [Svelte](https://marketplace.visualstudio.com/items?itemName=svelte.svelte-vscode).

## Need an official Svelte framework?

Check out [SvelteKit](https://github.com/sveltejs/kit#readme), which is also powered by Vite. Deploy anywhere with its serverless-first approach and adapt to various platforms, with out of the box support for TypeScript, SCSS, and Less, and easily-added support for mdsvex, GraphQL, PostCSS, Tailwind CSS, and more.

## Technical considerations

**Why use this over SvelteKit?**

- It brings its own routing solution which might not be preferable for some users.
- It is first and foremost a framework that just happens to use Vite under the hood, not a Vite app.

This template contains as little as possible to get started with Vite + Svelte, while taking into account the developer experience with regards to HMR and intellisense. It demonstrates capabilities like HMR updates and hot reloading of stores.

Users can later add TypeScript support with `@sveltejs/vite-plugin-svelte`.
''',
        }

    def get_package_json(self) -> Dict[str, Any]:
        """Get Svelte package.json configuration."""
        return {
            "name": "svelte-app",
            "private": True,
            "version": "0.0.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview"
            },
            "devDependencies": {
                "@sveltejs/vite-plugin-svelte": "^4.0.0",
                "svelte": "^5.0.0",
                "vite": "^5.0.0"
            },
            "engines": {
                "node": ">=22.0.0"
            }
        }

    def get_build_command(self) -> List[str]:
        """Get Svelte build command."""
        return ["npm", "run", "build"]

    def get_dev_command(self) -> List[str]:
        """Get Svelte dev server command."""
        return ["npm", "run", "dev"]

    def get_install_command(self) -> List[str]:
        """Get dependency installation command."""
        return ["npm", "install"]

    @property
    def default_port(self) -> int:
        """Svelte dev server default port."""
        return 5173

    @property
    def build_dir(self) -> str:
        """Svelte build output directory."""
        return "dist"

    def _add_port_to_command(self, cmd: List[str], port: int) -> List[str]:
        """Add port configuration to Svelte dev command."""
        if "dev" in cmd:
            return cmd + ["--port", str(port)]
        return cmd

    def _validate_framework_specific(self, project_dir: Path) -> List[str]:
        """Validate Svelte-specific requirements."""
        errors = []
        
        # Check for required Svelte files
        required_files = [
            "vite.config.js",
            "svelte.config.js",
            "src/main.js",
            "src/App.svelte"
        ]
        
        for file_path in required_files:
            if not (project_dir / file_path).exists():
                errors.append(f"Required Svelte file missing: {file_path}")
        
        return errors

    def create_app_component(self, markup_content: str, script_content: str = "", style_content: str = "") -> str:
        """Create the main App.svelte component."""
        script_section = f"<script>\n{script_content}\n</script>" if script_content else "<script>\n  // Component logic\n</script>"
        style_section = f"\n<style>\n{style_content}\n</style>" if style_content else ""
        
        return f'''{script_section}

<main>
  {markup_content}
</main>
{style_section}'''

    def create_component(self, name: str, markup_content: str, script_content: str = "", style_content: str = "") -> str:
        """Create a Svelte component."""
        script_section = f"<script>\n{script_content}\n</script>" if script_content else ""
        style_section = f"\n<style>\n{style_content}\n</style>" if style_content else ""
        
        return f'''{script_section}

{markup_content}
{style_section}'''
