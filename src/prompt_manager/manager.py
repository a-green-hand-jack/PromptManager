"""Core PromptManager class integrating all components."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from .cache import CacheKeyBuilder, MultiLevelCache
from .config import ConfigLoader, PromptConfig
from .template import VersionedTemplateRenderer
from .exceptions import (
    ParameterValidationError,
    TemplateNotFoundError,
    VersionNotFoundError,
)


class PromptManager:
    """Main interface for the prompt management system.

    This class integrates configuration loading, template rendering, caching,
    and version management into a single, easy-to-use API.

    Example:
        >>> manager = PromptManager("prompts")
        >>> messages = manager.render_messages(
        ...     prompt_name="trading_agent",
        ...     version="v2",
        ...     symbol="BTC-USD",
        ...     price=45000.0
        ... )
    """

    def __init__(
        self,
        prompts_dir: Union[str, Path],
        config_subdir: str = "configs",
        template_subdir: str = "templates",
        enable_cache: bool = True,
        template_cache_size: int = 50,
        render_cache_size: int = 200,
        dev_mode: bool = False,
    ):
        """Initialize the PromptManager.

        Args:
            prompts_dir: Root directory containing prompts
            config_subdir: Subdirectory for config files (default: "configs")
            template_subdir: Subdirectory for template files (default: "templates")
            enable_cache: Whether to enable caching
            template_cache_size: Max size for template cache
            render_cache_size: Max size for render result cache
            dev_mode: Enable development mode (disables cache, enables hot-reload)
        """
        self.prompts_dir = Path(prompts_dir)
        self.config_dir = self.prompts_dir / config_subdir
        self.template_dir = self.prompts_dir / template_subdir
        self.dev_mode = dev_mode

        # Disable cache in dev mode
        if dev_mode:
            enable_cache = False

        # Initialize components
        self.config_loader = ConfigLoader(self.config_dir)
        self.template_renderer = VersionedTemplateRenderer(self.template_dir)
        self.cache = MultiLevelCache(
            template_cache_size=template_cache_size,
            render_cache_size=render_cache_size,
            enabled=enable_cache,
        )

        # Loaded configs cache (separate from render cache)
        self._configs: Dict[str, PromptConfig] = {}

    def load_config(self, prompt_name: str, reload: bool = False) -> PromptConfig:
        """Load a prompt configuration.

        Args:
            prompt_name: Name of the prompt
            reload: Force reload even if cached

        Returns:
            PromptConfig object
        """
        if reload or prompt_name not in self._configs or self.dev_mode:
            config = self.config_loader.load(prompt_name)
            self._configs[prompt_name] = config
        return self._configs[prompt_name]

    def render(
        self,
        prompt_name: str,
        template_type: str,
        version: Optional[str] = None,
        validate_params: bool = True,
        **parameters: Any,
    ) -> str:
        """Render a single prompt template.

        Args:
            prompt_name: Name of the prompt configuration
            template_type: Type of template to render (e.g., "system", "user")
            version: Template version (uses config default if not specified)
            validate_params: Whether to validate parameters against config
            **parameters: Template variables

        Returns:
            Rendered prompt string
        """
        # Load config
        config = self.load_config(prompt_name)

        # Use config's default version if not specified
        if version is None:
            version = config.metadata.current_version

        # Validate and convert parameters
        if validate_params:
            try:
                parameters = config.validate_parameters(parameters)
            except ValueError as e:
                raise ParameterValidationError(f"Parameter validation failed: {e}")

        # Check cache
        cache_key = CacheKeyBuilder.build(
            f"{prompt_name}:{template_type}",
            version=version,
            **parameters
        )

        cached_result = self.cache.get_render(cache_key)
        if cached_result is not None:
            return cached_result

        # Render template
        try:
            result = self.template_renderer.render_versioned(
                template_type=template_type,
                version=version,
                **parameters
            )
        except TemplateNotFoundError as e:
            available_versions = self.template_renderer.list_versions(template_type)
            raise VersionNotFoundError(
                f"{e}. Available versions: {available_versions}"
            )

        # Cache result
        self.cache.put_render(cache_key, result)

        return result

    def render_messages(
        self,
        prompt_name: str,
        version: Optional[str] = None,
        system_params: Optional[Dict[str, Any]] = None,
        user_params: Optional[Dict[str, Any]] = None,
        validate_params: bool = True,
        **shared_params: Any,
    ) -> List[Dict[str, str]]:
        """Render both system and user prompts as message list.

        This is a convenience method for creating OpenAI-style message lists.

        Args:
            prompt_name: Name of the prompt configuration
            version: Template version (uses config default if not specified)
            system_params: Parameters specific to system prompt
            user_params: Parameters specific to user prompt
            validate_params: Whether to validate parameters
            **shared_params: Parameters shared between system and user prompts

        Returns:
            List of message dicts with 'role' and 'content' keys
        """
        system_params = system_params or {}
        user_params = user_params or {}

        # Merge shared params
        system_params = {**shared_params, **system_params}
        user_params = {**shared_params, **user_params}

        # Add current_date if not present
        if 'current_date' not in system_params and 'current_date' not in user_params:
            current_date = datetime.now().strftime("%Y-%m-%d")
            system_params['current_date'] = current_date
            user_params['current_date'] = current_date

        messages = []

        # Render system prompt if it exists
        try:
            system_content = self.render(
                prompt_name=prompt_name,
                template_type="system",
                version=version,
                validate_params=validate_params,
                **system_params
            )
            messages.append({"role": "system", "content": system_content})
        except (TemplateNotFoundError, VersionNotFoundError):
            # System prompt is optional
            pass

        # Render user prompt
        user_content = self.render(
            prompt_name=prompt_name,
            template_type="user",
            version=version,
            validate_params=validate_params,
            **user_params
        )
        messages.append({"role": "user", "content": user_content})

        return messages

    def get_llm_config(self, prompt_name: str) -> Optional[Dict[str, Any]]:
        """Get LLM configuration from prompt config.

        Args:
            prompt_name: Name of the prompt

        Returns:
            LLM config dict or None
        """
        config = self.load_config(prompt_name)
        return config.llm_config

    def list_prompts(self) -> List[str]:
        """List all available prompt configurations.

        Returns:
            List of prompt names
        """
        return self.config_loader.list_configs()

    def list_versions(self, template_type: str) -> List[str]:
        """List available versions for a template type.

        Args:
            template_type: Type of template (e.g., "system", "user")

        Returns:
            List of version identifiers
        """
        return self.template_renderer.list_versions(template_type)

    def clear_cache(self) -> None:
        """Clear all caches."""
        self.cache.clear()
        self._configs.clear()

    def reload(self, prompt_name: str) -> None:
        """Reload a specific prompt configuration.

        Useful in development for picking up config changes.

        Args:
            prompt_name: Name of the prompt to reload
        """
        self.load_config(prompt_name, reload=True)
        # Also clear related cache entries
        # (Since we don't track which cache keys belong to which prompt,
        # we clear the entire cache)
        self.cache.clear()

    def cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        return self.cache.stats()

    def info(self, prompt_name: str) -> Dict[str, Any]:
        """Get information about a prompt.

        Args:
            prompt_name: Name of the prompt

        Returns:
            Dictionary with prompt information
        """
        config = self.load_config(prompt_name)

        return {
            "name": config.metadata.name,
            "description": config.metadata.description,
            "current_version": config.metadata.current_version,
            "author": config.metadata.author,
            "created_at": config.metadata.created_at,
            "updated_at": config.metadata.updated_at,
            "tags": config.metadata.tags,
            "parameters": {
                name: {
                    "type": spec.type,
                    "required": spec.required,
                    "default": spec.default,
                    "description": spec.description,
                }
                for name, spec in config.parameters.items()
            },
            "llm_config": config.llm_config,
            "extends": config.extends,
            "includes": config.includes,
        }


# Singleton instance for convenience
_default_manager: Optional[PromptManager] = None


def get_manager(prompts_dir: Optional[Union[str, Path]] = None, **kwargs: Any) -> PromptManager:
    """Get or create the default PromptManager instance.

    Args:
        prompts_dir: Root directory containing prompts (required on first call)
        **kwargs: Additional arguments for PromptManager

    Returns:
        PromptManager instance
    """
    global _default_manager

    if _default_manager is None:
        if prompts_dir is None:
            raise ValueError(
                "prompts_dir must be provided when creating the default manager"
            )
        _default_manager = PromptManager(prompts_dir, **kwargs)

    return _default_manager


def reset_manager() -> None:
    """Reset the default manager instance."""
    global _default_manager
    _default_manager = None
