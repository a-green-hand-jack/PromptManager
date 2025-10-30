# Prompt Manager

<div align="center">

**A production-grade prompt management system for LLM applications**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Examples](#-examples)

</div>

---

## 🎯 Overview

**Prompt Manager** is a comprehensive solution for managing, versioning, and rendering prompts for Large Language Model (LLM) applications. It combines the best practices from production systems to provide:

- **Separation of Concerns**: YAML configs + Jinja2 templates
- **Version Management**: Multiple versions coexisting with inheritance support
- **High Performance**: Multi-level caching with 50-90% speedup
- **Type Safety**: Parameter validation and type conversion
- **Development Friendly**: Hot-reload and clear error messages
- **Production Ready**: Battle-tested patterns from real-world agent systems

---

## ✨ Features

### Core Features

- 🗂️ **Structured Configuration**: YAML-based prompt configurations with metadata, parameters, and LLM settings
- 📝 **Template System**: Powerful Jinja2 templating with includes and custom filters
- 🔄 **Version Management**:
  - Multiple versions coexist (v1, v2, v3...)
  - Inheritance via `extends` field
  - Easy A/B testing and rollback
- 🚀 **Performance**:
  - Multi-level caching (template + render caches)
  - 50-90% speedup on repeated renders
  - Configurable cache sizes
- ✅ **Type Safety**:
  - Parameter type declarations
  - Automatic validation and conversion
  - Required vs optional parameters with defaults
- 🔧 **Developer Experience**:
  - Dev mode with hot-reload
  - Clear error messages
  - Comprehensive examples
  - Detailed documentation
- 🔌 **Easy Integration**:
  - Simple API
  - OpenAI-compatible message format
  - Singleton pattern support
  - LLM config management

---

## 📦 Installation

### From Source

```bash
git clone https://github.com/yourusername/prompt-manager.git
cd prompt-manager
pip install -e .
```

### For Development

```bash
pip install -e ".[dev]"
```

---

## 🚀 Quick Start

### 1. Setup Project Structure

```
your_project/
└── prompts/
    ├── configs/
    │   └── my_agent.yaml
    └── templates/
        ├── common/
        │   └── instructions.jinja2
        ├── system/
        │   ├── v1.jinja2
        │   └── v2.jinja2
        └── user/
            └── observation.jinja2
```

### 2. Create Configuration

Create `prompts/configs/my_agent.yaml`:

```yaml
metadata:
  name: my_agent
  description: "My AI agent"
  current_version: "v1"

parameters:
  input_text:
    type: str
    required: true
  temperature:
    type: float
    required: false
    default: 0.7

llm_config:
  model: "gpt-4"
  temperature: 0.7
  max_tokens: 1000
```

### 3. Create Templates

Create `prompts/templates/system/v1.jinja2`:

```jinja2
You are a helpful AI assistant.

{% include 'common/instructions.jinja2' %}

Temperature setting: {{ temperature }}
```

Create `prompts/templates/user/observation.jinja2`:

```jinja2
User input: {{ input_text }}

Please provide a helpful response.
```

### 4. Use in Code

```python
from prompt_manager import PromptManager

# Initialize
manager = PromptManager("prompts")

# Render messages
messages = manager.render_messages(
    prompt_name="my_agent",
    version="v1",
    input_text="Hello, how are you?",
    temperature=0.8
)

# Use with OpenAI
import openai
response = openai.chat.completions.create(
    model=manager.get_llm_config("my_agent")["model"],
    messages=messages
)
```

---

## 📚 Documentation

### Basic Usage

#### Initialize PromptManager

```python
from prompt_manager import PromptManager

# Basic initialization
manager = PromptManager("prompts")

# With custom settings
manager = PromptManager(
    prompts_dir="prompts",
    enable_cache=True,
    template_cache_size=50,
    render_cache_size=200,
    dev_mode=False
)
```

#### Render Single Template

```python
# Render a specific template type (system or user)
system_prompt = manager.render(
    prompt_name="trading_agent",
    template_type="system",
    version="v2",
    symbol="BTC-USD",
    current_price=45000.0
)
```

#### Render Message List

```python
# Render both system and user prompts
messages = manager.render_messages(
    prompt_name="trading_agent",
    version="v2",
    symbol="BTC-USD",
    current_price=45000.0,
    rsi=32.5
)

# Result format (OpenAI-compatible)
# [
#     {"role": "system", "content": "..."},
#     {"role": "user", "content": "..."}
# ]
```

### Advanced Features

#### Version Management

```python
# Use specific version
messages_v1 = manager.render_messages(
    "agent", version="v1", **params
)

# Use default version (from config)
messages_default = manager.render_messages(
    "agent", **params
)

# List available versions
versions = manager.list_versions("system")
# ['v1', 'v2', 'v3']
```

#### Configuration Inheritance

In your YAML config:

```yaml
# child_agent.yaml
extends: "parent_agent"  # Inherits from parent_agent.yaml

metadata:
  name: child_agent
  # Other metadata...

parameters:
  # Child parameters override parent
  temperature:
    type: float
    default: 0.9  # Override parent's default
```

#### Template Includes

```jinja2
{# system/v2.jinja2 #}
You are a trading agent.

{% include 'common/risk_management.jinja2' %}

{# You can pass parameters to includes #}
{{ 'common/json_schema.jinja2' | render(schema_type='trading') }}
```

#### Parameter Validation

```python
# In config YAML
parameters:
  risk_level:
    type: float
    required: true
    default: 0.02
    description: "Risk per trade"

# Validation happens automatically
messages = manager.render_messages(
    "agent",
    risk_level=0.05  # ✅ Valid
)

messages = manager.render_messages(
    "agent",
    risk_level="high"  # ❌ TypeError: cannot convert 'high' to float
)
```

#### Caching

```python
# Enable caching (default)
manager = PromptManager("prompts", enable_cache=True)

# First render (cold)
messages1 = manager.render_messages("agent", **params)  # ~20ms

# Second render (cached)
messages2 = manager.render_messages("agent", **params)  # ~1ms

# Check cache stats
stats = manager.cache_stats()
print(stats['render_cache']['hit_rate'])  # "75.00%"

# Clear cache
manager.clear_cache()
```

#### Development Mode

```python
# Enable dev mode (disables caching, enables hot-reload)
manager = PromptManager("prompts", dev_mode=True)

# Now you can edit templates/configs and see changes immediately
messages = manager.render_messages("agent", **params)
# Edit your templates...
messages = manager.render_messages("agent", **params)  # Uses updated template
```

### Utility Functions

```python
# List all prompts
prompts = manager.list_prompts()
# ['trading_agent', 'research_agent', ...]

# Get prompt info
info = manager.info("trading_agent")
# Returns dict with metadata, parameters, llm_config, etc.

# Get LLM config
llm_config = manager.get_llm_config("trading_agent")
# {'model': 'gpt-4', 'temperature': 0.3, ...}

# Reload specific prompt (for development)
manager.reload("trading_agent")
```

---

## 📖 Examples

See the `examples/` directory for comprehensive examples:

- **`basic_usage.py`**: 7 basic examples covering core functionality
- **`advanced_usage.py`**: 7 advanced examples for production patterns

Run examples:

```bash
# Basic examples
python examples/basic_usage.py

# Advanced examples
python examples/advanced_usage.py
```

Example output:

```
⏱️  Cold render time: 18.50ms
⏱️  Cached render time: 0.95ms
🚀 Speedup: 19.5x faster

📊 Cache Statistics:
   Template cache: 2/50 items
   Render cache: 2/200 items
   Hit rate: 50.00%
```

---

## 🏗️ Architecture

### Design Philosophy

This system combines best practices from two production agent systems:

1. **ValueCell**: Structured configs, caching, testing
2. **Multi-AI-Trader**: Simple templates, version coexistence, excellent docs

### Key Components

```
┌─────────────────────────────────────┐
│        PromptManager                │
│  (Main API, coordinates all parts)  │
└──────────────┬──────────────────────┘
               │
       ┌───────┴────────┐
       │                │
┌──────▼──────┐   ┌────▼──────┐
│ ConfigLoader│   │  Template │
│  (YAML)     │   │  Renderer │
│             │   │  (Jinja2) │
└─────────────┘   └───────────┘
       │                │
       └───────┬────────┘
               │
       ┌───────▼────────┐
       │ MultiLevelCache│
       │  (LRU caches)  │
       └────────────────┘
```

### File Organization

```
prompts/
├── configs/          # YAML configurations
│   ├── agent1.yaml
│   └── agent2.yaml
├── templates/        # Jinja2 templates
│   ├── common/       # Reusable components
│   ├── system/       # System prompts (v1, v2, ...)
│   └── user/         # User prompts
└── VERSION_HISTORY.md  # Documentation (optional)
```

---

## 🧪 Testing

Run tests:

```bash
# Run all tests
pytest

# With coverage
pytest --cov=prompt_manager --cov-report=html

# Run specific test file
pytest tests/test_manager.py
```

---

## 🛠️ Best Practices

### 1. Version Your Prompts

- Keep multiple versions (v1, v2, v3) for easy rollback
- Document changes in VERSION_HISTORY.md
- Use extends for incremental improvements

### 2. Use Common Components

- Extract reusable content to `common/`
- Use `{% include %}` for composition
- Keep templates DRY

### 3. Validate Parameters

- Declare all parameters in config
- Use appropriate types
- Provide sensible defaults

### 4. Cache in Production

- Enable caching in production
- Use dev_mode=False
- Monitor cache hit rates

### 5. Hot-Reload in Development

- Use dev_mode=True locally
- Test prompt changes quickly
- Clear cache when needed

### 6. Organize by Feature

```
prompts/
├── configs/
│   ├── trading/
│   │   ├── portfolio_manager.yaml
│   │   └── risk_analyst.yaml
│   └── research/
│       └── paper_summarizer.yaml
└── templates/
    ├── trading/
    │   ├── common/
    │   ├── system/
    │   └── user/
    └── research/
        └── ...
```

---

## 🔍 Comparison with Other Systems

| Feature | PromptManager | LangChain | Plain Files |
|---------|--------------|-----------|-------------|
| Type Safety | ✅ | ⚠️ | ❌ |
| Versioning | ✅ | ⚠️ | ❌ |
| Caching | ✅ | ✅ | ❌ |
| Config Separation | ✅ | ❌ | ❌ |
| Hot Reload | ✅ | ❌ | ⚠️ |
| Template Includes | ✅ | ⚠️ | ❌ |
| Parameter Validation | ✅ | ⚠️ | ❌ |
| Zero Dependencies* | ✅ | ❌ | ✅ |

*Excluding Jinja2 and PyYAML

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

This project was inspired by and learns from:

- **ValueCell**: Structured configuration and caching strategies
- **Multi-AI-Trader**: Simple templates and version management
- Production LLM systems at scale

---

## 📬 Contact

For questions, issues, or suggestions:

- Open an issue on GitHub
- See the examples for common usage patterns
- Check the documentation in `docs/`

---

**Built with ❤️ for the LLM community**
