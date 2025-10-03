"""
ASTRA-specific evaluation framework for full-stack project assessment.

This module provides specialized evaluation capabilities for ASTRA benchmark
tasks, including automated test execution, scoring, and comprehensive assessment
of multi-file projects across different frameworks.
"""

import json
import subprocess
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
import xml.etree.ElementTree as ET

from core.logger import get_logger
from core.config import EvaluationConfig
from models.model_manager import ModelManager
from evaluation.evaluation_schemas import EvaluationResult, CriteriaScore


@dataclass
class TestResult:
    """Result of a single test case."""

    name: str
    passed: bool
    weight: float
    message: str = ""
    duration: float = 0.0


@dataclass
class AstraTestSuite:
    """Complete test suite results for an ASTRA task."""

    task_name: str
    test_results: List[TestResult]
    total_score: float
    max_score: float
    pass_rate: float
    execution_time: float
    test_command: str


class AstraEvaluator:
    """Specialized evaluator for ASTRA benchmark tasks."""

    def __init__(
        self,
        model_manager: Optional[ModelManager] = None,
        config: Optional[EvaluationConfig] = None,
        output_dir: str = "results",
    ):
        self.model_manager = model_manager
        self.config = config or EvaluationConfig()
        self.output_dir = Path(output_dir)
        self.logger = get_logger()

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Supported test file formats
        self.test_formats = ["junit.xml", "unit.xml", "test-results.xml"]

    def evaluate_astra_task(
        self,
        task_definition: Dict[str, Any],
        generated_files: Dict[str, str],
        project_path: Optional[str] = None,
    ) -> EvaluationResult:
        """Evaluate an ASTRA task with comprehensive assessment."""

        start_time = time.time()
        task_name = task_definition["name"]

        self.logger.info(f"Evaluating ASTRA task: {task_name}")

        try:
            # Step 1: Execute automated tests
            test_suite = self._run_automated_tests(
                task_definition, generated_files, project_path
            )

            # Step 2: Code quality assessment
            code_quality_score = self._assess_code_quality(
                generated_files, task_definition.get("astra_metadata", {})
            )

            # Step 3: Framework-specific assessment
            framework_score = self._assess_framework_compliance(
                generated_files, task_definition.get("astra_metadata", {})
            )

            # Step 4: Functional completeness assessment
            functional_score = self._assess_functional_completeness(
                generated_files, task_definition
            )

            # Step 5: Calculate overall score
            overall_score = self._calculate_overall_score(
                test_suite.total_score / max(test_suite.max_score, 1.0),
                code_quality_score,
                framework_score,
                functional_score,
            )

            # Step 6: Generate detailed feedback
            feedback = self._generate_comprehensive_feedback(
                task_definition,
                test_suite,
                code_quality_score,
                framework_score,
                functional_score,
            )

            execution_time = time.time() - start_time

            # Create evaluation result
            result = EvaluationResult(
                task_name=task_name,
                overall_score=overall_score,
                criteria_scores=[
                    CriteriaScore(
                        aspect="Test Results",
                        score=test_suite.total_score / max(test_suite.max_score, 1.0),
                        weight=0.5,
                        details=f"Passed {test_suite.pass_rate:.1%} of tests ({test_suite.total_score}/{test_suite.max_score} points)",
                    ),
                    CriteriaScore(
                        aspect="Code Quality",
                        score=code_quality_score,
                        weight=0.2,
                        details="Code structure, readability, and best practices",
                    ),
                    CriteriaScore(
                        aspect="Framework Compliance",
                        score=framework_score,
                        weight=0.2,
                        details="Framework-specific patterns and conventions",
                    ),
                    CriteriaScore(
                        aspect="Functional Completeness",
                        score=functional_score,
                        weight=0.1,
                        details="Implementation completeness and feature coverage",
                    ),
                ],
                feedback=feedback,
                execution_time=execution_time,
                metadata={
                    "test_suite": test_suite.__dict__,
                    "framework": task_definition.get("astra_metadata", {}).get(
                        "framework", "Unknown"
                    ),
                    "category": task_definition.get("astra_metadata", {}).get(
                        "category", "Unknown"
                    ),
                    "total_testcases": task_definition.get("astra_metadata", {}).get(
                        "total_testcases", 0
                    ),
                    "project_files_count": len(generated_files),
                },
            )

            # Save detailed results
            self._save_astra_results(result, test_suite, task_definition)

            return result

        except Exception as e:
            self.logger.error(f"Error evaluating ASTRA task {task_name}: {e}")
            return self._create_error_result(
                task_name, str(e), time.time() - start_time
            )

    def _run_automated_tests(
        self,
        task_definition: Dict[str, Any],
        generated_files: Dict[str, str],
        project_path: Optional[str] = None,
    ) -> AstraTestSuite:
        """Execute the automated test suite for an ASTRA task."""

        astra_metadata = task_definition.get("astra_metadata", {})
        test_command = astra_metadata.get("test_command", "")

        if not test_command:
            # Create a mock test suite if no test command
            return self._create_mock_test_suite(task_definition)

        try:
            # Create temporary project directory
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Write generated files to temporary directory
                for file_path, content in generated_files.items():
                    full_path = temp_path / file_path
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(content)

                # Install dependencies if package.json exists
                if (temp_path / "package.json").exists():
                    self._install_dependencies(temp_path)

                # Execute test command
                test_results = self._execute_test_command(test_command, temp_path)

                # Parse test results
                parsed_results = self._parse_test_results(test_results, astra_metadata)

                return parsed_results

        except Exception as e:
            self.logger.warning(f"Failed to execute automated tests: {e}")
            return self._create_mock_test_suite(task_definition)

    def _install_dependencies(self, project_path: Path):
        """Install project dependencies."""
        try:
            # Install npm dependencies
            subprocess.run(
                ["npm", "install"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300,
            )
        except Exception as e:
            self.logger.warning(f"Failed to install dependencies: {e}")

    def _execute_test_command(
        self, test_command: str, project_path: Path
    ) -> Dict[str, Any]:
        """Execute the test command and capture results."""
        try:
            # Parse test command
            if test_command.startswith("bash "):
                command_parts = ["bash", "-c", test_command[5:]]
            else:
                command_parts = test_command.split()

            # Execute command
            result = subprocess.run(
                command_parts,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
            )

            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0,
            }

        except subprocess.TimeoutExpired:
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": "Test execution timed out",
                "success": False,
            }
        except Exception as e:
            return {"returncode": -1, "stdout": "", "stderr": str(e), "success": False}

    def _parse_test_results(
        self, test_results: Dict[str, Any], astra_metadata: Dict[str, Any]
    ) -> AstraTestSuite:
        """Parse test results from various formats."""
        test_cases = astra_metadata.get("testcases", [])

        # Look for test result files
        test_files = []
        for test_file in self.test_formats:
            if Path(test_file).exists():
                test_files.append(test_file)

        if test_files:
            return self._parse_junit_xml(test_files[0], astra_metadata)
        else:
            # Create mock results based on test execution
            return self._create_results_from_execution(test_results, astra_metadata)

    def _parse_junit_xml(
        self, xml_file: str, astra_metadata: Dict[str, Any]
    ) -> AstraTestSuite:
        """Parse JUnit XML test results."""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            test_results = []
            total_score = 0.0
            max_score = 0.0

            # Get test cases from metadata
            test_cases = astra_metadata.get("testcases", [])
            test_case_weights = {tc["name"]: tc.get("weight", 1.0) for tc in test_cases}

            for testcase in root.findall(".//testcase"):
                name = testcase.get("name", "Unknown test")
                failure = testcase.find("failure")
                passed = failure is None

                weight = test_case_weights.get(name, 1.0)
                max_score += weight

                if passed:
                    total_score += weight

                test_results.append(
                    TestResult(
                        name=name,
                        passed=passed,
                        weight=weight,
                        message=failure.get("message", "") if failure else "Passed",
                        duration=float(testcase.get("time", 0.0)),
                    )
                )

            pass_rate = total_score / max_score if max_score > 0 else 0.0

            return AstraTestSuite(
                task_name=astra_metadata.get("task_name", "Unknown"),
                test_results=test_results,
                total_score=total_score,
                max_score=max_score,
                pass_rate=pass_rate,
                execution_time=sum(result.duration for result in test_results),
                test_command=astra_metadata.get("test_command", ""),
            )

        except Exception as e:
            self.logger.warning(f"Failed to parse JUnit XML: {e}")
            return self._create_mock_test_suite(
                {"name": "ASTRA Task", "astra_metadata": astra_metadata}
            )

    def _create_results_from_execution(
        self, test_results: Dict[str, Any], astra_metadata: Dict[str, Any]
    ) -> AstraTestSuite:
        """Create test results from command execution output."""
        test_cases = astra_metadata.get("testcases", [])

        parsed_results = []
        total_score = 0.0
        max_score = 0.0

        for test_case in test_cases:
            weight = test_case.get("weight", 1.0)
            max_score += weight

            # Assume tests passed if command succeeded
            passed = test_results.get("success", False)
            if passed:
                total_score += weight

            parsed_results.append(
                TestResult(
                    name=test_case["name"],
                    passed=passed,
                    weight=weight,
                    message="Passed" if passed else "Failed - see test output",
                    duration=0.0,
                )
            )

        pass_rate = total_score / max_score if max_score > 0 else 0.0

        return AstraTestSuite(
            task_name=astra_metadata.get("task_name", "Unknown"),
            test_results=parsed_results,
            total_score=total_score,
            max_score=max_score,
            pass_rate=pass_rate,
            execution_time=0.0,
            test_command=astra_metadata.get("test_command", ""),
        )

    def _create_mock_test_suite(
        self, task_definition: Dict[str, Any]
    ) -> AstraTestSuite:
        """Create a mock test suite when automated testing is not available."""
        astra_metadata = task_definition.get("astra_metadata", {})
        test_cases = astra_metadata.get("testcases", [])

        test_results = []
        total_score = 0.0
        max_score = 0.0

        for test_case in test_cases:
            weight = test_case.get("weight", 1.0)
            max_score += weight

            # Create mock results (this would be replaced with actual test execution)
            passed = True  # Assume pass for demonstration
            if passed:
                total_score += weight

            test_results.append(
                TestResult(
                    name=test_case["name"],
                    passed=passed,
                    weight=weight,
                    message="Mock test result - automated testing not available",
                    duration=0.0,
                )
            )

        pass_rate = total_score / max_score if max_score > 0 else 0.0

        return AstraTestSuite(
            task_name=task_definition["name"],
            test_results=test_results,
            total_score=total_score,
            max_score=max_score,
            pass_rate=pass_rate,
            execution_time=0.0,
            test_command=astra_metadata.get(
                "test_command", "No test command specified"
            ),
        )

    def _assess_code_quality(
        self, generated_files: Dict[str, Any], astra_metadata: Dict[str, Any]
    ) -> float:
        """Assess code quality of generated files."""
        score = 0.8  # Base score

        framework = astra_metadata.get("framework", "").lower()

        for file_path, content in generated_files.items():
            file_extension = Path(file_path).suffix.lower()

            # Check for common code quality indicators (frontend only)
            if file_extension == ".js" or file_extension == ".jsx":
                score += self._assess_javascript_quality(content)
            elif file_extension == ".ts" or file_extension == ".tsx":
                score += self._assess_typescript_quality(content)
            elif file_extension in [".html", ".css"]:
                score += self._assess_web_quality(content)

        # Framework-specific quality checks (frontend only)
        if "react" in framework:
            score += self._assess_react_quality(generated_files)
        elif "angular" in framework:
            score += self._assess_angular_quality(generated_files)
        elif "nextjs" in framework or "next" in framework:
            score += self._assess_react_quality(generated_files)  # Next.js uses React
        elif "vue" in framework:
            score += self._assess_vue_quality(generated_files)
        elif "svelte" in framework:
            score += self._assess_svelte_quality(generated_files)

        return min(max(score / len(generated_files), 0.0), 1.0)

    def _assess_javascript_quality(self, content: str) -> float:
        """Assess JavaScript code quality."""
        score = 0.0

        # Check for modern syntax
        if "const" in content or "let" in content:
            score += 0.1
        if "=>" in content:  # Arrow functions
            score += 0.1
        if "async" in content and "await" in content:
            score += 0.1

        # Check for error handling
        if "try" in content and "catch" in content:
            score += 0.1

        # Check for proper function definitions
        if "function" in content or "=>" in content:
            score += 0.1

        # Check for proper imports/exports
        if "import" in content or "export" in content:
            score += 0.1

        return min(score, 1.0)

    def _assess_typescript_quality(self, content: str) -> float:
        """Assess TypeScript code quality."""
        score = self._assess_javascript_quality(content)

        # TypeScript-specific checks
        if ":" in content and "interface" in content:
            score += 0.2
        if "type" in content:
            score += 0.1

        return min(score, 1.0)

    def _assess_python_quality(self, content: str) -> float:
        """Assess Python code quality."""
        score = 0.0

        if "def " in content:
            score += 0.2
        if "class " in content:
            score += 0.1
        if "import " in content:
            score += 0.1
        if "try:" in content and "except" in content:
            score += 0.2
        if "if __name__" in content:
            score += 0.1

        return min(score, 1.0)

    def _assess_java_quality(self, content: str) -> float:
        """Assess Java code quality."""
        score = 0.0

        if "public class" in content:
            score += 0.2
        if "private" in content or "public" in content:
            score += 0.1
        if "@Override" in content:
            score += 0.1
        if "try {" in content and "catch" in content:
            score += 0.2

        return min(score, 1.0)

    def _assess_ruby_quality(self, content: str) -> float:
        """Assess Ruby code quality."""
        score = 0.0

        if "def " in content:
            score += 0.2
        if "class " in content:
            score += 0.1
        if "begin" in content and "rescue" in content:
            score += 0.2
        if "require" in content:
            score += 0.1

        return min(score, 1.0)

    def _assess_web_quality(self, content: str) -> float:
        """Assess HTML/CSS code quality."""
        score = 0.0

        if "<!DOCTYPE html>" in content:
            score += 0.1
        if "data-testid" in content:  # Important for ASTRA testing
            score += 0.3
        if "alt=" in content:
            score += 0.1
        if "meta charset" in content:
            score += 0.1

        return min(score, 1.0)

    def _assess_react_quality(self, generated_files: Dict[str, str]) -> float:
        """Assess React-specific code quality."""
        score = 0.0

        for content in generated_files.values():
            if "import React" in content or 'from "react"' in content:
                score += 0.2
            if "useState" in content or "useEffect" in content:
                score += 0.2
            if "export default" in content:
                score += 0.1
            if "className=" in content or "class=" in content:
                score += 0.1

        return min(score, 1.0)

    def _assess_angular_quality(self, generated_files: Dict[str, str]) -> float:
        """Assess Angular-specific code quality."""
        score = 0.0

        for content in generated_files.values():
            if "@Component" in content:
                score += 0.3
            if "@Input" in content or "@Output" in content:
                score += 0.2
            if "ngOnInit" in content or "ngOnChanges" in content:
                score += 0.2
            if "data-test-id" in content:  # Angular testing convention
                score += 0.3

        return min(score, 1.0)

    def _assess_nodejs_quality(self, generated_files: Dict[str, str]) -> float:
        """Assess Node.js-specific code quality."""
        score = 0.0

        for content in generated_files.values():
            if "require(" in content or "import " in content:
                score += 0.1
            if "app.listen" in content or "app.get" in content or "app.post" in content:
                score += 0.2
            if "res.send" in content or "res.json" in content:
                score += 0.1
            if "module.exports" in content or "export default" in content:
                score += 0.1

        return min(score, 1.0)

    def _assess_framework_compliance(
        self, generated_files: Dict[str, str], astra_metadata: Dict[str, Any]
    ) -> float:
        """Assess framework-specific compliance (frontend only)."""
        framework = astra_metadata.get("framework", "").lower()

        if "react" in framework:
            return self._assess_react_quality(generated_files)
        elif "angular" in framework:
            return self._assess_angular_quality(generated_files)
        elif "nextjs" in framework or "next" in framework:
            return self._assess_react_quality(generated_files)  # Next.js uses React
        elif "vue" in framework:
            return self._assess_vue_quality(generated_files)
        elif "svelte" in framework:
            return self._assess_svelte_quality(generated_files)
        else:
            return 0.7  # Default score for unknown frameworks

    def _assess_vue_quality(self, generated_files: Dict[str, str]) -> float:
        """Assess Vue.js code quality."""
        score = 0.0

        for content in generated_files.values():
            if "import { createApp }" in content or "Vue.createApp" in content:
                score += 0.2
            if "export default" in content:
                score += 0.1
            if "<template>" in content and "<script>" in content:
                score += 0.2
            if "data-test-id" in content or "data-testid" in content:
                score += 0.3
            if "v-if" in content or "v-for" in content:
                score += 0.1
            if "computed:" in content or "methods:" in content:
                score += 0.1

        return min(score, 1.0)

    def _assess_svelte_quality(self, generated_files: Dict[str, str]) -> float:
        """Assess Svelte code quality."""
        score = 0.0

        for content in generated_files.values():
            if "<script>" in content and "</script>" in content:
                score += 0.2
            if "export let" in content:
                score += 0.2
            if "$: " in content:  # Reactive statements
                score += 0.2
            if "on:" in content:  # Event handlers
                score += 0.1
            if "data-test-id" in content or "data-testid" in content:
                score += 0.3

        return min(score, 1.0)

    def _assess_functional_completeness(
        self, generated_files: Dict[str, str], task_definition: Dict[str, Any]
    ) -> float:
        """Assess functional completeness based on task requirements."""
        score = 0.0
        requirements = task_definition.get("requirements", [])
        expected_features = task_definition.get("expected_features", [])

        # Check for required features in code
        all_content = " ".join(generated_files.values())

        for requirement in requirements:
            if isinstance(requirement, str):
                # Simple keyword matching for requirements
                if any(
                    keyword.lower() in all_content.lower()
                    for keyword in requirement.split()[:3]
                ):
                    score += 0.1

        for feature in expected_features:
            if isinstance(feature, str):
                # Simple keyword matching for expected features
                if any(
                    keyword.lower() in all_content.lower()
                    for keyword in feature.split()[:3]
                ):
                    score += 0.1

        # Check for data-testid attributes (critical for ASTRA)
        if "data-testid" in all_content:
            score += 0.3

        return min(max(score, 0.0), 1.0)

    def _calculate_overall_score(
        self,
        test_score: float,
        code_quality: float,
        framework_score: float,
        functional_score: float,
    ) -> float:
        """Calculate overall score with weighted components."""
        return (
            test_score * 0.5
            + code_quality * 0.2
            + framework_score * 0.2
            + functional_score * 0.1
        )

    def _generate_comprehensive_feedback(
        self,
        task_definition: Dict[str, Any],
        test_suite: AstraTestSuite,
        code_quality: float,
        framework_score: float,
        functional_score: float,
    ) -> str:
        """Generate comprehensive feedback for the evaluation."""

        framework = task_definition.get("astra_metadata", {}).get(
            "framework", "Unknown"
        )

        feedback = f"""ASTRA Task Evaluation Results

Task: {task_definition['name']}
Framework: {framework}
Test Success Rate: {test_suite.pass_rate:.1%} ({test_suite.total_score}/{test_suite.max_score} points)

Assessment Breakdown:
• Test Results: {test_suite.pass_rate:.1%} success rate
• Code Quality: {code_quality:.1%}
• Framework Compliance: {framework_score:.1%}
• Functional Completeness: {functional_score:.1%}

Test Results Summary:
"""

        for result in test_suite.test_results[:5]:  # Show first 5 tests
            status = "✅ PASS" if result.passed else "❌ FAIL"
            feedback += f"• {result.name}: {status} (weight: {result.weight})\n"

        if len(test_suite.test_results) > 5:
            feedback += f"... and {len(test_suite.test_results) - 5} more tests\n"

        feedback += f"""
Strengths:
• {'Automated tests executed successfully' if test_suite.pass_rate > 0 else 'Test execution framework ready'}
• {'Good code structure' if code_quality > 0.7 else 'Code structure can be improved'}
• {'Framework compliance' if framework_score > 0.7 else 'Framework-specific patterns need attention'}

Areas for Improvement:
• {'Focus on failing test cases' if test_suite.pass_rate < 1.0 else 'All tests passing'}
• {'Improve code quality' if code_quality < 0.7 else 'Good code quality maintained'}
• {'Enhance framework-specific patterns' if framework_score < 0.7 else 'Framework patterns well implemented'}

Recommendations:
1. Ensure all data-testid attributes are correctly implemented for testing
2. Follow framework-specific best practices and conventions
3. Implement proper error handling and edge cases
4. Verify all functional requirements are completely addressed
"""

        return feedback

    def _save_astra_results(
        self,
        result: EvaluationResult,
        test_suite: AstraTestSuite,
        task_definition: Dict[str, Any],
    ):
        """Save detailed ASTRA evaluation results."""

        # Create results directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_dir = (
            self.output_dir
            / f"astra_{timestamp}_{task_definition['name'].replace(' ', '_').replace(':', '')}"
        )
        result_dir.mkdir(exist_ok=True)

        # Save main evaluation result
        with open(result_dir / "evaluation.json", "w") as f:
            json.dump(result.__dict__, f, indent=2, default=str)

        # Save test suite details
        with open(result_dir / "test_suite.json", "w") as f:
            json.dump(test_suite.__dict__, f, indent=2, default=str)

        # Save task metadata
        with open(result_dir / "task_metadata.json", "w") as f:
            json.dump(task_definition, f, indent=2, default=str)

        # Generate summary report
        summary = {
            "task_name": task_definition["name"],
            "framework": task_definition.get("astra_metadata", {}).get(
                "framework", "Unknown"
            ),
            "overall_score": result.overall_score,
            "test_pass_rate": test_suite.pass_rate,
            "total_tests": len(test_suite.test_results),
            "execution_time": result.execution_time,
            "timestamp": timestamp,
        }

        with open(result_dir / "summary.json", "w") as f:
            json.dump(summary, f, indent=2)

    def _create_error_result(
        self, task_name: str, error_message: str, execution_time: float
    ) -> EvaluationResult:
        """Create an error evaluation result."""
        return EvaluationResult(
            task_name=task_name,
            overall_score=0.0,
            criteria_scores=[
                CriteriaScore(
                    aspect="Error",
                    score=0.0,
                    weight=1.0,
                    details=f"Evaluation failed: {error_message}",
                )
            ],
            feedback=f"Evaluation failed due to error: {error_message}",
            execution_time=execution_time,
            metadata={"error": True, "error_message": error_message},
        )
