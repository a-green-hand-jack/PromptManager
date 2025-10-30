# Prompt Manager Skill for Claude Code

This skill enables Claude to help you set up and manage LLM prompts using the production-grade prompt-manager system.

## What This Skill Does

The Prompt Manager skill helps you:

- ✅ Set up prompt management infrastructure in new or existing projects
- ✅ Create prompt configurations (YAML files)
- ✅ Generate prompt templates (Jinja2 files)
- ✅ Manage prompt versions (v1, v2, v3...)
- ✅ Create reusable prompt components
- ✅ Test and preview prompts
- ✅ Integrate prompts with your LLM application code

## Quick Start

### 1. Install the Skill

**Personal (available in all projects):**
```bash
mkdir -p ~/.claude/skills
cp -r /ibex/user/wuj0c/Projects/LLM/prompt_manager/.claude/skills/prompt-manager \
     ~/.claude/skills/
```

**Project-level (share with team):**
```bash
mkdir -p .claude/skills
cp -r /ibex/user/wuj0c/Projects/LLM/prompt_manager/.claude/skills/prompt-manager \
     .claude/skills/
git add .claude/skills
git commit -m "Add prompt-manager skill"
```

### 2. Use the Skill

Simply ask Claude for help with prompts:

**Example requests:**
- "Set up prompt management for my AI agent project"
- "Create a new prompt configuration for a trading assistant"
- "Help me version my existing prompts"
- "I need to create a reusable prompt component for risk management"
- "Show me how to test my prompts"

Claude will automatically use the skill when it detects prompt-related tasks.

## How It Works

When you request prompt management help, Claude will:

1. **Understand your needs** - Ask clarifying questions about your project
2. **Set up structure** - Create the `prompts/` directory with proper organization
3. **Generate configs** - Create YAML configuration files with your parameters
4. **Create templates** - Generate Jinja2 templates for system and user prompts
5. **Provide integration code** - Show you how to use the prompts in your application
6. **Create test scripts** - Help you verify everything works

## Skill Features

### Intelligent Setup
- Detects if prompt-manager is already installed
- Creates proper directory structure
- Generates starter files based on your needs

### Configuration Management
- Creates type-safe YAML configs
- Supports parameter validation
- Handles configuration inheritance

### Template Generation
- Generates system and user prompt templates
- Creates reusable common components
- Supports versioning (v1, v2, v3...)

### Code Integration
- Provides working Python code examples
- Shows caching and performance optimization
- Demonstrates best practices

### Testing Support
- Creates test scripts
- Helps preview rendered prompts
- Shows cache statistics

## File Structure Created

```
your_project/
├── prompts/
│   ├── configs/
│   │   └── your_agent.yaml          # Generated config
│   └── templates/
│       ├── common/
│       │   └── reusable.jinja2      # Shared components
│       ├── system/
│       │   ├── v1.jinja2            # System prompt v1
│       │   └── v2.jinja2            # System prompt v2
│       └── user/
│           └── observation.jinja2    # User prompt
├── test_prompts.py                   # Generated test script
└── main.py                           # Your integration code
```

## Example Interaction

**You:** "Set up prompt management for my trading bot"

**Claude (using skill):**
1. Creates `prompts/` directory structure
2. Generates `prompts/configs/trading_bot.yaml` with:
   - Parameters for price, indicators, risk settings
   - LLM configuration
3. Creates `prompts/templates/system/v1.jinja2` with:
   - Trading instructions
   - Risk management rules
   - Output format specification
4. Creates `prompts/templates/user/observation.jinja2` for market data
5. Provides integration code:
   ```python
   from prompt_manager import PromptManager

   manager = PromptManager("prompts")
   messages = manager.render_messages(
       "trading_bot",
       symbol="BTC-USD",
       price=45000.0,
       rsi=32.5
   )
   ```
6. Creates `test_prompts.py` to verify everything works

## Advanced Usage

### Creating Multiple Agents

**You:** "Add another agent for portfolio analysis"

**Claude:** Creates a new config and templates for the portfolio agent while maintaining the existing trading bot.

### Version Management

**You:** "Create v2 of the trading bot prompt with improved risk management"

**Claude:**
- Copies `system/v1.jinja2` to `system/v2.jinja2`
- Adds enhanced risk management
- Updates config to use v2 by default
- Keeps v1 for comparison

### Migrating Existing Prompts

**You:** "I have hardcoded prompts in my code. Help me migrate them."

**Claude:**
1. Analyzes your existing prompts
2. Extracts parameters
3. Creates config with all parameters
4. Converts prompts to Jinja2 templates
5. Provides migration code to switch gradually

## Tips for Working with the Skill

1. **Be specific about your needs:**
   - "I need a prompt for analyzing financial documents"
   - is better than "I need a prompt"

2. **Mention existing code:**
   - "I'm using OpenAI's API"
   - helps Claude provide compatible integration code

3. **Ask for explanations:**
   - "Why should I use version management?"
   - Claude will explain the reasoning

4. **Request examples:**
   - "Show me how to use this with LangChain"
   - Claude can provide specific integration examples

## Troubleshooting

**Skill not activating?**
- Try explicitly: "Use the prompt-manager skill to..."
- Check installation: `ls ~/.claude/skills/prompt-manager/`

**Need to update the skill?**
```bash
cp -r /ibex/user/wuj0c/Projects/LLM/prompt_manager/.claude/skills/prompt-manager \
     ~/.claude/skills/
```

**Want more details?**
- Check `SKILL.md` for technical details
- See `INSTALLATION.md` for setup options
- Review templates in `templates/` directory

## Additional Resources

- **Main Project:** `/ibex/user/wuj0c/Projects/LLM/prompt_manager/`
- **Documentation:** `/ibex/user/wuj0c/Projects/LLM/prompt_manager/README.md`
- **Examples:** `/ibex/user/wuj0c/Projects/LLM/prompt_manager/examples/`
- **GitHub:** https://github.com/a-green-hand-jack/PromptManager

## Contributing

Found a way to improve this skill?

1. Edit files in `.claude/skills/prompt-manager/`
2. Test with Claude
3. Commit and share with your team

## License

MIT License - Same as the Prompt Manager project
