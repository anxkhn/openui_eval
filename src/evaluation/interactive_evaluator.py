"""
Interactive Task Evaluator for testing dynamic web applications.

This module provides functionality to evaluate interactive web tasks
that require user interactions beyond static HTML/CSS rendering.
"""

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException


@dataclass
class InteractionStep:
    """Definition of a single interaction step."""

    step_name: str
    action: str  # click, fill_form, navigate, verify_element, wait
    selector: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    expected: Optional[str] = None
    timeout: int = 10
    description: str = ""


@dataclass
class InteractionProfile:
    """Profile defining how to test an interactive task."""

    task_name: str
    interaction_type: (
        str  # form_submission, navigation, simple_interaction, complex_stateful
    )
    steps: List[InteractionStep] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    base_url: str = "http://localhost:3000"
    setup_steps: List[InteractionStep] = field(default_factory=list)
    cleanup_steps: List[InteractionStep] = field(default_factory=list)


@dataclass
class InteractionResult:
    """Result of an interaction evaluation."""

    task_name: str
    success: bool
    total_steps: int
    completed_steps: int
    step_results: List[Dict[str, Any]]
    functional_score: float
    usability_score: float
    error_handling_score: float
    performance_score: float
    total_score: float
    errors: List[str]
    execution_time: float
    screenshots: List[str]  # Paths to screenshots taken during evaluation


class InteractiveEvaluator:
    """Evaluates interactive web tasks using browser automation."""

    def __init__(self, headless: bool = True, screenshot_dir: str = "screenshots"):
        self.headless = headless
        self.screenshot_dir = Path(screenshot_dir)
        self.screenshot_dir.mkdir(exist_ok=True)
        self.driver: Optional[webdriver.Chrome] = None
        self.wait_timeout = 10

    def _setup_driver(self) -> webdriver.Chrome:
        """Initialize Chrome WebDriver with appropriate options."""
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument("--headless")

        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")

        # Allow file access
        chrome_options.add_argument("--allow-file-access-from-files")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(self.wait_timeout)

        return self.driver

    def _take_screenshot(self, name: str) -> str:
        """Take a screenshot and return the file path."""
        if not self.driver:
            return ""

        timestamp = int(time.time())
        filename = f"{name}_{timestamp}.png"
        filepath = self.screenshot_dir / filename

        try:
            self.driver.save_screenshot(str(filepath))
            return str(filepath)
        except Exception as e:
            print(f"Failed to take screenshot {name}: {e}")
            return ""

    def _execute_step(self, step: InteractionStep) -> Dict[str, Any]:
        """Execute a single interaction step and return the result."""
        result = {
            "step_name": step.step_name,
            "action": step.action,
            "success": False,
            "error": None,
            "execution_time": 0,
            "screenshot": None,
        }

        start_time = time.time()

        try:
            if step.action == "navigate":
                if step.selector:
                    self.driver.get(step.selector)
                else:
                    # Navigate to base URL
                    self.driver.get("file://" + str(Path.cwd() / "index.html"))

                result["success"] = True

            elif step.action == "click":
                if not step.selector:
                    raise ValueError("Click action requires a selector")

                element = WebDriverWait(self.driver, step.timeout).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, step.selector))
                )
                element.click()
                result["success"] = True

            elif step.action == "fill_form":
                if not step.selector or not step.data:
                    raise ValueError("Fill form action requires selector and data")

                # Find form and fill fields
                form = self.driver.find_element(By.CSS_SELECTOR, step.selector)

                for field_name, field_value in step.data.items():
                    try:
                        # Try different field identification strategies
                        field = form.find_element(By.NAME, field_name)
                    except NoSuchElementException:
                        try:
                            field = form.find_element(By.ID, field_name)
                        except NoSuchElementException:
                            field = form.find_element(
                                By.CSS_SELECTOR,
                                f"[name='{field_name}'], [id='{field_name}']",
                            )

                    field.clear()
                    field.send_keys(str(field_value))

                result["success"] = True

            elif step.action == "verify_element":
                if not step.selector:
                    raise ValueError("Verify element action requires a selector")

                element = WebDriverWait(self.driver, step.timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, step.selector))
                )

                # Check expected content if provided
                if step.expected:
                    element_text = element.text
                    if step.expected.lower() in element_text.lower():
                        result["success"] = True
                    else:
                        result["success"] = False
                        result["error"] = (
                            f"Expected '{step.expected}' but found '{element_text}'"
                        )
                else:
                    result["success"] = True

            elif step.action == "wait":
                if step.expected:
                    # Wait for specific condition
                    WebDriverWait(self.driver, step.timeout).until(
                        lambda driver: step.expected.lower()
                        in driver.page_source.lower()
                    )
                else:
                    # Simple wait
                    time.sleep(step.timeout)
                result["success"] = True

            else:
                result["error"] = f"Unknown action: {step.action}"

        except TimeoutException as e:
            result["error"] = f"Timeout after {step.timeout}s: {str(e)}"
        except Exception as e:
            result["error"] = f"Step execution failed: {str(e)}"

        result["execution_time"] = time.time() - start_time
        result["screenshot"] = self._take_screenshot(f"step_{step.step_name}")

        return result

    def evaluate_task(
        self, profile: InteractionProfile, generated_files: Dict[str, str]
    ) -> InteractionResult:
        """Evaluate an interactive task using its interaction profile."""
        if not self.driver:
            self._setup_driver()

        start_time = time.time()
        step_results = []
        errors = []

        try:
            # Execute setup steps
            for step in profile.setup_steps:
                result = self._execute_step(step)
                step_results.append(result)
                if not result["success"]:
                    errors.append(f"Setup failed: {step.step_name} - {result['error']}")

            # Execute main interaction steps
            completed_steps = 0
            for step in profile.steps:
                result = self._execute_step(step)
                step_results.append(result)

                if result["success"]:
                    completed_steps += 1
                else:
                    errors.append(f"Step failed: {step.step_name} - {result['error']}")
                    # Continue execution for debugging purposes

            # Execute cleanup steps
            for step in profile.cleanup_steps:
                result = self._execute_step(step)
                step_results.append(result)
                if not result["success"]:
                    errors.append(
                        f"Cleanup failed: {step.step_name} - {result['error']}"
                    )

            # Calculate scores
            functional_score = (
                completed_steps / len(profile.steps) if profile.steps else 0.0
            )
            usability_score = self._calculate_usability_score(step_results)
            error_handling_score = self._calculate_error_handling_score(
                step_results, errors
            )
            performance_score = self._calculate_performance_score(step_results)
            total_score = (
                functional_score * 0.5
                + usability_score * 0.3
                + error_handling_score * 0.15
                + performance_score * 0.05
            )

            success = functional_score >= 0.8 and len(errors) == 0

        except Exception as e:
            errors.append(f"Evaluation failed: {str(e)}")
            functional_score = usability_score = error_handling_score = (
                performance_score
            ) = total_score = 0.0
            success = False
            completed_steps = 0

        execution_time = time.time() - start_time

        return InteractionResult(
            task_name=profile.task_name,
            success=success,
            total_steps=len(profile.steps),
            completed_steps=completed_steps,
            step_results=step_results,
            functional_score=functional_score,
            usability_score=usability_score,
            error_handling_score=error_handling_score,
            performance_score=performance_score,
            total_score=total_score,
            errors=errors,
            execution_time=execution_time,
            screenshots=[
                r.get("screenshot") for r in step_results if r.get("screenshot")
            ],
        )

    def _calculate_usability_score(self, step_results: List[Dict[str, Any]]) -> float:
        """Calculate usability score based on execution time and error patterns."""
        if not step_results:
            return 0.0

        # Check for timeouts and slow interactions
        timeouts = sum(1 for r in step_results if "Timeout" in str(r.get("error", "")))
        slow_steps = sum(1 for r in step_results if r.get("execution_time", 0) > 5.0)

        # Base score affected by timeouts and slow interactions
        base_score = 1.0
        timeout_penalty = (timeouts / len(step_results)) * 0.5
        slowness_penalty = (slow_steps / len(step_results)) * 0.2

        return max(0.0, base_score - timeout_penalty - slowness_penalty)

    def _calculate_error_handling_score(
        self, step_results: List[Dict[str, Any]], errors: List[str]
    ) -> float:
        """Calculate error handling score."""
        if not step_results:
            return 0.0

        total_steps = len(step_results)
        failed_steps = sum(1 for r in step_results if not r.get("success", False))

        # Perfect score if no failures, decreasing based on failure rate
        if failed_steps == 0:
            return 1.0

        # Check if errors are handled gracefully (not crashes)
        crash_errors = sum(
            1
            for error in errors
            if "crash" in error.lower() or "fatal" in error.lower()
        )

        if crash_errors > 0:
            return max(0.0, 1.0 - (crash_errors / total_steps))
        else:
            return max(0.5, 1.0 - (failed_steps / total_steps) * 0.5)

    def _calculate_performance_score(self, step_results: List[Dict[str, Any]]) -> float:
        """Calculate performance score based on execution times."""
        if not step_results:
            return 0.0

        execution_times = [r.get("execution_time", 0) for r in step_results]
        avg_time = sum(execution_times) / len(execution_times)

        # Score based on average execution time (faster is better)
        if avg_time < 1.0:
            return 1.0
        elif avg_time < 3.0:
            return 0.8
        elif avg_time < 5.0:
            return 0.6
        elif avg_time < 10.0:
            return 0.4
        else:
            return 0.2

    def close(self):
        """Clean up resources."""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Utility functions for creating interaction profiles from WebGen-Bench tasks
def create_form_interaction_profile(task_data: Dict[str, Any]) -> InteractionProfile:
    """Create an interaction profile for form-based tasks."""
    task_name = task_data["name"]
    webgen_meta = task_data.get("webgen_metadata", {})
    eval_tasks = webgen_meta.get("evaluation_tasks", [])

    steps = []

    # Find form-related evaluation tasks
    form_tasks = [
        t
        for t in eval_tasks
        if any(
            keyword in t["task"].lower()
            for keyword in ["form", "submit", "input", "fill"]
        )
    ]

    if form_tasks:
        for i, form_task in enumerate(form_tasks[:3]):  # Limit to 3 steps
            steps.append(
                InteractionStep(
                    step_name=f"form_step_{i+1}",
                    action="verify_element",  # Start with verification, can be enhanced later
                    selector="form, .form, #form",  # Generic form selector
                    expected=form_task["expected"][:50],  # Extract expected outcome
                    description=form_task["task"],
                )
            )

    return InteractionProfile(
        task_name=task_name,
        interaction_type="form_submission",
        steps=steps,
        success_criteria=["form_accessible", "validation_works"],
    )


def create_navigation_interaction_profile(
    task_data: Dict[str, Any],
) -> InteractionProfile:
    """Create an interaction profile for navigation-based tasks."""
    task_name = task_data["name"]
    webgen_meta = task_data.get("webgen_metadata", {})
    eval_tasks = webgen_meta.get("evaluation_tasks", [])

    steps = []

    # Find navigation-related evaluation tasks
    nav_tasks = [
        t
        for t in eval_tasks
        if any(
            keyword in t["task"].lower()
            for keyword in ["navigate", "click", "page", "link"]
        )
    ]

    if nav_tasks:
        for i, nav_task in enumerate(nav_tasks[:3]):  # Limit to 3 steps
            steps.append(
                InteractionStep(
                    step_name=f"nav_step_{i+1}",
                    action="verify_element",
                    selector="nav, .nav, .navigation, a, button",  # Generic navigation selector
                    expected=nav_task["expected"][:50],
                    description=nav_task["task"],
                )
            )

    return InteractionProfile(
        task_name=task_name,
        interaction_type="navigation",
        steps=steps,
        success_criteria=["navigation_works", "pages_accessible"],
    )


def create_simple_interaction_profile(task_data: Dict[str, Any]) -> InteractionProfile:
    """Create an interaction profile for simple interactive tasks."""
    task_name = task_data["name"]
    webgen_meta = task_data.get("webgen_metadata", {})
    eval_tasks = webgen_meta.get("evaluation_tasks", [])

    steps = []

    # Take first 2 evaluation tasks as interaction steps
    for i, eval_task in enumerate(eval_tasks[:2]):
        steps.append(
            InteractionStep(
                step_name=f"interaction_step_{i+1}",
                action="verify_element",
                selector="button, .button, .btn, input, select, textarea",  # Generic interactive element
                expected=eval_task["expected"][:50],
                description=eval_task["task"],
            )
        )

    return InteractionProfile(
        task_name=task_name,
        interaction_type="simple_interaction",
        steps=steps,
        success_criteria=["elements_responsive", "interactions_work"],
    )
