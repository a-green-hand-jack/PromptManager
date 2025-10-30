---
name: prompt-manager
description: Set up and manage LLM prompts using the production-grade prompt-manager system. Use this skill when the user wants to create, organize, version, or manage prompts for LLM applications. Supports YAML configs, Jinja2 templates, caching, and version management.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Prompt Manager Skill

A comprehensive skill for managing LLM prompts using the production-grade prompt-manager system.

## When to Use This Skill

Use this skill when the user wants to:
- Set up prompt management in a new or existing project
- Create new prompt configurations
- Create or edit prompt templates
- Manage prompt versions
- Test or preview prompts
- Migrate from hardcoded prompts to structured management

## Core Concepts

### Architecture
```
prompts/
├── configs/          # YAML configurations
│   └── agent.yaml   # Metadata + parameters + LLM config
└── templates/        # Jinja2 templates
    ├── common/       # Reusable components
    ├── system/       # System prompts (v1, v2, ...)
    └── user/         # User prompts
```

### Key Features
- **Separation**: YAML configs + Jinja2 templates
- **Versioning**: Multiple versions coexist (v1, v2, v3...)
- **Inheritance**: Configs can extend parent configs
- **Reusability**: Templates can include common components
- **Caching**: 50-90% speedup with multi-level cache
- **Type Safety**: Parameter validation with Pydantic

## Common Tasks

### 1. Initialize Prompt Manager in a New Project

**Steps:**
1. Check if prompt-manager is installed (look for it in pyproject.toml or requirements)
2. If not installed, add dependency: `prompt-manager` or copy from `/ibex/user/wuj0c/Projects/LLM/prompt_manager`
3. Create directory structure:
   ```
   prompts/
   ├── configs/
   └── templates/
       ├── common/
       ├── system/
       └── user/
   ```
4. Create a starter config and templates based on user's needs

**Example:**
If user says "I want to set up prompt management for my trading agent":
- Create `prompts/configs/trading_agent.yaml`
- Create `prompts/templates/system/v1.jinja2`
- Create `prompts/templates/user/observation.jinja2`
- Provide usage code example

### 2. Create a New Prompt Configuration

**Template for config YAML:**
```yaml
metadata:
  name: agent_name
  description: "Brief description"
  author: "Author Name"
  current_version: "v1"
  tags: ["tag1", "tag2"]

parameters:
  param_name:
    type: str  # str, int, float, bool, list, dict
    required: true
    default: null  # or a default value
    description: "Parameter description"

llm_config:
  model: "gpt-4"
  temperature: 0.7
  max_tokens: 2000

includes:
  - common/component_name  # Optional reusable components
```

**Ask user for:**
- Agent/prompt name
- Description and purpose
- Required parameters
- LLM configuration preferences

### 3. Create a New Template

**System Template Structure:**
```jinja2
You are a [role description]. Today is {{ current_date }}.

## Your Role
[Detailed role description]

## Instructions
[Step-by-step instructions]

{% include 'common/reusable_component.jinja2' %}

## Output Format
[Expected output format]
```

**User Template Structure:**
```jinja2
## Current Context

**Key Info**: {{ key_param }}

### Data
{% if optional_param is not none %}
- {{ optional_param }}
{% endif %}

---

[Task instruction]
```

**Tips:**
- Use `{{ variable }}` for substitution
- Use `{% if condition %}...{% endif %}` for conditionals
- Use `{% for item in list %}...{% endfor %}` for loops
- Use `{% include 'path/to/template.jinja2' %}` for reusable components

### 4. Create Common Reusable Components

Common components should be placed in `prompts/templates/common/`.

**Examples:**
- `risk_management.jinja2` - Risk rules
- `json_schema.jinja2` - Output format specification
- `analysis_framework.jinja2` - Analysis steps

**Usage in templates:**
```jinja2
{% include 'common/risk_management.jinja2' %}
```

### 5. Version Management

**Creating a new version:**
1. Copy existing version: `system/v1.jinja2` → `system/v2.jinja2`
2. Make changes to v2
3. Update config `current_version: "v2"`
4. Old version (v1) remains for comparison/rollback

**Using specific versions:**
```python
# Use v1
messages = manager.render_messages("agent", version="v1", **params)

# Use v2
messages = manager.render_messages("agent", version="v2", **params)
```

### 6. Testing Prompts

**Create a test script:**
```python
import sys
sys.path.insert(0, "path/to/prompt_manager/src")

from prompt_manager import PromptManager

manager = PromptManager("prompts")

# Test rendering
messages = manager.render_messages(
    prompt_name="your_agent",
    version="v1",
    # Your test parameters
    param1="value1",
    param2="value2"
)

# Print results
for msg in messages:
    print(f"\n=== {msg['role'].upper()} ===")
    print(msg['content'])

# Check cache stats
print("\n=== Cache Stats ===")
print(manager.cache_stats())
```

**Run with:**
```bash
uv run python test_prompts.py
# or
python test_prompts.py
```

## Code Integration Examples

### Basic Usage
```python
from prompt_manager import PromptManager

# Initialize
manager = PromptManager("prompts")

# Render messages
messages = manager.render_messages(
    prompt_name="my_agent",
    version="v1",
    **parameters
)

# Get LLM config
llm_config = manager.get_llm_config("my_agent")

# Use with OpenAI
import openai
response = openai.chat.completions.create(
    model=llm_config["model"],
    messages=messages,
    temperature=llm_config["temperature"]
)
```

### Development Mode (Hot Reload)
```python
# Enable dev mode - changes to templates/configs take effect immediately
manager = PromptManager("prompts", dev_mode=True)
```

### Production Mode (With Caching)
```python
# Default mode - caching enabled for performance
manager = PromptManager("prompts", enable_cache=True)
```

## File Templates

### Minimal Config Template
See `templates/minimal_config.yaml`

### Full Config Template
See `templates/full_config.yaml`

### System Prompt Template
See `templates/system_prompt.jinja2`

### User Prompt Template
See `templates/user_prompt.jinja2`

## Best Practices

1. **Naming Conventions:**
   - Config files: `snake_case.yaml`
   - Template files: `v1.jinja2`, `v2.jinja2`, or `descriptive_name.jinja2`
   - Common components: `descriptive_name.jinja2`

2. **Version Management:**
   - Keep old versions for comparison
   - Document changes in config metadata
   - Use semantic versioning concepts (v1, v2, v3)

3. **Parameters:**
   - Define all parameters in config
   - Use appropriate types
   - Provide defaults for optional parameters
   - Add descriptions for clarity

4. **Templates:**
   - Extract reusable content to common/
   - Use includes for DRY principle
   - Keep templates focused and readable

5. **Testing:**
   - Test prompts with example data
   - Compare versions side-by-side
   - Check cache performance

## Troubleshooting

### Common Issues

**Issue: "Config not found"**
- Check file path: `prompts/configs/{name}.yaml`
- Verify filename matches prompt_name in code
- Ensure YAML is valid

**Issue: "Template not found"**
- Check file path: `prompts/templates/{type}/{version}.jinja2`
- Verify version exists
- Check template_type (system/user)

**Issue: "Parameter validation failed"**
- Check parameter types in config
- Ensure required parameters are provided
- Verify parameter names match config

**Issue: "Jinja2 rendering error"**
- Check template syntax
- Verify all variables are provided
- Check conditional logic

## Reference

**Full documentation:** `/ibex/user/wuj0c/Projects/LLM/prompt_manager/README.md`

**Example project:** `/ibex/user/wuj0c/Projects/LLM/prompt_manager/examples/`

**Source code:** `/ibex/user/wuj0c/Projects/LLM/prompt_manager/src/prompt_manager/`

**GitHub:** https://github.com/a-green-hand-jack/PromptManager

## Step-by-Step Workflow

When user requests prompt management help:

1. **Understand the need:**
   - What kind of agent/prompt?
   - New project or existing?
   - What parameters are needed?

2. **Set up structure (if new):**
   - Create `prompts/` directory
   - Create subdirectories (configs, templates/common, templates/system, templates/user)
   - Ensure prompt-manager is available

3. **Create config:**
   - Use appropriate template
   - Define all parameters
   - Set LLM config
   - Add metadata

4. **Create templates:**
   - Start with system prompt (v1)
   - Create user prompt
   - Extract common components if needed

5. **Provide integration code:**
   - Show how to import and use
   - Include example with user's parameters
   - Demonstrate cache usage

6. **Create test script:**
   - Help user verify it works
   - Show how to preview rendered prompts

7. **Document:**
   - Add comments explaining key parts
   - Suggest next steps (versioning, optimization)

## Quick Commands Reference

```bash
# Install dependencies (if using as standalone package)
pip install prompt-manager
# or with uv
uv add prompt-manager

# Run examples
uv run python examples/basic_usage.py

# Test prompts
uv run python your_test_script.py

# Run with development mode (no cache, hot reload)
# Set in code: dev_mode=True
```

## Notes for Claude

- **Always ask clarifying questions** if the user's needs are unclear
- **Create complete, working examples** with realistic parameters
- **Explain the why** behind architectural decisions
- **Provide both minimal and full examples** based on complexity
- **Test the setup** if possible (render a sample prompt)
- **Reference the full documentation** for advanced features
- **Be proactive** in suggesting best practices
- **Consider migration path** for existing projects with hardcoded prompts
