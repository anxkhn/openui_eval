"""Web renderer for capturing screenshots of HTML content using Selenium."""

import os
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import chromedriver_autoinstaller
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ..core.config import RenderingConfig
from ..core.exceptions import RenderingError
from ..core.logger import get_logger


class WebRenderer:
    """Web renderer for capturing screenshots of HTML content."""

    def __init__(self, config: RenderingConfig):
        self.config = config
        self.logger = get_logger()
        self.driver = None
        # Install chromedriver if needed
        try:
            chromedriver_autoinstaller.install()
        except Exception as e:
            self.logger.warning(f"Failed to auto-install chromedriver: {e}")

    def _setup_driver(self):
        """Setup Chrome WebDriver with appropriate options."""
        try:
            chrome_options = Options()
            if self.config.headless:
                chrome_options.add_argument("--headless")
            # Add common options for better rendering
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")  # Faster loading
            chrome_options.add_argument("--disable-javascript")  # For static rendering
            chrome_options.add_argument(
                f"--window-size={self.config.viewport_width},{self.config.viewport_height}"
            )
            # Set user agent
            chrome_options.add_argument(
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            # Create driver
            self.driver = webdriver.Chrome(options=chrome_options)
            # Set window size
            self.driver.set_window_size(
                self.config.viewport_width, self.config.viewport_height
            )
            # Set timeouts
            self.driver.implicitly_wait(self.config.timeout)
            self.driver.set_page_load_timeout(self.config.timeout)
            self.logger.debug("WebDriver setup complete")
        except Exception as e:
            error_msg = f"Failed to setup WebDriver: {e}"
            self.logger.error(error_msg)
            raise RenderingError(error_msg)

    def _cleanup_driver(self):
        """Clean up WebDriver resources."""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                self.logger.debug("WebDriver cleanup complete")
            except Exception as e:
                self.logger.warning(f"Error during WebDriver cleanup: {e}")

    def render_html_file(
        self, html_path: str, screenshot_path: str, create_llm_version: bool = True
    ) -> Dict[str, Any]:
        """
        Render HTML file and capture screenshot.
        Args:
            html_path: Path to HTML file
            screenshot_path: Path to save screenshot (full resolution)
            create_llm_version: Whether to create an LLM-optimized version
        Returns:
            Dictionary with paths and success status
        """
        start_time = time.time()
        try:
            # Ensure HTML file exists
            if not Path(html_path).exists():
                raise RenderingError(f"HTML file not found: {html_path}")
            # Setup driver if not already done
            if not self.driver:
                self._setup_driver()
            # Convert to file URL
            file_url = f"file://{os.path.abspath(html_path)}"
            self.logger.debug(f"Loading HTML file: {file_url}")
            # Load the HTML file
            self.driver.get(file_url)
            # Wait for page to load
            time.sleep(self.config.wait_time)
            # Wait for body element to be present
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except Exception:
                self.logger.warning(
                    "Body element not found, proceeding with screenshot"
                )
            # Ensure screenshot directory exists
            Path(screenshot_path).parent.mkdir(parents=True, exist_ok=True)
            # Capture full-resolution screenshot
            success = self.driver.save_screenshot(screenshot_path)
            duration = time.time() - start_time
            result = {
                "success": success,
                "full_screenshot_path": screenshot_path if success else None,
                "llm_screenshot_path": None,
                "duration": duration,
            }
            if success:
                # Create LLM-optimized version if requested
                if create_llm_version:
                    # Generate LLM screenshot path
                    screenshot_path_obj = Path(screenshot_path)
                    llm_screenshot_path = (
                        screenshot_path_obj.parent
                        / f"{screenshot_path_obj.stem}_llm{screenshot_path_obj.suffix}"
                    )
                    if self._create_llm_optimized_image(
                        screenshot_path, str(llm_screenshot_path)
                    ):
                        result["llm_screenshot_path"] = str(llm_screenshot_path)
                self.logger.log_rendering_operation(
                    url=file_url,
                    screenshot_path=screenshot_path,
                    duration=duration,
                    success=True,
                )
            else:
                self.logger.log_rendering_operation(
                    url=file_url,
                    screenshot_path=screenshot_path,
                    duration=duration,
                    success=False,
                )
            return result
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Failed to render HTML file {html_path}: {e}"
            self.logger.error(error_msg)
            self.logger.log_rendering_operation(
                url=html_path,
                screenshot_path=screenshot_path,
                duration=duration,
                success=False,
                error=str(e),
            )
            return {
                "success": False,
                "full_screenshot_path": None,
                "llm_screenshot_path": None,
                "duration": duration,
                "error": str(e),
            }

    def render_html_content(
        self,
        html_content: str,
        screenshot_path: str,
        temp_dir: str = "temp",
        create_llm_version: bool = True,
    ) -> Dict[str, Any]:
        """
        Render HTML content and capture screenshot.
        Args:
            html_content: HTML content as string
            screenshot_path: Path to save screenshot (full resolution)
            temp_dir: Directory for temporary files
            create_llm_version: Whether to create an LLM-optimized version
        Returns:
            Dictionary with paths and success status
        """
        try:
            # Create temporary HTML file
            temp_path = Path(temp_dir)
            temp_path.mkdir(parents=True, exist_ok=True)
            temp_html_path = temp_path / f"temp_{int(time.time())}.html"
            with open(temp_html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            # Render the temporary file
            result = self.render_html_file(
                str(temp_html_path), screenshot_path, create_llm_version
            )
            # Clean up temporary file
            try:
                temp_html_path.unlink()
            except Exception as e:
                self.logger.warning(f"Failed to cleanup temporary file: {e}")
            return result
        except Exception as e:
            error_msg = f"Failed to render HTML content: {e}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "full_screenshot_path": None,
                "llm_screenshot_path": None,
                "duration": 0,
                "error": str(e),
            }

    def capture_full_page_screenshot(
        self, html_path: str, screenshot_path: str
    ) -> bool:
        """
        Capture full page screenshot (entire page height).
        Args:
            html_path: Path to HTML file
            screenshot_path: Path to save screenshot
        Returns:
            True if successful, False otherwise
        """
        start_time = time.time()
        try:
            # Setup driver if not already done
            if not self.driver:
                self._setup_driver()
            # Convert to file URL
            file_url = f"file://{os.path.abspath(html_path)}"
            # Load the HTML file
            self.driver.get(file_url)
            # Wait for page to load
            time.sleep(self.config.wait_time)
            # Get page dimensions
            total_width = self.driver.execute_script("return document.body.offsetWidth")
            total_height = self.driver.execute_script(
                "return document.body.parentNode.scrollHeight"
            )
            # Set window size to capture full page
            self.driver.set_window_size(total_width, total_height)
            # Wait a bit more for layout to adjust
            time.sleep(1)
            # Ensure screenshot directory exists
            Path(screenshot_path).parent.mkdir(parents=True, exist_ok=True)
            # Capture screenshot
            success = self.driver.save_screenshot(screenshot_path)
            # Reset window size
            self.driver.set_window_size(
                self.config.viewport_width, self.config.viewport_height
            )
            duration = time.time() - start_time
            if success:
                self.logger.log_rendering_operation(
                    url=file_url,
                    screenshot_path=screenshot_path,
                    duration=duration,
                    success=True,
                    full_page=True,
                )
                return True
            else:
                return False
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Failed to capture full page screenshot: {e}"
            self.logger.error(error_msg)
            self.logger.log_rendering_operation(
                url=html_path,
                screenshot_path=screenshot_path,
                duration=duration,
                success=False,
                error=str(e),
            )
            return False

    def get_page_info(self, html_path: str) -> Dict[str, Any]:
        """
        Get information about the rendered page.
        Args:
            html_path: Path to HTML file
        Returns:
            Dictionary with page information
        """
        try:
            # Setup driver if not already done
            if not self.driver:
                self._setup_driver()
            # Convert to file URL
            file_url = f"file://{os.path.abspath(html_path)}"
            # Load the HTML file
            self.driver.get(file_url)
            # Wait for page to load
            time.sleep(self.config.wait_time)
            # Get page information
            info = {
                "title": self.driver.title,
                "url": self.driver.current_url,
                "page_width": self.driver.execute_script(
                    "return document.body.offsetWidth"
                ),
                "page_height": self.driver.execute_script(
                    "return document.body.parentNode.scrollHeight"
                ),
                "viewport_width": self.driver.execute_script(
                    "return window.innerWidth"
                ),
                "viewport_height": self.driver.execute_script(
                    "return window.innerHeight"
                ),
                "has_javascript_errors": False,  # Could be enhanced to check console logs
                "load_time": self.config.wait_time,  # Approximate
            }
            # Try to get more detailed information
            try:
                info["element_count"] = len(self.driver.find_elements(By.XPATH, "//*"))
                info["image_count"] = len(self.driver.find_elements(By.TAG_NAME, "img"))
                info["link_count"] = len(self.driver.find_elements(By.TAG_NAME, "a"))
                info["form_count"] = len(self.driver.find_elements(By.TAG_NAME, "form"))
            except Exception as e:
                self.logger.warning(f"Failed to get detailed page info: {e}")
            return info
        except Exception as e:
            self.logger.error(f"Failed to get page info for {html_path}: {e}")
            return {}

    def test_responsiveness(
        self, html_path: str, screenshot_dir: str
    ) -> Dict[str, bool]:
        """
        Test responsiveness by capturing screenshots at different viewport sizes.
        Args:
            html_path: Path to HTML file
            screenshot_dir: Directory to save screenshots
        Returns:
            Dictionary with success status for each viewport
        """
        viewports = {
            "mobile": (375, 667),
            "tablet": (768, 1024),
            "desktop": (1920, 1080),
        }
        results = {}
        original_size = (self.config.viewport_width, self.config.viewport_height)
        try:
            for viewport_name, (width, height) in viewports.items():
                try:
                    # Set viewport size
                    if self.driver:
                        self.driver.set_window_size(width, height)
                    else:
                        # Temporarily update config
                        self.config.viewport_width = width
                        self.config.viewport_height = height
                        self._setup_driver()
                    # Capture screenshot
                    screenshot_path = Path(screenshot_dir) / f"{viewport_name}_view.png"
                    success = self.render_html_file(html_path, str(screenshot_path))
                    results[viewport_name] = success
                    if success:
                        self.logger.info(
                            f"Captured {viewport_name} screenshot: {screenshot_path}"
                        )
                except Exception as e:
                    self.logger.error(
                        f"Failed to test {viewport_name} responsiveness: {e}"
                    )
                    results[viewport_name] = False
            # Restore original viewport size
            if self.driver:
                self.driver.set_window_size(*original_size)
            self.config.viewport_width = original_size[0]
            self.config.viewport_height = original_size[1]
            return results
        except Exception as e:
            self.logger.error(f"Failed to test responsiveness: {e}")
            return {name: False for name in viewports.keys()}

    def cleanup(self):
        """Clean up renderer resources."""
        self._cleanup_driver()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()

    def _create_llm_optimized_image(
        self,
        original_path: str,
        llm_path: str,
        target_size: Tuple[int, int] = (1280, 720),
    ) -> bool:
        """
        Create a resized version of the screenshot for LLM consumption.
        Args:
            original_path: Path to the original full-resolution screenshot
            llm_path: Path to save the LLM-optimized image
            target_size: Target size for the LLM image (width, height)
        Returns:
            True if successful, False otherwise
        """
        try:
            # Open the original image
            with Image.open(original_path) as img:
                # Convert to RGB if needed (in case of RGBA)
                if img.mode != "RGB":
                    img = img.convert("RGB")
                # Resize with high-quality resampling
                resized_img = img.resize(target_size, Image.Resampling.LANCZOS)
                # Ensure directory exists
                Path(llm_path).parent.mkdir(parents=True, exist_ok=True)
                # Save the resized image with optimization
                resized_img.save(llm_path, "PNG", optimize=True, quality=85)
                self.logger.debug(
                    f"Created LLM-optimized image: {llm_path} ({target_size[0]}x{target_size[1]})"
                )
                return True
        except Exception as e:
            self.logger.error(f"Failed to create LLM-optimized image: {e}")
            return False
