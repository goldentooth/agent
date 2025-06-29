"""Web-based tools for HTTP requests, web scraping, and API integration."""

from __future__ import annotations

import json
import time
from typing import Any
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
from pydantic import Field, HttpUrl

from ..flow_agent import FlowIOSchema, FlowTool
from .performance import async_cache, get_http_client, performance_monitor


# HTTP Request Tool
class HttpRequestInput(FlowIOSchema):
    """Input schema for HTTP request tool."""

    url: HttpUrl = Field(..., description="URL to request")
    method: str = Field(
        default="GET", description="HTTP method (GET, POST, PUT, DELETE)"
    )
    headers: dict[str, str] | None = Field(default=None, description="HTTP headers")
    params: dict[str, str] | None = Field(default=None, description="Query parameters")
    data: dict[str, Any] | None = Field(default=None, description="Request body data")
    timeout: float = Field(default=30.0, description="Request timeout in seconds")
    follow_redirects: bool = Field(default=True, description="Follow HTTP redirects")


class HttpRequestOutput(FlowIOSchema):
    """Output schema for HTTP request tool."""

    url: str = Field(..., description="Requested URL")
    status_code: int = Field(..., description="HTTP status code")
    headers: dict[str, str] = Field(..., description="Response headers")
    content: str = Field(..., description="Response content")
    content_type: str = Field(..., description="Response content type")
    elapsed_seconds: float = Field(..., description="Request duration in seconds")
    success: bool = Field(..., description="Whether request was successful")
    error: str | None = Field(default=None, description="Error message if failed")


@performance_monitor.timed("http_request")
@async_cache(ttl=300.0)
async def http_request_implementation(
    input_data: HttpRequestInput,
) -> HttpRequestOutput:
    """Execute HTTP request with comprehensive error handling."""
    start_time = time.time()

    try:
        # Use shared HTTP client for connection pooling
        client = await get_http_client()

        # Prepare request parameters
        request_kwargs = {
            "method": input_data.method.upper(),
            "url": str(input_data.url),
            "headers": input_data.headers or {},
            "params": input_data.params or {},
            "timeout": input_data.timeout,
        }

        # Add data for POST/PUT requests
        if input_data.data and input_data.method.upper() in ["POST", "PUT", "PATCH"]:
            if isinstance(input_data.data, dict):
                request_kwargs["json"] = input_data.data
            else:
                request_kwargs["data"] = input_data.data  # type: ignore[unreachable]

        # Execute request
        response = await client.request(**request_kwargs)  # type: ignore[arg-type]
        elapsed = time.time() - start_time

        # Extract response data
        content_type = response.headers.get("content-type", "").split(";")[0]

        return HttpRequestOutput(
            url=str(response.url),
            status_code=response.status_code,
            headers=dict(response.headers),
            content=response.text,
            content_type=content_type,
            elapsed_seconds=elapsed,
            success=200 <= response.status_code < 300,
            error=(
                None
                if 200 <= response.status_code < 300
                else f"HTTP {response.status_code}"
            ),
        )

    except httpx.TimeoutException:
        elapsed = time.time() - start_time
        return HttpRequestOutput(
            url=str(input_data.url),
            status_code=0,
            headers={},
            content="",
            content_type="",
            elapsed_seconds=elapsed,
            success=False,
            error="Request timeout",
        )
    except Exception as e:
        elapsed = time.time() - start_time
        return HttpRequestOutput(
            url=str(input_data.url),
            status_code=0,
            headers={},
            content="",
            content_type="",
            elapsed_seconds=elapsed,
            success=False,
            error=str(e),
        )


# Web Scraping Tool
class WebScrapeInput(FlowIOSchema):
    """Input schema for web scraping tool."""

    url: HttpUrl = Field(..., description="URL to scrape")
    selector: str | None = Field(
        default=None, description="CSS selector for specific elements"
    )
    extract_links: bool = Field(
        default=False, description="Extract all links from page"
    )
    extract_text: bool = Field(default=True, description="Extract text content")
    extract_images: bool = Field(default=False, description="Extract image URLs")
    max_content_length: int = Field(
        default=50000, description="Maximum content length to return"
    )
    headers: dict[str, str] | None = Field(
        default=None, description="Custom HTTP headers"
    )


class WebScrapeOutput(FlowIOSchema):
    """Output schema for web scraping tool."""

    url: str = Field(..., description="Scraped URL")
    title: str | None = Field(default=None, description="Page title")
    text_content: str = Field(..., description="Extracted text content")
    links: list[str] = Field(default_factory=list, description="Extracted links")
    images: list[str] = Field(default_factory=list, description="Extracted image URLs")
    selected_elements: list[str] = Field(
        default_factory=list, description="Content from CSS selector"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional page metadata"
    )
    success: bool = Field(..., description="Whether scraping was successful")
    error: str | None = Field(default=None, description="Error message if failed")


async def web_scrape_implementation(input_data: WebScrapeInput) -> WebScrapeOutput:
    """Scrape web content with BeautifulSoup parsing."""
    try:
        # First get the page content
        http_input = HttpRequestInput(
            url=input_data.url,
            headers=input_data.headers or {"User-Agent": "Goldentooth-Agent/1.0"},
        )

        http_result = await http_request_implementation(http_input)

        if not http_result.success:
            return WebScrapeOutput(
                url=str(input_data.url),
                text_content="",
                success=False,
                error=f"Failed to fetch page: {http_result.error}",
            )

        # Parse with BeautifulSoup
        soup = BeautifulSoup(http_result.content, "html.parser")

        # Extract title
        title = soup.title.string.strip() if soup.title and soup.title.string else None

        # Extract text content
        text_content = ""
        if input_data.extract_text:
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            text_content = soup.get_text(separator=" ", strip=True)

            # Limit content length
            if len(text_content) > input_data.max_content_length:
                text_content = text_content[: input_data.max_content_length] + "..."

        # Extract links
        links = []
        if input_data.extract_links:
            base_url = str(input_data.url)
            for link in soup.find_all("a", href=True):
                href = link["href"]  # type: ignore[index]
                # Convert relative URLs to absolute
                absolute_url = urljoin(base_url, str(href))
                if absolute_url not in links:
                    links.append(absolute_url)

        # Extract images
        images = []
        if input_data.extract_images:
            base_url = str(input_data.url)
            for img in soup.find_all("img", src=True):
                src = img["src"]  # type: ignore[index]
                # Convert relative URLs to absolute
                absolute_url = urljoin(base_url, str(src))
                if absolute_url not in images:
                    images.append(absolute_url)

        # Extract selected elements
        selected_elements = []
        if input_data.selector:
            elements = soup.select(input_data.selector)
            for element in elements:
                selected_elements.append(element.get_text(strip=True))

        # Extract metadata
        metadata = {}

        # Meta tags
        for meta in soup.find_all("meta"):
            name = meta.get("name") or meta.get("property")  # type: ignore[union-attr]
            content = meta.get("content")  # type: ignore[union-attr]
            if name and content:
                metadata[name] = content

        # Additional metadata
        metadata.update(
            {
                "content_type": http_result.content_type,
                "status_code": http_result.status_code,
                "content_length": len(http_result.content),
            }
        )

        return WebScrapeOutput(
            url=str(input_data.url),
            title=title,
            text_content=text_content,
            links=links,
            images=images,
            selected_elements=selected_elements,
            metadata=metadata,  # type: ignore[arg-type]
            success=True,
            error=None,
        )

    except Exception as e:
        return WebScrapeOutput(
            url=str(input_data.url), text_content="", success=False, error=str(e)
        )


# JSON API Tool
class JsonApiInput(FlowIOSchema):
    """Input schema for JSON API tool."""

    url: HttpUrl = Field(..., description="API endpoint URL")
    method: str = Field(default="GET", description="HTTP method")
    headers: dict[str, str] | None = Field(default=None, description="HTTP headers")
    params: dict[str, str] | None = Field(default=None, description="Query parameters")
    json_data: dict[str, Any] | None = Field(
        default=None, description="JSON request body"
    )
    auth_token: str | None = Field(
        default=None, description="Bearer token for authentication"
    )
    timeout: float = Field(default=30.0, description="Request timeout")


class JsonApiOutput(FlowIOSchema):
    """Output schema for JSON API tool."""

    url: str = Field(..., description="API endpoint URL")
    status_code: int = Field(..., description="HTTP status code")
    response_data: dict[str, Any] = Field(..., description="Parsed JSON response")
    headers: dict[str, str] = Field(..., description="Response headers")
    elapsed_seconds: float = Field(..., description="Request duration")
    success: bool = Field(..., description="Whether API call was successful")
    error: str | None = Field(default=None, description="Error message if failed")


async def json_api_implementation(input_data: JsonApiInput) -> JsonApiOutput:
    """Execute JSON API request with automatic parsing."""
    try:
        # Prepare headers
        headers = input_data.headers or {}
        headers["Content-Type"] = "application/json"
        headers["Accept"] = "application/json"

        # Add authentication if provided
        if input_data.auth_token:
            headers["Authorization"] = f"Bearer {input_data.auth_token}"

        # Create HTTP request
        http_input = HttpRequestInput(
            url=input_data.url,
            method=input_data.method,
            headers=headers,
            params=input_data.params,
            data=input_data.json_data,
            timeout=input_data.timeout,
        )

        # Execute request
        http_result = await http_request_implementation(http_input)

        # Parse JSON response
        response_data = {}
        if http_result.content:
            try:
                response_data = json.loads(http_result.content)
            except json.JSONDecodeError:
                response_data = {"raw_content": http_result.content}

        return JsonApiOutput(
            url=http_result.url,
            status_code=http_result.status_code,
            response_data=response_data,
            headers=http_result.headers,
            elapsed_seconds=http_result.elapsed_seconds,
            success=http_result.success,
            error=http_result.error,
        )

    except Exception as e:
        return JsonApiOutput(
            url=str(input_data.url),
            status_code=0,
            response_data={},
            headers={},
            elapsed_seconds=0.0,
            success=False,
            error=str(e),
        )


# Tool instances
HttpRequestTool = FlowTool(
    name="http_request",
    input_schema=HttpRequestInput,
    output_schema=HttpRequestOutput,
    implementation=http_request_implementation,
    description="Execute HTTP requests with comprehensive error handling and response parsing",
)

WebScrapeTool = FlowTool(
    name="web_scrape",
    input_schema=WebScrapeInput,
    output_schema=WebScrapeOutput,
    implementation=web_scrape_implementation,
    description="Scrape web content with link extraction, text parsing, and CSS selectors",
)

JsonApiTool = FlowTool(
    name="json_api",
    input_schema=JsonApiInput,
    output_schema=JsonApiOutput,
    implementation=json_api_implementation,
    description="Execute JSON API requests with automatic parsing and authentication support",
)
