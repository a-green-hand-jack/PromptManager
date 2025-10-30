"""Basic tests for PromptManager."""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from prompt_manager import (
    PromptManager,
    ConfigNotFoundError,
    TemplateNotFoundError,
    VersionNotFoundError,
)


@pytest.fixture
def prompts_dir():
    """Return path to example prompts directory."""
    return Path(__file__).parent.parent / "examples" / "prompts"


@pytest.fixture
def manager(prompts_dir):
    """Create a PromptManager instance."""
    return PromptManager(prompts_dir, enable_cache=False)


@pytest.fixture
def cached_manager(prompts_dir):
    """Create a PromptManager instance with caching enabled."""
    return PromptManager(prompts_dir, enable_cache=True)


class TestBasicFunctionality:
    """Test basic PromptManager functionality."""

    def test_initialization(self, prompts_dir):
        """Test manager initialization."""
        manager = PromptManager(prompts_dir)
        assert manager is not None
        assert manager.prompts_dir == Path(prompts_dir)

    def test_load_config(self, manager):
        """Test loading a configuration."""
        config = manager.load_config("trading_agent")
        assert config is not None
        assert config.metadata.name == "trading_agent"

    def test_config_not_found(self, manager):
        """Test error when config doesn't exist."""
        with pytest.raises(ConfigNotFoundError):
            manager.load_config("non_existent_config")

    def test_list_prompts(self, manager):
        """Test listing available prompts."""
        prompts = manager.list_prompts()
        assert isinstance(prompts, list)
        assert "trading_agent" in prompts

    def test_list_versions(self, manager):
        """Test listing available template versions."""
        versions = manager.list_versions("system")
        assert isinstance(versions, list)
        assert "v1" in versions
        assert "v2" in versions


class TestRendering:
    """Test template rendering functionality."""

    def test_render_system_prompt(self, manager):
        """Test rendering a system prompt."""
        result = manager.render(
            prompt_name="trading_agent",
            template_type="system",
            version="v1",
            symbol="BTC-USD",
            current_price=45000.0,
        )
        assert isinstance(result, str)
        assert len(result) > 0
        assert "BTC-USD" in result or "trading" in result.lower()

    def test_render_user_prompt(self, manager):
        """Test rendering a user prompt."""
        result = manager.render(
            prompt_name="trading_agent",
            template_type="user",
            version="observation",
            symbol="BTC-USD",
            current_price=45000.0,
            rsi=32.5,
        )
        assert isinstance(result, str)
        assert "BTC-USD" in result
        assert "45000" in result

    def test_render_messages(self, manager):
        """Test rendering complete message list."""
        messages = manager.render_messages(
            prompt_name="trading_agent",
            version="v1",
            symbol="BTC-USD",
            current_price=45000.0,
            rsi=32.5,
        )
        assert isinstance(messages, list)
        assert len(messages) >= 1  # At least user message
        assert all(isinstance(msg, dict) for msg in messages)
        assert all("role" in msg and "content" in msg for msg in messages)

    def test_version_not_found(self, manager):
        """Test error when version doesn't exist."""
        with pytest.raises(VersionNotFoundError):
            manager.render(
                prompt_name="trading_agent",
                template_type="system",
                version="v999",
                symbol="BTC-USD",
                current_price=45000.0,
            )


class TestParameters:
    """Test parameter handling."""

    def test_parameter_defaults(self, manager):
        """Test that default parameters are used."""
        # Should work with only required params
        messages = manager.render_messages(
            prompt_name="trading_agent",
            version="v1",
            symbol="BTC-USD",
            current_price=45000.0,
            # Other params should use defaults from config
        )
        assert len(messages) >= 1

    def test_parameter_override(self, manager):
        """Test overriding default parameters."""
        result = manager.render(
            prompt_name="trading_agent",
            template_type="system",
            version="v1",
            symbol="BTC-USD",
            current_price=45000.0,
            risk_cap_pct=0.05,  # Override default
            min_confidence=0.80,  # Override default
        )
        assert "0.05" in result or "5" in result  # Check override is used


class TestCaching:
    """Test caching functionality."""

    def test_cache_enabled(self, cached_manager):
        """Test that caching works."""
        params = {
            "symbol": "BTC-USD",
            "current_price": 45000.0,
            "rsi": 32.5,
        }

        # First render (cold)
        messages1 = cached_manager.render_messages(
            "trading_agent", version="v1", **params
        )

        # Check cache stats
        stats = cached_manager.cache_stats()
        assert stats["enabled"] is True

        # Second render (should be cached)
        messages2 = cached_manager.render_messages(
            "trading_agent", version="v1", **params
        )

        # Results should be identical
        assert messages1 == messages2

        # Cache should have hits
        stats = cached_manager.cache_stats()
        assert stats["render_cache"]["hits"] > 0

    def test_clear_cache(self, cached_manager):
        """Test clearing the cache."""
        params = {"symbol": "BTC", "current_price": 45000.0}

        # Render once
        cached_manager.render_messages("trading_agent", version="v1", **params)

        # Clear cache
        cached_manager.clear_cache()

        # Check cache is empty
        stats = cached_manager.cache_stats()
        assert stats["render_cache"]["size"] == 0
        assert stats["template_cache"]["size"] == 0


class TestConfiguration:
    """Test configuration management."""

    def test_get_llm_config(self, manager):
        """Test getting LLM configuration."""
        llm_config = manager.get_llm_config("trading_agent")
        assert llm_config is not None
        assert "model" in llm_config
        assert "temperature" in llm_config

    def test_get_info(self, manager):
        """Test getting prompt information."""
        info = manager.info("trading_agent")
        assert info is not None
        assert info["name"] == "trading_agent"
        assert "description" in info
        assert "parameters" in info
        assert "llm_config" in info

    def test_reload_config(self, manager):
        """Test reloading a configuration."""
        # Load once
        config1 = manager.load_config("trading_agent")

        # Reload
        manager.reload("trading_agent")

        # Load again
        config2 = manager.load_config("trading_agent")

        # Should have same content
        assert config1.metadata.name == config2.metadata.name


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
