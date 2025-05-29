# 🔬 Autonomous Scientific Discovery Repository

This repository implements a complete autonomous scientific discovery system with temporal memory management through Git history and advanced contamination prevention protocols.

## 📁 Repository Structure

```
00-ALL-STARS/
├── input_hypotheses/          # 📥 User drops research hypotheses here
├── cycle_outputs/             # 📤 Agent research cycle results
├── validated_findings/        # ✅ Confirmed scientific discoveries
├── work_in_progress/         # 🔄 Active research materials
├── archived_attempts/        # 📚 Failed attempts and learnings
├── .github/workflows/        # 🤖 Automated workflows
├── experiments/templates/    # 🧪 Experiment templates
├── capabilities/            # 🛠️ Agent tools and capabilities
├── meta_instructions/       # 📋 Knowledge evolution tracking
└── 00-AGENT_INSTRUCTIONS.md # 🧠 Complete agent protocol v2.0
```

## 🚀 Quick Start

### For Users:
1. **Drop research hypotheses** in `input_hypotheses/` folder
2. **Agents will automatically process** them through the discovery protocol
3. **Check results** in `cycle_outputs/` and `validated_findings/`

### For Agents:
1. **Read** `00-AGENT_INSTRUCTIONS.md` for complete protocol v2.0
2. **Configure headless operation** to prevent display blocking
3. **Consult memory** via git history before starting
4. **Follow strict folder discipline** - NO files in root directory
5. **Document everything** with rich commit messages

## 🛡️ Contamination Prevention & Scientific Integrity

This repository implements **military-grade** protocols to prevent:
- ❌ **Automated content generation** without scientific basis
- ❌ **Fake validation** with arbitrary metrics
- ❌ **Pseudoscientific content** proliferation
- ❌ **Discovery claims** without rigorous validation
- ❌ **Root directory clutter** - strict folder discipline enforced
- ❌ **Display blocking** - headless operation required

### 🔒 **Folder Discipline (STRICTLY ENFORCED)**
```
⚠️ ZERO TOLERANCE FOR ROOT DIRECTORY FILES ⚠️
✅ EVERY file must go in designated folder
✅ Automatic cleanup protocols active
✅ Stray files moved to archived_attempts/
```

## 🖥️ Headless Operation Protocol

**NEW**: Prevents automation blocking by display commands:
```bash
export MPLBACKEND=Agg           # Non-interactive matplotlib
export DISPLAY=:99             # Virtual display
export QT_QPA_PLATFORM=offscreen  # Qt applications
export PLOTLY_RENDERER=png     # Plotly file output
```

All plots saved as files, never displayed. Emergency recovery commands included.

## 🧠 Temporal Memory System

This repository uses **Git history as temporal memory**:
- Every commit preserves what was known at that moment
- Historical findings are always dated when referenced
- Past validations expire and need reverification after 90 days
- Failed attempts become learning experiences
- Evolution of understanding is trackable through git diff

## 📊 Current Research Status

### Active Investigations:
- **3-4:2 Modal Framework**: Cosmic structure formation theory (computational validation completed)

### Validation Status Clarification:
- **Computational Validation**: ✅ Completed (356-line test script, mathematical verification)
- **Mathematical Framework**: ✅ Verified (spherical harmonic orthogonality, energy conservation)
- **Peer Review**: ⏳ Pending (requires independent expert review)
- **Observational Testing**: ⏳ Pending (requires telescope data)

**Note**: "Computational validation" ≠ "Peer review ready" - precise language enforced.

## 📈 Knowledge Evolution

Track the evolution of understanding in `meta_instructions/knowledge_evolution.yaml`:
- Total validations: 1
- Domains explored: cosmology, wave_physics, mathematical_physics
- Success rate: 100%
- Key learnings: Contamination prevention, temporal memory systems, headless automation

## 🔍 Memory Consultation

Before starting new research, agents consult temporal memory:

```bash
# Check if we've investigated this before
git log --grep="$CURRENT_HYPOTHESIS" --oneline

# Review related past work
git log --grep="$DOMAIN" --since="6 months ago"

# Learn from past failures
git log --grep="FAILED" --pretty=format:"%h %s"

# Build on validated findings (with re-verification)
git log --grep="VALIDATED" --pretty=format:"%h %s"
```

## 📚 Learning from History

The `archived_attempts/learnings.log` contains valuable lessons:
- **2025-01-29**: Major contamination incident and recovery
- **Prevention protocols**: Implemented to avoid future incidents
- **Success patterns**: Repository restructure and temporal memory
- **Automation fixes**: Headless operation to prevent blocking

## 🎯 Expected Outcomes

Agents processing materials in this repository should:
- Apply rigorous scientific validation methods
- Build on past validated findings with temporal context
- Learn from archived failures to avoid repetition
- Document all work with confidence levels and limitations
- Use precise validation language (computational ≠ peer-reviewed)
- Contribute to the evolution of scientific understanding

## 🔄 Research Cycle

1. **Environment Setup**: Configure headless operation
2. **Memory Consultation**: Check git history for related work
3. **Workspace Verification**: Ensure clean folder structure
4. **Environmental Scanning**: Process input_hypotheses folder
5. **Hypothesis Formation**: Build on past validated findings
6. **Experimental Design**: Create reproducible experiments (headless)
7. **Validation**: Apply multiple scientific reasoning methods
8. **Memory Integration**: Update temporal record with findings

## 🚨 Emergency Protocols

If automation gets stuck:
```bash
killall -9 python3         # Emergency stop
export MPLBACKEND=Agg      # Reset backend
export DISPLAY=:99         # Virtual display
```

If files appear in root directory:
```bash
find . -maxdepth 1 -type f | grep -v -E "(README|LICENSE)" | xargs -I {} mv {} archived_attempts/
```

## 📞 Contact

This is an autonomous research system. Drop hypotheses in `input_hypotheses/` and agents will process them according to the complete scientific discovery protocol v2.0.

---

**Last Updated**: 2025-01-29  
**Repository Status**: ✅ Clean and Operational  
**Agent Protocol**: ✅ v2.0 Fully Implemented  
**Temporal Memory**: ✅ Active  
**Contamination Prevention**: ✅ Military-Grade  
**Headless Operation**: ✅ Configured  
**Folder Discipline**: ✅ Strictly Enforced
