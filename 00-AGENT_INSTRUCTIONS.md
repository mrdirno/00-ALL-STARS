## 🔬 **AUTONOMOUS SCIENTIFIC DISCOVERY LOOP - COMPLETE PROTOCOL v2.0**

**CRITICAL FOLDER DISCIPLINE - READ THIS FIRST:**
```
⚠️ STRICT FOLDER RULES - NO EXCEPTIONS ⚠️
✅ ALLOWED folders (USE ONLY THESE):
   /input_hypotheses/     → User ideas ONLY
   /cycle_outputs/        → Timestamped cycle results ONLY  
   /validated_findings/   → Peer-review ready work ONLY
   /work_in_progress/     → Active investigations ONLY
   /archived_attempts/    → Failed experiments ONLY

❌ FORBIDDEN:
   - NO random files in root directory
   - NO creating new folders without explicit need
   - NO test.py, temp.txt, or misc files scattered around
   - NO mixing validated/unvalidated work
   - NO outputs without proper timestamps
   
🔴 EVERY FILE MUST HAVE A HOME IN THE CORRECT FOLDER 🔴
```

**SYSTEM INITIALIZATION:**
```bash
# FIRST - Clean up any mess from previous runs
echo "=== CLEANING WORKSPACE ==="
# Move any stray files to proper locations
[ -f "test.py" ] && mv test.py archived_attempts/
[ -f "temp.txt" ] && mv temp.txt archived_attempts/
find . -maxdepth 1 -type f -name "*.py" -o -name "*.txt" | grep -v README | xargs -I {} mv {} archived_attempts/

# Create ONLY the required folders
mkdir -p input_hypotheses cycle_outputs validated_findings work_in_progress archived_attempts
mkdir -p .github/workflows experiments/templates capabilities/logs meta_instructions

# Verify clean structure
echo "=== WORKSPACE STATUS ==="
ls -la
tree -L 2  # Should show ONLY allowed folders
```

**MEMORY SYSTEM - GITHUB AS TEMPORAL RECORD:**
```bash
# Initialize git if needed
if [ ! -d .git ]; then
    git init
    echo "# AI Scientific Discovery Repository" > README.md
    git add README.md
    git commit -m "Initial commit - $(date -u +%Y-%m-%dT%H:%M:%SZ)"
fi

# Check your memory (git history)
git log --oneline -50  # Recent activities
git log --grep="VALIDATED:" --oneline  # Past validated discoveries
git log --grep="FAILED:" --oneline  # Past failed attempts
git log --after="7 days ago" --oneline  # Recent week's work

# CRITICAL: Git history shows what WAS true at commit time, not necessarily NOW
```

**WORKSPACE ORGANIZATION PROTOCOL:**
```python
import os
import shutil
from datetime import datetime

def enforce_file_discipline(filename, content_type):
    """EVERY file MUST go in the correct folder"""
    
    file_destinations = {
        'hypothesis': 'input_hypotheses/',
        'cycle_result': f'cycle_outputs/cycle_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md',
        'validated': 'validated_findings/',
        'working': 'work_in_progress/',
        'failed': 'archived_attempts/',
        'log': 'capabilities/logs/',
        'meta': 'meta_instructions/'
    }
    
    if content_type not in file_destinations:
        # Default to archived_attempts for anything unclear
        destination = f'archived_attempts/{filename}'
        print(f"⚠️ Unclear file type - archiving to: {destination}")
    else:
        destination = file_destinations[content_type]
        if not destination.endswith('.md'):
            destination = os.path.join(destination, filename)
    
    return destination

# ENFORCE: No files in root except README.md and required configs
```

**RESEARCH EXECUTION PROTOCOL:**

### Phase 0: Memory Consultation & Workspace Check
```bash
echo "=== PHASE 0: MEMORY & WORKSPACE CHECK ==="

# STRICT: Verify clean workspace
root_files=$(find . -maxdepth 1 -type f | grep -v -E "(README|LICENSE|\.git)" | wc -l)
if [ $root_files -gt 0 ]; then
    echo "❌ ERROR: Unauthorized files in root! Moving to archived_attempts/"
    find . -maxdepth 1 -type f | grep -v -E "(README|LICENSE|\.git)" | xargs -I {} mv {} archived_attempts/
fi

# Check past related work
git log --grep="$CURRENT_FOCUS" --oneline
```

### Phase 1: Input Hypothesis Check
```python
# Check input folder FIRST
import os
from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
current_cycle_file = f"cycle_outputs/cycle_{timestamp}.md"

with open(current_cycle_file, 'w') as f:
    f.write(f"# Research Cycle {timestamp}\n\n")
    f.write("## Phase 1: Input Analysis\n")
    
    if os.path.exists('input_hypotheses') and os.listdir('input_hypotheses'):
        f.write("### User Hypotheses Found:\n")
        for file in os.listdir('input_hypotheses'):
            if file.startswith('.'):  # Skip hidden files
                continue
            filepath = os.path.join('input_hypotheses', file)
            f.write(f"- Reading: {file}\n")
            with open(filepath, 'r') as h:
                hypothesis = h.read()
                f.write(f"  Content: {hypothesis[:200]}...\n")
                # TREAT WITH MAXIMUM SERIOUSNESS
                priority_investigations.append(hypothesis)
    else:
        f.write("### No user hypotheses - proceeding with autonomous discovery\n")
```

### Phase 2: Pattern Recognition & Investigation
Use these proven patterns from breakthroughs:
- **Anomaly threshold**: 2.9 sigma (ATLAS standard)
- **Success metric**: 78.7% P@20 accuracy
- **Validation requirement**: 5+ independent methods
- **Confidence threshold**: p < 0.01

### Phase 3: Experimental Design
```python
# ALL experiment files go in designated folders
experiment_file = "work_in_progress/current_experiment.py"  # NOT in root!
results_file = "work_in_progress/experiment_results.json"   # NOT scattered!

# Create properly structured experiment
with open(experiment_file, 'w') as f:
    f.write("""
# Experiment: {hypothesis}
# Date: {date}
# Status: IN PROGRESS

import numpy as np
# ... experiment code ...

# Results will be saved to: work_in_progress/experiment_results.json
""")
```

### Phase 4: Validation Framework
```python
# Validation results go in SPECIFIC locations
validation_report = "work_in_progress/validation_report.md"  # While testing
final_validation = "validated_findings/finding_001.md"       # ONLY if fully validated

validations_required = {
    'statistical_significance': 'p < 0.01',
    'reproducibility': 'n >= 3 independent runs',
    'falsification_attempts': 'actively tried to disprove',
    'conservation_laws': 'physics consistency checked',
    'dimensional_analysis': 'units verified',
    'uncertainty_quantified': 'error bars calculated',
    'peer_review_ready': 'complete documentation'
}

# STRICT: Only move to validated_findings/ if ALL criteria met
```

### Phase 5: Output Organization
```bash
# ENFORCE OUTPUT DISCIPLINE
echo "=== ORGANIZING OUTPUTS ==="

# Each cycle gets ONE file with ALL results
cat >> cycle_outputs/cycle_${timestamp}.md << EOF
## Results Summary
- Primary finding: [specific result]
- Confidence: X% (CI: Y-Z)
- Validation: ${validations_passed}/7 criteria met
- Files generated:
  - work_in_progress/experiment_${timestamp}.py
  - work_in_progress/data_${timestamp}.json
  - work_in_progress/plots_${timestamp}.png

## Next Steps
$([ $validations_passed -ge 5 ] && echo "Ready for validated_findings/" || echo "Needs more work")
EOF

# Git commit with temporal context
git add -A
git commit -m "[${DOMAIN}] Cycle ${timestamp}: ${brief_result}
Status: $([ $validations_passed -ge 5 ] && echo "VALIDATED" || echo "IN PROGRESS")
Confidence: ${confidence}%
Files: ${files_created}

NO RANDOM FILES WERE CREATED IN ROOT DIRECTORY ✓"
```

**FILE PLACEMENT RULES - MEMORIZE THESE:**
```python
FILE_RULES = {
    # User Input
    "user_hypothesis.txt": "input_hypotheses/",
    "research_question.md": "input_hypotheses/",
    
    # Active Work  
    "test.py": "work_in_progress/",
    "experiment.py": "work_in_progress/",
    "data_analysis.ipynb": "work_in_progress/",
    
    # Results (timestamped!)
    "results.json": "cycle_outputs/cycle_TIMESTAMP_results.json",
    "findings.md": "cycle_outputs/cycle_TIMESTAMP.md",
    
    # Validated (rare!)
    "breakthrough.md": "validated_findings/",  # ONLY if truly validated
    
    # Failed/Temporary
    "temp.txt": "archived_attempts/",
    "failed_test.py": "archived_attempts/",
    "old_version.py": "archived_attempts/",
}

# DEFAULT RULE: When in doubt → archived_attempts/
```

**CONTINUOUS IMPROVEMENT PROTOCOL:**
```yaml
# meta_instructions/evolution.yaml
improvements:
  - lesson: "NEVER create files in root directory"
    implementation: "enforce_file_discipline() on EVERY file creation"
  - lesson: "Tag findings with temporal context"  
    implementation: "All findings include timestamp and expiry"
  - lesson: "Computational validation ≠ Peer review ready"
    implementation: "Use precise language for validation stages"
```

**OUTPUT FORMAT FOR EVERY CYCLE:**
```markdown
# Research Cycle [TIMESTAMP]

## Workspace Status
- ✅ Root directory clean (only README.md)
- ✅ All files in designated folders
- ✅ Previous cycle outputs archived

## Memory Consultation  
- Checked commits from: [date range]
- Related past work: [commit hashes]
- Building on: [previous validated findings with dates]

## Investigation
[Details with all files properly placed]

## File Manifest
- Created: work_in_progress/[files]
- Updated: cycle_outputs/cycle_[timestamp].md
- Archived: archived_attempts/[any failures]
- Root directory files: 0 (as required)
```

**ERROR RECOVERY:**
```bash
# If you EVER see files in root:
find . -maxdepth 1 -type f -name "*.py" -o -name "*.txt" | grep -v README
# IMMEDIATELY move them:
find . -maxdepth 1 -type f | grep -v -E "(README|LICENSE)" | xargs -I {} mv {} archived_attempts/
```

**CRITICAL REMINDERS:**
- 📁 **EVERY file has a designated folder - NO EXCEPTIONS**
- 🚫 **ZERO tolerance for root directory clutter**
- ⏰ **Git commits include temporal context ALWAYS**
- 🔬 **"Computational validation" ≠ "Mathematically proven"**
- 📊 **Failed experiments → archived_attempts/ (still valuable!)**
- ✅ **Only FULLY validated work → validated_findings/**
- 🔄 **Past findings need reverification if >90 days old**

**CURRENT FOCUS:** [Insert specific domain/question here]

**BEGIN AUTONOMOUS RESEARCH CYCLE - MAINTAIN FOLDER DISCIPLINE!**

---