"""HTML processing utilities for extracting and validating HTML from model responses."""

import html
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup, Comment

from ..core.exceptions import HTMLExtractionError
from ..core.logger import get_logger


class HTMLProcessor:
    """Processes and validates HTML content from model responses."""

    def __init__(self):
        self.logger = get_logger()
        # Common HTML patterns for extraction
        self.html_patterns = [
            # Full HTML document
            r"```html\s*(.*?)\s*```",
            r"```\s*(<!DOCTYPE.*?</html>)\s*```",
            # HTML blocks
            r"<html[^>]*>.*?</html>",
            r"<!DOCTYPE[^>]*>.*?</html>",
            # Partial HTML (body content)
            r"<body[^>]*>.*?</body>",
            r"<div[^>]*>.*?</div>",
            # Any content between HTML tags
            r"(<[^>]+>.*?</[^>]+>)",
        ]

    def extract_html(self, text: str) -> Optional[str]:
        """
        Extract HTML content from model response text.
        Args:
            text: Raw text response from model
        Returns:
            Extracted HTML content or None if not found
        """
        try:
            # Clean the text
            text = text.strip()
            # Try each pattern
            for pattern in self.html_patterns:
                matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
                if matches:
                    html_content = matches[0]
                    # If it's a tuple (from groups), take the first element
                    if isinstance(html_content, tuple):
                        html_content = html_content[0]
                    # Clean and validate
                    cleaned_html = self._clean_html(html_content)
                    if self._is_valid_html(cleaned_html):
                        self.logger.debug(
                            f"Extracted HTML using pattern: {pattern[:50]}..."
                        )
                        return cleaned_html
            # If no patterns match, check if the entire text is HTML
            if self._is_valid_html(text):
                self.logger.debug("Using entire response as HTML")
                return self._clean_html(text)
            # Last resort: look for any HTML-like content
            html_like = self._extract_html_like_content(text)
            if html_like:
                return html_like
            self.logger.warning("No HTML content found in response")
            return None
        except Exception as e:
            self.logger.error(f"Failed to extract HTML: {e}")
            raise HTMLExtractionError(f"HTML extraction failed: {e}")

    def _clean_html(self, html_content: str) -> str:
        """Clean and normalize HTML content."""
        try:
            # Unescape HTML entities
            html_content = html.unescape(html_content)
            # Remove markdown code block markers
            html_content = re.sub(r"^```html\s*", "",
                                  html_content, flags=re.IGNORECASE)
            html_content = re.sub(r"^```\s*", "", html_content)
            html_content = re.sub(r"\s*```$", "", html_content)
            # Parse with BeautifulSoup for cleaning
            soup = BeautifulSoup(html_content, "html.parser")
            # Remove comments
            for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                comment.extract()
            # Ensure proper HTML structure
            if not soup.find("html"):
                # Wrap in basic HTML structure
                if soup.find("head") or soup.find("body"):
                    # Has head or body, just wrap in html
                    html_content = f"<html>{soup.prettify()}</html>"
                else:
                    # No structure, create full document
                    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated Content</title>
</head>
<body>
{soup.prettify()}
</body>
</html>"""
            else:
                html_content = soup.prettify()
            return html_content.strip()
        except Exception as e:
            self.logger.warning(
                f"Failed to clean HTML, returning original: {e}")
            return html_content.strip()

    def _is_valid_html(self, content: str) -> bool:
        """Check if content is valid HTML."""
        try:
            if not content.strip():
                return False
            # Check for basic HTML indicators
            html_indicators = [
                "<html",
                "<!DOCTYPE",
                "<head>",
                "<body>",
                "<div",
                "<span",
                "<p>",
                "<h1",
                "<h2",
                "<h3",
                "<h4",
                "<h5",
                "<h6",
                "<script",
                "<style",
                "<link",
                "<meta",
            ]
            content_lower = content.lower()
            has_html_tags = any(
                indicator in content_lower for indicator in html_indicators
            )
            if not has_html_tags:
                return False
            # Try to parse with BeautifulSoup
            soup = BeautifulSoup(content, "html.parser")
            # Check if parsing was successful and found actual tags
            return len(soup.find_all()) > 0
        except Exception:
            return False

    def _extract_html_like_content(self, text: str) -> Optional[str]:
        """Extract any HTML-like content as a last resort."""
        try:
            # Look for any content that starts and ends with HTML tags
            pattern = r"(<[^>]+>.*?</[^>]+>)"
            matches = re.findall(pattern, text, re.DOTALL)
            if matches:
                # Join all matches
                html_content = "\n".join(matches)
                if self._is_valid_html(html_content):
                    return self._clean_html(html_content)
            return None
        except Exception:
            return None

    def validate_html(self, html_content: str) -> Dict[str, Any]:
        """
        Validate HTML content and return validation results.
        Args:
            html_content: HTML content to validate
        Returns:
            Dictionary with validation results
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            validation_results = {
                "is_valid": True,
                "has_doctype": bool(
                    soup.find(string=re.compile(r"<!DOCTYPE", re.IGNORECASE))
                ),
                "has_html_tag": bool(soup.find("html")),
                "has_head": bool(soup.find("head")),
                "has_body": bool(soup.find("body")),
                "has_title": bool(soup.find("title")),
                "has_meta_charset": bool(soup.find("meta", attrs={"charset": True})),
                "has_viewport_meta": bool(
                    soup.find("meta", attrs={"name": "viewport"})
                ),
                "has_css": bool(
                    soup.find("style") or soup.find("link", rel="stylesheet")
                ),
                "has_javascript": bool(soup.find("script")),
                "tag_count": len(soup.find_all()),
                "text_content_length": len(soup.get_text().strip()),
                "warnings": [],
                "errors": [],
            }
            # Check for common issues
            if not validation_results["has_doctype"]:
                validation_results["warnings"].append(
                    "Missing DOCTYPE declaration")
            if not validation_results["has_title"]:
                validation_results["warnings"].append("Missing title tag")
            if not validation_results["has_meta_charset"]:
                validation_results["warnings"].append(
                    "Missing charset meta tag")
            if validation_results["tag_count"] == 0:
                validation_results["errors"].append("No HTML tags found")
                validation_results["is_valid"] = False
            if validation_results["text_content_length"] == 0:
                validation_results["warnings"].append(
                    "No visible text content")
            return validation_results
        except Exception as e:
            return {
                "is_valid": False,
                "errors": [f"Validation failed: {e}"],
                "warnings": [],
                "tag_count": 0,
                "text_content_length": 0,
            }

    def extract_inline_assets(self, html_content: str) -> Dict[str, List[str]]:
        """
        Extract inline CSS and JavaScript from HTML.
        Args:
            html_content: HTML content to analyze
        Returns:
            Dictionary with lists of inline CSS and JS
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            assets = {
                "inline_css": [],
                "inline_js": [],
                "external_css": [],
                "external_js": [],
                "images": [],
            }
            # Extract inline CSS
            for style_tag in soup.find_all("style"):
                if style_tag.string:
                    assets["inline_css"].append(style_tag.string.strip())
            # Extract inline JavaScript
            for script_tag in soup.find_all("script"):
                if script_tag.string:
                    assets["inline_js"].append(script_tag.string.strip())
                elif script_tag.get("src"):
                    assets["external_js"].append(script_tag.get("src"))
            # Extract external CSS
            for link_tag in soup.find_all("link", rel="stylesheet"):
                if link_tag.get("href"):
                    assets["external_css"].append(link_tag.get("href"))
            # Extract images
            for img_tag in soup.find_all("img"):
                if img_tag.get("src"):
                    assets["images"].append(img_tag.get("src"))
            return assets
        except Exception as e:
            self.logger.error(f"Failed to extract assets: {e}")
            return {
                "inline_css": [],
                "inline_js": [],
                "external_css": [],
                "external_js": [],
                "images": [],
            }

    def save_html(self, html_content: str, output_path: str) -> bool:
        """
        Save HTML content to file.
        Args:
            html_content: HTML content to save
            output_path: Path to save the file
        Returns:
            True if successful, False otherwise
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            self.logger.debug(f"Saved HTML to {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save HTML to {output_path}: {e}")
            return False

    def get_html_stats(self, html_content: str) -> Dict[str, Any]:
        """
        Get statistics about HTML content.
        Args:
            html_content: HTML content to analyze
        Returns:
            Dictionary with HTML statistics
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            # Count different types of elements
            element_counts = {}
            for tag in soup.find_all():
                tag_name = tag.name.lower()
                element_counts[tag_name] = element_counts.get(tag_name, 0) + 1
            # Get text content
            text_content = soup.get_text().strip()
            # Count lines of CSS and JS
            assets = self.extract_inline_assets(html_content)
            css_lines = sum(len(css.split("\n"))
                            for css in assets["inline_css"])
            js_lines = sum(len(js.split("\n")) for js in assets["inline_js"])
            return {
                "total_elements": len(soup.find_all()),
                "element_counts": element_counts,
                "text_length": len(text_content),
                "html_size_bytes": len(html_content.encode("utf-8")),
                "css_lines": css_lines,
                "js_lines": js_lines,
                "external_resources": len(assets["external_css"])
                + len(assets["external_js"]),
                "images": len(assets["images"]),
                "has_responsive_meta": bool(
                    soup.find("meta", attrs={"name": "viewport"})
                ),
                "has_semantic_tags": bool(
                    soup.find_all(
                        [
                            "header",
                            "nav",
                            "main",
                            "section",
                            "article",
                            "aside",
                            "footer",
                        ]
                    )
                ),
            }
        except Exception as e:
            self.logger.error(f"Failed to get HTML stats: {e}")
            return {}
