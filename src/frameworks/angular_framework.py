"""Angular 20 framework implementation."""

from pathlib import Path
from typing import Any, Dict, List

from frameworks.base_framework import BaseFramework


class AngularFramework(BaseFramework):
    """Angular 20 framework implementation."""

    def __init__(self):
        super().__init__("Angular", "20.0.0")

    def get_project_template(self) -> Dict[str, str]:
        """Get Angular project template files."""
        return {
            "angular.json": """{
  "$schema": "./node_modules/@angular/cli/lib/config/schema.json",
  "version": 1,
  "newProjectRoot": "projects",
  "projects": {
    "angular-app": {
      "projectType": "application",
      "schematics": {},
      "root": "",
      "sourceRoot": "src",
      "prefix": "app",
      "architect": {
        "build": {
          "builder": "@angular-devkit/build-angular:browser",
          "options": {
            "outputPath": "dist/angular-app",
            "index": "src/index.html",
            "main": "src/main.ts",
            "polyfills": ["zone.js"],
            "tsConfig": "tsconfig.app.json",
            "assets": ["src/favicon.ico", "src/assets"],
            "styles": ["src/styles.css"],
            "scripts": []
          },
          "configurations": {
            "production": {
              "budgets": [
                {
                  "type": "initial",
                  "maximumWarning": "500kb",
                  "maximumError": "1mb"
                },
                {
                  "type": "anyComponentStyle",
                  "maximumWarning": "2kb",
                  "maximumError": "4kb"
                }
              ],
              "outputHashing": "all"
            },
            "development": {
              "buildOptimizer": false,
              "optimization": false,
              "vendorChunk": true,
              "extractLicenses": false,
              "sourceMap": true,
              "namedChunks": true
            }
          },
          "defaultConfiguration": "production"
        },
        "serve": {
          "builder": "@angular-devkit/build-angular:dev-server",
          "configurations": {
            "production": {
              "buildTarget": "angular-app:build:production"
            },
            "development": {
              "buildTarget": "angular-app:build:development"
            }
          },
          "defaultConfiguration": "development"
        }
      }
    }
  }
}""",
            "src/index.html": """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>AngularApp</title>
  <base href="/">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" type="image/x-icon" href="favicon.ico">
</head>
<body>
  <app-root></app-root>
</body>
</html>""",
            "src/main.ts": """import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';

bootstrapApplication(AppComponent, appConfig)
  .catch((err) => console.error(err));""",
            "src/styles.css": """/* You can add global styles to this file, and also import other style files */
html, body { height: 100%; }
body { margin: 0; font-family: Roboto, "Helvetica Neue", sans-serif; }""",
            "src/app/app.config.ts": """import { ApplicationConfig } from '@angular/core';
import { provideRouter } from '@angular/router';

import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [provideRouter(routes)]
};""",
            "src/app/app.routes.ts": """import { Routes } from '@angular/router';

export const routes: Routes = [];""",
            "tsconfig.json": """{
  "compileOnSave": false,
  "compilerOptions": {
    "baseUrl": "./",
    "outDir": "./dist/out-tsc",
    "forceConsistentCasingInFileNames": true,
    "strict": true,
    "noImplicitOverride": true,
    "noPropertyAccessFromIndexSignature": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "sourceMap": true,
    "declaration": false,
    "downlevelIteration": true,
    "experimentalDecorators": true,
    "moduleResolution": "node",
    "importHelpers": true,
    "target": "ES2022",
    "module": "ES2022",
    "useDefineForClassFields": false,
    "lib": [
      "ES2022",
      "dom"
    ]
  },
  "angularCompilerOptions": {
    "enableI18nLegacyMessageIdFormat": false,
    "strictInjectionParameters": true,
    "strictInputAccessModifiers": true,
    "strictTemplates": true
  }
}""",
            "tsconfig.app.json": """{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "outDir": "./out-tsc/app",
    "types": []
  },
  "files": [
    "src/main.ts"
  ],
  "include": [
    "src/**/*.d.ts"
  ]
}""",
            ".gitignore": """# Compiled output
/dist
/tmp
/out-tsc
/bazel-out

# Node
/node_modules
npm-debug.log
yarn-error.log

# IDEs and editors
.idea/
.project
.classpath
.c9/
*.launch
.settings/
*.sublime-workspace

# Visual Studio Code
.vscode/*
!.vscode/settings.json
!.vscode/tasks.json
!.vscode/launch.json
!.vscode/extensions.json
.history/*

# Miscellaneous
/.angular/cache
.sass-cache/
/connect.lock
/coverage
/libpeerconnection.log
testem.log
/typings

# System files
.DS_Store
Thumbs.db""",
            "README.md": """# AngularApp

This project was generated with [Angular CLI](https://github.com/angular/angular-cli).

## Development server

Run `ng serve` for a dev server. Navigate to `http://localhost:4200/`. The application will automatically reload if you change any of the source files.

## Code scaffolding

Run `ng generate component component-name` to generate a new component. You can also use `ng generate directive|pipe|service|class|guard|interface|enum|module`.

## Build

Run `ng build` to build the project. The build artifacts will be stored in the `dist/` directory.

## Running unit tests

Run `ng test` to execute the unit tests via [Karma](https://karma-runner.github.io).

## Running end-to-end tests

Run `ng e2e` to execute the end-to-end tests via a platform of your choice. To use this command, you need to first add a package that implements end-to-end testing capabilities.

## Further help

To get more help on the Angular CLI use `ng help` or go check out the [Angular CLI Overview and Command Reference](https://angular.io/cli) page.
""",
        }

    def get_package_json(self) -> Dict[str, Any]:
        """Get Angular package.json configuration."""
        return {
            "name": "angular-app",
            "version": "0.0.0",
            "scripts": {
                "ng": "ng",
                "start": "ng serve",
                "build": "ng build",
                "watch": "ng build --watch --configuration development",
                "test": "ng test",
            },
            "private": True,
            "dependencies": {
                "@angular/animations": "^20.0.0",
                "@angular/common": "^20.0.0",
                "@angular/compiler": "^20.0.0",
                "@angular/core": "^20.0.0",
                "@angular/forms": "^20.0.0",
                "@angular/platform-browser": "^20.0.0",
                "@angular/platform-browser-dynamic": "^20.0.0",
                "@angular/router": "^20.0.0",
                "rxjs": "~7.8.0",
                "tslib": "^2.3.0",
                "zone.js": "~0.15.0",
            },
            "devDependencies": {
                "@angular-devkit/build-angular": "^20.0.0",
                "@angular/cli": "^20.0.0",
                "@angular/compiler-cli": "^20.0.0",
                "@types/jasmine": "~5.1.0",
                "jasmine-core": "~5.1.0",
                "karma": "~6.4.0",
                "karma-chrome-launcher": "~3.2.0",
                "karma-coverage": "~2.2.0",
                "karma-jasmine": "~5.1.0",
                "karma-jasmine-html-reporter": "~2.1.0",
                "typescript": "~5.6.0",
            },
            "engines": {"node": ">=22.0.0"},
        }

    def get_build_command(self) -> List[str]:
        """Get Angular build command."""
        return ["npm", "run", "build"]

    def get_dev_command(self) -> List[str]:
        """Get Angular dev server command."""
        return ["npm", "start"]

    def get_install_command(self) -> List[str]:
        """Get dependency installation command."""
        return ["npm", "install"]

    @property
    def default_port(self) -> int:
        """Angular dev server default port."""
        return 4200

    @property
    def build_dir(self) -> str:
        """Angular build output directory."""
        return "dist"

    def _add_port_to_command(self, cmd: List[str], port: int) -> List[str]:
        """Add port configuration to Angular dev command."""
        if "start" in cmd or "ng" in cmd:
            return cmd + ["--port", str(port)]
        return cmd

    def _validate_framework_specific(self, project_dir: Path) -> List[str]:
        """Validate Angular-specific requirements."""
        errors = []

        # Check for required Angular files
        required_files = ["angular.json", "src/main.ts", "src/app/app.component.ts"]

        for file_path in required_files:
            if not (project_dir / file_path).exists():
                errors.append(f"Required Angular file missing: {file_path}")

        return errors

    def create_app_component(
        self, template_content: str, style_content: str = ""
    ) -> str:
        """Create the main App component."""
        return f"""import {{ Component }} from '@angular/core';

@Component({{
  selector: 'app-root',
  standalone: true,
  imports: [],
  template: `
    {template_content}
  `,
  styles: [`
    {style_content}
  `]
}})
export class AppComponent {{
  title = 'angular-app';
}}"""

    def create_component(
        self, name: str, selector: str, template_content: str, style_content: str = ""
    ) -> str:
        """Create an Angular component."""
        class_name = (
            "".join([word.capitalize() for word in name.split("-")]) + "Component"
        )

        return f"""import {{ Component }} from '@angular/core';

@Component({{
  selector: '{selector}',
  standalone: true,
  imports: [],
  template: `
    {template_content}
  `,
  styles: [`
    {style_content}
  `]
}})
export class {class_name} {{
  // Component logic here
}}"""
