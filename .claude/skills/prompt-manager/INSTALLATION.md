# Installing Prompt Manager Skill

## Option 1: Personal Skill (Available in All Projects)

Copy the skill to your personal skills directory:

```bash
# Create personal skills directory if it doesn't exist
mkdir -p ~/.claude/skills

# Copy the skill
cp -r /ibex/user/wuj0c/Projects/LLM/prompt_manager/.claude/skills/prompt-manager \
     ~/.claude/skills/
```

The skill will now be available in all your projects.

## Option 2: Project Skill (Team Sharing)

Keep the skill in your project's `.claude/skills/` directory:

```bash
# In your project root
mkdir -p .claude/skills

# Copy the skill
cp -r /ibex/user/wuj0c/Projects/LLM/prompt_manager/.claude/skills/prompt-manager \
     .claude/skills/
```

Commit to git to share with your team:

```bash
git add .claude/skills/prompt-manager
git commit -m "Add prompt-manager skill"
git push
```

## Using the Skill

Once installed, invoke the skill by saying:

- "Use the prompt-manager skill to set up prompt management in my project"
- "I need to create a new prompt configuration for my trading agent"
- "Help me organize my LLM prompts using prompt-manager"

Claude will automatically use the skill when appropriate.

## Installing the Prompt Manager Library

The skill helps you manage prompts, but you also need the prompt-manager library:

### Option A: From PyPI (when published)
```bash
pip install prompt-manager
# or with uv
uv add prompt-manager
```

### Option B: From Source (current)
```bash
# Clone or copy the library
cp -r /ibex/user/wuj0c/Projects/LLM/prompt_manager/src/prompt_manager \
     your_project/src/

# Or add to your pyproject.toml
[project]
dependencies = [
    "jinja2>=3.1.0",
    "pyyaml>=6.0",
    "pydantic>=2.0.0",
]
```

### Option C: As Git Submodule
```bash
# In your project
git submodule add git@github.com:a-green-hand-jack/PromptManager.git libs/prompt_manager

# Use it
import sys
sys.path.insert(0, "libs/prompt_manager/src")
from prompt_manager import PromptManager
```

## Verifying Installation

Test the skill:

```bash
# In Claude Code, say:
# "Use prompt-manager skill to create a test prompt"
```

Test the library:

```python
from prompt_manager import PromptManager
print("✅ Prompt Manager installed successfully!")
```

## Updating the Skill

### Personal Skills
```bash
cp -r /ibex/user/wuj0c/Projects/LLM/prompt_manager/.claude/skills/prompt-manager \
     ~/.claude/skills/
```

### Project Skills
```bash
git pull  # If in a git repository
# or manually copy updated files
```

## Uninstalling

### Personal Skills
```bash
rm -rf ~/.claude/skills/prompt-manager
```

### Project Skills
```bash
rm -rf .claude/skills/prompt-manager
git rm -r .claude/skills/prompt-manager  # If committed
```
