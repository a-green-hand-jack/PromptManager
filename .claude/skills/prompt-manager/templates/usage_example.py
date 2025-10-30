"""Example usage of the prompt manager system."""

import sys
from pathlib import Path

# Add prompt_manager to path if needed
# sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from prompt_manager import PromptManager


def main():
    # Initialize the manager
    manager = PromptManager("prompts")

    # Example parameters
    params = {
        "input_text": "Your input here",
        "threshold": 0.75,
        # Add other parameters as defined in your config
    }

    # Render messages
    messages = manager.render_messages(
        prompt_name="your_agent_name",
        version="v1",
        **params
    )

    # Print the messages
    print("=" * 80)
    print("Generated Messages:")
    print("=" * 80)

    for i, msg in enumerate(messages, 1):
        print(f"\nMessage {i} [{msg['role']}]:")
        print("-" * 40)
        print(msg['content'])

    # Get LLM configuration
    llm_config = manager.get_llm_config("your_agent_name")
    print("\n" + "=" * 80)
    print("LLM Configuration:")
    print("=" * 80)
    print(f"Model: {llm_config['model']}")
    print(f"Temperature: {llm_config['temperature']}")
    print(f"Max Tokens: {llm_config['max_tokens']}")

    # Cache statistics
    stats = manager.cache_stats()
    print("\n" + "=" * 80)
    print("Cache Statistics:")
    print("=" * 80)
    print(f"Enabled: {stats['enabled']}")
    print(f"Template cache: {stats['template_cache']['size']} items")
    print(f"Render cache: {stats['render_cache']['size']} items")


if __name__ == "__main__":
    main()
