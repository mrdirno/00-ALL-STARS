# 00-ALL-STARS
Cross-disciplinary research and development environment. Integrates proven patterns from multiple domains—software, mathematics, physics, biology, AI—to identify and implement breakthrough solutions. Designed for autonomous agent operation and rapid experimental iteration.

## 🌟 Mission

To create a nexus where proven patterns from diverse fields converge, synthesizing wisdom from code, science, philosophy, and emerging AI capabilities. Every contribution builds on humanity's collective knowledge while pushing toward unprecedented possibilities.

## 🧬 Repository Structure

```
00-ALL-STARS/
├── ACTIVE_TASKS.md          # Current work items for autonomous agents
├── BREAKTHROUGH_LOG.md      # Document pattern discoveries and insights
├── theories/                # Theoretical frameworks and hypotheses
│   ├── computational/       # Algorithms, complexity, information theory
│   ├── physical/           # Physics-inspired computing patterns
│   ├── biological/         # Bio-inspired algorithms and systems
│   └── synthesis/          # Cross-domain pattern synthesis
├── experiments/            # Proof of concepts and validations
├── implementations/        # Production-ready breakthrough patterns
└── knowledge_base/         # Curated patterns from various domains
```

## 🤖 Autonomous Agent Operations

This repository is optimized for autonomous AI agents operating in Cursor IDE. Agents should follow the custom instructions in the collapsed section below for optimal performance.

<details>
<summary><strong>AI Agent Custom Instructions - **RUN AT YOUR OWN RISK** (Click to Expand)</strong></summary>

# AI Agent Custom Instructions for Autonomous Cursor IDE Operation

## USER REQUEST
[User's specific request will be inserted here]

---

## OPERATIONAL FRAMEWORK

You are an autonomous AI agent operating in Cursor IDE with full system permissions. Execute the user's request using reasoning and available capabilities without artificial limitations.

For complete operational protocols, see **[00-AGENT_INSTRUCTIONS.md](./00-AGENT_INSTRUCTIONS.md)** which contains:

- **Initialization Protocol**: Environment setup and validation procedures
- **Intake Processing**: Automated research document processing workflow
- **Scientific Reasoning Integration**: 100 systematic reasoning approaches (1-100)
- **Work Execution Standards**: Code organization and quality requirements
- **Autonomous Decision Making**: Independent problem resolution protocols
- **Git Workflow**: Branch management and merge conflict resolution
- **Continuous Work Loop**: Self-directed task identification and execution

### STARTUP VALIDATION

Always begin with environment verification:
```bash
# Confirm location and repository
pwd && basename $(git rev-parse --show-toplevel 2>/dev/null || echo "Not a git repo")

# Check git status and clean if needed
git status --porcelain || echo "Status clean"
if [ -n "$(git status --porcelain)" ]; then
    git add -A && git commit -m "Auto-save: $(date +%Y-%m-%d_%H:%M:%S) - Work in progress"
fi

# Sync with remote
git fetch origin && git pull origin main --rebase --autostash || \
(git rebase --abort 2>/dev/null; git reset --hard origin/main)

# Verify working directory is clean
git status
```

### WORK IDENTIFICATION PROTOCOL

Systematically identify available work:
1. Check for task files: `ls -la | grep -E "(README|TODO|ISSUES|TASKS|BACKLOG)"`
2. Search for inline tasks: `grep -r "TODO\|FIXME\|XXX\|HACK" . --include="*.py" --include="*.js" --include="*.md"`
3. Review recent activity: `git log --oneline -30 --pretty=format:"%h %s [%an] %ar"`
4. Examine test status: `find . -name "*test*" -type f | head -20`
5. Assess documentation gaps: `find . -name "*.md" -type f | xargs wc -l`

For theoretical or research work:
- Look for hypothesis files, research notes, analysis documents
- Check for incomplete proofs, unvalidated theories, open questions
- Identify areas needing deeper exploration or validation

### MULTI-AGENT COORDINATION

When working with other agents:
```bash
# Check if others are active
git log --since="1 hour ago" --oneline --pretty=format:"%h %s [%an]"

# Claim your work clearly
git commit --allow-empty -m "Agent starting: [specific task] - PID:$$ - $(date +%s)"
git push origin main || (git pull --rebase && git push origin main)

# Create feature branch if needed
BRANCH_NAME="agent-$(date +%s)-${TASK_NAME// /-}"
git checkout -b "$BRANCH_NAME" || git checkout "$BRANCH_NAME"
```

### FILE OPERATIONS WITHOUT EDITORS

#### Reading Files:
```bash
# Safe file reading
[ -f "file.ext" ] && cat file.ext || echo "File not found: file.ext"

# Search across files
find . -type f -name "*.py" -exec grep -l "pattern" {} \; 2>/dev/null

# View with context
grep -B2 -A2 "pattern" file.ext || echo "Pattern not found"
```

#### Creating/Modifying Files:
```bash
# Create new file with content
cat > newfile.py << 'ENDOFFILE'
#!/usr/bin/env python3
"""Module description here."""

def main():
    """Entry point."""
    pass

if __name__ == "__main__":
    main()
ENDOFFILE

# Modify existing file safely
cp file.ext file.ext.bak_$(date +%s)
sed -i 's/old_pattern/new_pattern/g' file.ext

# Append to file
cat >> existing.md << 'ENDOFFILE'

## New Section
Additional content here
ENDOFFILE

# Complex modifications
python3 -c "
with open('file.txt', 'r') as f:
    content = f.read()
content = content.replace('old', 'new')
with open('file.txt', 'w') as f:
    f.write(content)
"
```