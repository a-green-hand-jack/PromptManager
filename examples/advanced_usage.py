"""Advanced usage examples for the PromptManager."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from prompt_manager import PromptManager


def example_1_version_comparison():
    """Example 1: Compare different prompt versions."""
    print("=" * 80)
    print("Example 1: Version Comparison")
    print("=" * 80)

    manager = PromptManager("examples/prompts")

    params = {
        "symbol": "BTC-USD",
        "current_price": 45000.0,
        "risk_cap_pct": 0.02,
        "min_confidence": 0.70,
    }

    # Render v1
    system_v1 = manager.render(
        "trading_agent",
        template_type="system",
        version="v1",
        **params
    )

    # Render v2
    system_v2 = manager.render(
        "trading_agent",
        template_type="system",
        version="v2",
        **params
    )

    print(f"\n📊 Version Comparison:")
    print(f"   v1 length: {len(system_v1)} characters")
    print(f"   v2 length: {len(system_v2)} characters")
    print(f"   v2 is {len(system_v2) - len(system_v1)} characters longer")

    print("\n--- v1 Preview (first 300 chars) ---")
    print(system_v1[:300] + "...")

    print("\n--- v2 Preview (first 300 chars) ---")
    print(system_v2[:300] + "...")


def example_2_batch_rendering():
    """Example 2: Batch render multiple prompts."""
    print("\n" + "=" * 80)
    print("Example 2: Batch Rendering for Backtesting")
    print("=" * 80)

    manager = PromptManager("examples/prompts", enable_cache=True)

    # Simulate backtest with multiple observations
    observations = [
        {"symbol": "BTC-USD", "current_price": 45000, "rsi": 30, "macd": 100},
        {"symbol": "BTC-USD", "current_price": 45500, "rsi": 35, "macd": 120},
        {"symbol": "BTC-USD", "current_price": 46000, "rsi": 42, "macd": 150},
        {"symbol": "ETH-USD", "current_price": 3000, "rsi": 65, "macd": -50},
        {"symbol": "ETH-USD", "current_price": 2950, "rsi": 58, "macd": -80},
    ]

    import time
    start = time.time()

    results = []
    for obs in observations:
        messages = manager.render_messages(
            prompt_name="trading_agent",
            version="v2",
            **obs
        )
        results.append(messages)

    elapsed = (time.time() - start) * 1000

    print(f"\n✅ Rendered {len(results)} prompt sets in {elapsed:.2f}ms")
    print(f"   Average: {elapsed/len(results):.2f}ms per render")

    # Show cache effectiveness
    stats = manager.cache_stats()
    print(f"\n📊 Cache Statistics:")
    print(f"   Template cache hit rate: {stats['template_cache']['hit_rate']}")
    print(f"   Render cache hit rate: {stats['render_cache']['hit_rate']}")


def example_3_custom_parameters():
    """Example 3: Using custom parameters not in config."""
    print("\n" + "=" * 80)
    print("Example 3: Custom Parameters")
    print("=" * 80)

    manager = PromptManager("examples/prompts")

    # You can pass custom parameters even if not defined in config
    # The system is flexible and allows additional context
    messages = manager.render_messages(
        prompt_name="trading_agent",
        version="v2",
        symbol="BTC-USD",
        current_price=45000.0,
        # Standard parameters
        rsi=32.0,
        macd=100.0,
        # Custom parameters (not in config, but template can use them)
        user_params={
            "bollinger_upper": 46500.0,
            "bollinger_lower": 43500.0,
            "account_balance": 10000.0,
            "positions": [
                {
                    "symbol": "ETH-USD",
                    "side": "long",
                    "size_usd": 2000.0,
                    "entry_price": 2950.0,
                    "pnl_pct": 2.5
                }
            ]
        },
        validate_params=False,  # Disable strict validation for custom params
    )

    print("\n✅ Rendered messages with custom parameters")
    print(f"   Total messages: {len(messages)}")
    print("\n--- User Message Preview ---")
    print(messages[-1]['content'][:500] + "...")


def example_4_singleton_pattern():
    """Example 4: Using the singleton pattern for global access."""
    print("\n" + "=" * 80)
    print("Example 4: Singleton Pattern")
    print("=" * 80)

    from prompt_manager import get_manager

    # Initialize the default manager
    manager1 = get_manager("examples/prompts")

    # Get the same instance elsewhere
    manager2 = get_manager()

    print(f"\n✅ Singleton pattern working: {manager1 is manager2}")

    # Use the global manager
    info = manager2.info("trading_agent")
    print(f"   Prompt: {info['name']}")
    print(f"   Version: {info['current_version']}")


def example_5_error_handling():
    """Example 5: Proper error handling."""
    print("\n" + "=" * 80)
    print("Example 5: Error Handling")
    print("=" * 80)

    from prompt_manager import (
        ConfigNotFoundError,
        TemplateNotFoundError,
        VersionNotFoundError,
        ParameterValidationError,
    )

    manager = PromptManager("examples/prompts")

    # Test 1: Config not found
    print("\n🧪 Test 1: Non-existent prompt")
    try:
        manager.render_messages("non_existent_prompt", symbol="BTC")
    except ConfigNotFoundError as e:
        print(f"   ✅ Caught ConfigNotFoundError: {e}")

    # Test 2: Version not found
    print("\n🧪 Test 2: Non-existent version")
    try:
        manager.render(
            "trading_agent",
            template_type="system",
            version="v99",
            symbol="BTC"
        )
    except VersionNotFoundError as e:
        print(f"   ✅ Caught VersionNotFoundError: {e}")

    # Test 3: Missing required parameter
    print("\n🧪 Test 3: Missing required parameter")
    try:
        manager.render_messages(
            "trading_agent",
            version="v1",
            # Missing 'symbol' and 'current_price' which are required
        )
    except (ParameterValidationError, KeyError) as e:
        print(f"   ✅ Caught validation error: {e}")


def example_6_integration_with_llm():
    """Example 6: Integration with LLM API (mock)."""
    print("\n" + "=" * 80)
    print("Example 6: LLM Integration Pattern")
    print("=" * 80)

    manager = PromptManager("examples/prompts")

    # Get messages and LLM config
    messages = manager.render_messages(
        prompt_name="trading_agent",
        version="v2",
        symbol="BTC-USD",
        current_price=45000.0,
        rsi=32.0,
        macd=100.0,
    )

    llm_config = manager.get_llm_config("trading_agent")

    # Simulate OpenAI API call structure
    api_call = {
        "model": llm_config["model"],
        "messages": messages,
        "temperature": llm_config["temperature"],
        "max_tokens": llm_config["max_tokens"],
        "response_format": llm_config.get("response_format"),
    }

    print("\n📤 API Call Structure:")
    print(f"   Model: {api_call['model']}")
    print(f"   Temperature: {api_call['temperature']}")
    print(f"   Max Tokens: {api_call['max_tokens']}")
    print(f"   Messages: {len(api_call['messages'])}")
    print(f"   Response Format: {api_call['response_format']}")

    print("\n💡 Usage with OpenAI:")
    print("   ```python")
    print("   from openai import OpenAI")
    print("   client = OpenAI()")
    print("   response = client.chat.completions.create(**api_call)")
    print("   ```")


def example_7_reload_in_development():
    """Example 7: Reload prompts during development."""
    print("\n" + "=" * 80)
    print("Example 7: Reload During Development")
    print("=" * 80)

    manager = PromptManager("examples/prompts", dev_mode=False)

    # Initial render
    messages1 = manager.render_messages(
        "trading_agent",
        version="v1",
        symbol="BTC",
        current_price=45000.0
    )

    print("\n✅ Initial render completed")
    print(f"   System prompt length: {len(messages1[0]['content'])}")

    # Simulate editing the config/template
    print("\n🔧 Imagine you edited the config or template...")
    print("   (In real use, you'd actually edit the file)")

    # Reload the prompt
    manager.reload("trading_agent")

    # Render again
    messages2 = manager.render_messages(
        "trading_agent",
        version="v1",
        symbol="BTC",
        current_price=45000.0
    )

    print("\n✅ Reloaded and rendered again")
    print(f"   System prompt length: {len(messages2[0]['content'])}")
    print("   (Changes would be reflected here)")


def main():
    """Run all advanced examples."""
    examples = [
        example_1_version_comparison,
        example_2_batch_rendering,
        example_3_custom_parameters,
        example_4_singleton_pattern,
        example_5_error_handling,
        example_6_integration_with_llm,
        example_7_reload_in_development,
    ]

    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\n❌ Error in {example.__name__}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 80)
    print("All advanced examples completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
