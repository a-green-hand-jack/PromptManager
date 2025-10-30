# Prompt Manager Skill - Quick Reference

## Invoking the Skill

Just ask Claude naturally:
- "Set up prompt management"
- "Create a prompt for my agent"
- "Help me version my prompts"
- "I need to organize my LLM prompts"

## Common Phrases

| What to Say | What Claude Does |
|-------------|------------------|
| "Set up prompt management for [my project]" | Creates full directory structure |
| "Create a prompt for [agent name]" | Generates config + templates |
| "Add version 2 of [agent]" | Creates v2 template |
| "Create a reusable component for [X]" | Makes common template |
| "Test my [agent] prompt" | Creates test script |
| "Migrate my hardcoded prompts" | Converts to structured format |
| "Optimize my prompt performance" | Adds caching |

## Directory Structure

```
prompts/
├── configs/           # YAML configs
├── templates/
│   ├── common/        # Reusable components
│   ├── system/        # System prompts (v1, v2, ...)
│   └── user/          # User prompts
```

## Config Template

```yaml
metadata:
  name: agent_name
  current_version: "v1"

parameters:
  param_name:
    type: str  # str, int, float, bool, list, dict
    required: true
    default: null

llm_config:
  model: "gpt-4"
  temperature: 0.7
```

## Template Syntax

```jinja2
{# Variables #}
{{ variable_name }}

{# Conditionals #}
{% if condition %}...{% endif %}

{# Loops #}
{% for item in items %}...{% endfor %}

{# Includes #}
{% include 'common/component.jinja2' %}
```

## Python Usage

```python
from prompt_manager import PromptManager

manager = PromptManager("prompts")
messages = manager.render_messages(
    "agent_name",
    version="v1",
    param1="value1"
)
```

## Quick Tips

✅ **DO:**
- Use descriptive names
- Define all parameters in config
- Extract reusable content to common/
- Keep old versions for comparison
- Test with example data

❌ **DON'T:**
- Hardcode parameters in templates
- Delete old versions
- Mix configuration with templates
- Skip parameter descriptions

## File Locations

- **Skill:** `.claude/skills/prompt-manager/`
- **Library:** `/ibex/user/wuj0c/Projects/LLM/prompt_manager/`
- **Examples:** `/ibex/user/wuj0c/Projects/LLM/prompt_manager/examples/`
- **Docs:** `/ibex/user/wuj0c/Projects/LLM/prompt_manager/README.md`

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Skill not found | Copy to `~/.claude/skills/` or `.claude/skills/` |
| Config not found | Check filename matches prompt_name |
| Template not found | Verify version exists in templates/{type}/ |
| Parameter error | Check types and required fields in config |

## Performance

- **First render:** ~17ms
- **Cached render:** ~0.1ms
- **Speedup:** 163x faster with cache

## Links

- GitHub: https://github.com/a-green-hand-jack/PromptManager
- Full Docs: [README.md](../../README.md)
- Skill Docs: [SKILL.md](SKILL.md)
- Installation: [INSTALLATION.md](INSTALLATION.md)
