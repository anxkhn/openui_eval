"""React 19 framework implementation."""

from pathlib import Path
from typing import Any, Dict, List

from .base_framework import BaseFramework


class ReactFramework(BaseFramework):
    """React 19 framework implementation."""

    def __init__(self):
        super().__init__("React", "19.0.0")

    def get_project_template(self) -> Dict[str, str]:
        """Get React project template files."""
        return {
            "public/index.html": '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="React App" />
    <title>React App</title>
</head>
<body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
</body>
</html>''',
            "src/index.js": '''import React from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App';

const container = document.getElementById('root');
const root = createRoot(container);
root.render(<App />);''',
            "src/index.css": '''body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}

* {
  box-sizing: border-box;
}''',
            ".gitignore": '''# Dependencies
node_modules/
.pnp
.pnp.js

# Testing
coverage/

# Production
build/

# Environment variables
.env.local
.env.development.local
.env.test.local
.env.production.local

# Logs
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db''',
            "README.md": '''# React App

This project was bootstrapped with Create React App.

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

### `npm run build`

Builds the app for production to the `build` folder.
''',
        }

    def get_package_json(self) -> Dict[str, Any]:
        """Get React package.json configuration."""
        return {
            "name": "react-app",
            "version": "0.1.0",
            "private": True,
            "dependencies": {
                "react": "^19.0.0",
                "react-dom": "^19.0.0",
                "react-scripts": "5.0.1"
            },
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test",
                "eject": "react-scripts eject"
            },
            "eslintConfig": {
                "extends": [
                    "react-app",
                    "react-app/jest"
                ]
            },
            "browserslist": {
                "production": [
                    ">0.2%",
                    "not dead",
                    "not op_mini all"
                ],
                "development": [
                    "last 1 chrome version",
                    "last 1 firefox version",
                    "last 1 safari version"
                ]
            },
            "engines": {
                "node": ">=22.0.0"
            }
        }

    def get_build_command(self) -> List[str]:
        """Get React build command."""
        return ["npm", "run", "build"]

    def get_dev_command(self) -> List[str]:
        """Get React dev server command."""
        return ["npm", "start"]

    def get_install_command(self) -> List[str]:
        """Get dependency installation command."""
        return ["npm", "install"]

    @property
    def default_port(self) -> int:
        """React dev server default port."""
        return 3000

    @property
    def build_dir(self) -> str:
        """React build output directory."""
        return "build"

    def _add_port_to_command(self, cmd: List[str], port: int) -> List[str]:
        """Add port configuration to React dev command."""
        if "start" in cmd:
            # React uses PORT environment variable
            return ["env", f"PORT={port}"] + cmd
        return cmd

    def _validate_framework_specific(self, project_dir: Path) -> List[str]:
        """Validate React-specific requirements."""
        errors = []
        
        # Check for required React files
        required_files = [
            "public/index.html",
            "src/index.js",
            "src/App.js"
        ]
        
        for file_path in required_files:
            if not (project_dir / file_path).exists():
                errors.append(f"Required React file missing: {file_path}")
        
        return errors

    def create_app_component(self, component_content: str) -> str:
        """Create the main App component."""
        return f'''import React from 'react';
import './App.css';

function App() {{
  return (
    <div className="App">
      {component_content}
    </div>
  );
}}

export default App;'''

    def create_component_css(self, css_content: str = "") -> str:
        """Create the App.css file."""
        base_css = '''.App {
  text-align: center;
}

.App-header {
  background-color: #282c34;
  padding: 20px;
  color: white;
}

.App-link {
  color: #61dafb;
}'''
        
        if css_content:
            return base_css + "\n\n" + css_content
        return base_css
