"""Prompt Manager - A production-grade prompt management system for LLM applications.

This package provides a comprehensive solution for managing, versioning, and rendering
prompts for Large Language Model applications.

Main Components:
    - PromptManager: Main interface for prompt management
    - ConfigLoader: Load and validate prompt configurations
    - TemplateRenderer: Render Jinja2 templates with caching
    - MultiLevelCache: High-performance caching system

Example:
    >>> from prompt_manager import PromptManager
    >>>
    >>> manager = PromptManager("prompts")
    >>> messages = manager.render_messages(
    ...     prompt_name="trading_agent",
    ...     version="v2",
    ...     symbol="BTC-USD",
    ...     price=45000.0
    ... )
"""

__version__ = "1.0.0"

from .manager import PromptManager, get_manager, reset_manager
from .config import (
    ConfigLoader,
    PromptConfig,
    PromptMetadata,
    ParameterSpec,
)
from .template import (
    TemplateRenderer,
    VersionedTemplateRenderer,
)
from .cache import (
    LRUCache,
    MultiLevelCache,
    CacheKeyBuilder,
)
from .exceptions import (
    PromptManagerError,
    ConfigNotFoundError,
    ConfigValidationError,
    TemplateNotFoundError,
    TemplateRenderError,
    VersionNotFoundError,
    ParameterValidationError,
    CacheError,
)

__all__ = [
    # Main classes
    "PromptManager",
    "get_manager",
    "reset_manager",

    # Config classes
    "ConfigLoader",
    "PromptConfig",
    "PromptMetadata",
    "ParameterSpec",

    # Template classes
    "TemplateRenderer",
    "VersionedTemplateRenderer",

    # Cache classes
    "LRUCache",
    "MultiLevelCache",
    "CacheKeyBuilder",

    # Exceptions
    "PromptManagerError",
    "ConfigNotFoundError",
    "ConfigValidationError",
    "TemplateNotFoundError",
    "TemplateRenderError",
    "VersionNotFoundError",
    "ParameterValidationError",
    "CacheError",
]
