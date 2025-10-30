"""Basic usage examples for the PromptManager."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from prompt_manager import PromptManager


def example_1_basic_rendering():
    """Example 1: Basic prompt rendering."""
    print("=" * 80)
    print("Example 1: Basic Prompt Rendering")
    print("=" * 80)

    # Initialize the manager
    manager = PromptManager("examples/prompts")

    # Render a simple user prompt
    user_prompt = manager.render(
        prompt_name="trading_agent",
        template_type="user",
        version="observation",  # User template filename (without .jinja2)
        symbol="BTC-USD",
        current_price=45000.0,
        rsi=32.5,
        macd=150.0,
        volume_24h=2_500_000_000,
    )

    print("\n--- Rendered User Prompt ---")
    print(user_prompt)


def example_2_message_rendering():
    """Example 2: Render complete message list (system + user)."""
    print("\n" + "=" * 80)
    print("Example 2: Complete Message List Rendering")
    print("=" * 80)

    manager = PromptManager("examples/prompts")

    # Render both system and user prompts as message list
    messages = manager.render_messages(
        prompt_name="trading_agent",
        version="v2",  # Use version 2 of system prompt
        # Shared parameters (used by both system and user)
        symbol="BTC-USD",
        current_price=45000.0,
        risk_cap_pct=0.02,
        min_confidence=0.70,
        # User-specific parameters
        user_params={
            "rsi": 32.5,
            "macd": 150.0,
            "volume_24h": 2_500_000_000,
        }
    )

    print(f"\n--- Generated {len(messages)} messages ---")
    for i, msg in enumerate(messages):
        print(f"\nMessage {i+1} (role: {msg['role']}):")
        print("-" * 40)
        # Truncate for display
        content = msg['content']
        if len(content) > 500:
            print(content[:500] + "\n... (truncated)")
        else:
            print(content)


def example_3_parameter_validation():
    """Example 3: Parameter validation."""
    print("\n" + "=" * 80)
    print("Example 3: Parameter Validation")
    print("=" * 80)

    manager = PromptManager("examples/prompts")

    # This will use default values from config for missing parameters
    try:
        messages = manager.render_messages(
            prompt_name="trading_agent",
            version="v1",
            symbol="ETH-USD",
            current_price=3000.0,
            # Note: risk_cap_pct, min_confidence etc. will use defaults
        )
        print("\n✅ Successfully rendered with default parameters")
        print(f"Generated {len(messages)} messages")
    except Exception as e:
        print(f"\n❌ Error: {e}")


def example_4_cache_performance():
    """Example 4: Demonstrate caching performance."""
    print("\n" + "=" * 80)
    print("Example 4: Cache Performance")
    print("=" * 80)

    import time

    manager = PromptManager("examples/prompts", enable_cache=True)

    params = {
        "symbol": "BTC-USD",
        "current_price": 45000.0,
        "rsi": 35.0,
        "macd": 100.0,
    }

    # First render (cold)
    start = time.time()
    messages1 = manager.render_messages("trading_agent", version="v2", **params)
    cold_time = (time.time() - start) * 1000

    # Second render (cached)
    start = time.time()
    messages2 = manager.render_messages("trading_agent", version="v2", **params)
    cached_time = (time.time() - start) * 1000

    print(f"\n⏱️  Cold render time: {cold_time:.2f}ms")
    print(f"⏱️  Cached render time: {cached_time:.2f}ms")
    print(f"🚀 Speedup: {cold_time/cached_time:.1f}x faster")

    # Print cache stats
    stats = manager.cache_stats()
    print(f"\n📊 Cache Statistics:")
    print(f"   Template cache: {stats['template_cache']['size']}/{stats['template_cache']['max_size']} items")
    print(f"   Render cache: {stats['render_cache']['size']}/{stats['render_cache']['max_size']} items")
    print(f"   Hit rate: {stats['render_cache']['hit_rate']}")


def example_5_llm_config():
    """Example 5: Get LLM configuration from prompt."""
    print("\n" + "=" * 80)
    print("Example 5: LLM Configuration")
    print("=" * 80)

    manager = PromptManager("examples/prompts")

    # Get LLM config for a prompt
    llm_config = manager.get_llm_config("trading_agent")

    print("\n⚙️  LLM Configuration:")
    for key, value in llm_config.items():
        print(f"   {key}: {value}")


def example_6_prompt_info():
    """Example 6: Get detailed prompt information."""
    print("\n" + "=" * 80)
    print("Example 6: Prompt Information")
    print("=" * 80)

    manager = PromptManager("examples/prompts")

    # Get detailed info about a prompt
    info = manager.info("trading_agent")

    print("\n📋 Prompt Information:")
    print(f"   Name: {info['name']}")
    print(f"   Description: {info['description']}")
    print(f"   Current Version: {info['current_version']}")
    print(f"   Author: {info['author']}")
    print(f"   Tags: {', '.join(info['tags'])}")

    print(f"\n📝 Parameters ({len(info['parameters'])}):")
    for name, spec in list(info['parameters'].items())[:5]:  # Show first 5
        required = "required" if spec['required'] else "optional"
        default = f" (default: {spec['default']})" if spec['default'] is not None else ""
        print(f"   - {name} ({spec['type']}, {required}){default}")
    if len(info['parameters']) > 5:
        print(f"   ... and {len(info['parameters']) - 5} more")


def example_7_dev_mode():
    """Example 7: Development mode with hot-reload."""
    print("\n" + "=" * 80)
    print("Example 7: Development Mode")
    print("=" * 80)

    # Initialize with dev mode enabled
    manager = PromptManager("examples/prompts", dev_mode=True)

    print("\n🔧 Development mode enabled:")
    print("   - Caching is disabled")
    print("   - Templates are reloaded on every render")
    print("   - Config changes are picked up immediately")

    # Render once
    messages = manager.render_messages(
        prompt_name="trading_agent",
        version="v1",
        symbol="BTC-USD",
        current_price=45000.0,
    )

    print(f"\n✅ Rendered {len(messages)} messages in dev mode")
    print("   (You can now edit templates/configs and see changes immediately)")


def main():
    """Run all examples."""
    examples = [
        example_1_basic_rendering,
        example_2_message_rendering,
        example_3_parameter_validation,
        example_4_cache_performance,
        example_5_llm_config,
        example_6_prompt_info,
        example_7_dev_mode,
    ]

    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\n❌ Error in {example.__name__}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 80)
    print("All examples completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
