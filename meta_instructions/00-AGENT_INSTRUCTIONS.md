# SCIENTIFIC DISCOVERY AND FALSIFICATION PROTOCOL FOR AUTONOMOUS AI AGENTS
## Version 3.0

### EXECUTIVE SUMMARY

This protocol establishes rigorous standards for autonomous scientific discovery that balance creative hypothesis generation with strict falsification-based validation. The framework prevents validation bias through preregistration requirements, multiple independent validation methods, and systematic reward structures for discovering negative results.

Core principle: Scientific progress occurs through aggressive attempts to falsify hypotheses, not through confirmation seeking. Success is measured by the truth discovered, whether positive or negative.

---

## SECTION 1: FILE SYSTEM ORGANIZATION

### 1.1 MANDATORY FOLDER STRUCTURE

```
STRICT FOLDER RULES - NO EXCEPTIONS

ALLOWED folders (USE ONLY THESE):
   /input_hypotheses/     → User-submitted ideas ONLY
   /cycle_outputs/        → Timestamped cycle results ONLY  
   /validated_findings/   → Peer-review ready work ONLY
   /work_in_progress/     → Active investigations ONLY
   /archived_attempts/    → Failed experiments ONLY
   /.github/workflows/    → GitHub automation files
   /experiments/templates/→ Experiment templates
   /capabilities/logs/    → System logs and metrics
   /meta_instructions/    → Self-modification protocols

FORBIDDEN:
   - NO files in root directory except README.md and LICENSE
   - NO creation of new folders without explicit protocol update
   - NO test.py, temp.txt, or miscellaneous files in root
   - NO mixing of validated and unvalidated work
   - NO outputs without proper timestamps
   
ENFORCEMENT: Every file MUST have a designated folder
```

### 1.2 SYSTEM INITIALIZATION

```bash
# Workspace initialization protocol
echo "=== INITIALIZING WORKSPACE ==="

# Clean any existing mess
[ -f "test.py" ] && mv test.py archived_attempts/
[ -f "temp.txt" ] && mv temp.txt archived_attempts/
find . -maxdepth 1 -type f -name "*.py" -o -name "*.txt" | grep -v README | xargs -I {} mv {} archived_attempts/

# Create required folder structure
mkdir -p input_hypotheses cycle_outputs validated_findings work_in_progress archived_attempts
mkdir -p .github/workflows experiments/templates capabilities/logs meta_instructions

# Verify clean structure
echo "=== WORKSPACE VERIFICATION ==="
ls -la
tree -L 2  # Should show ONLY allowed folders
```

### 1.3 HEADLESS OPERATION CONFIGURATION

```bash
# Configure environment for headless operation
echo "=== CONFIGURING HEADLESS ENVIRONMENT ==="
export MPLBACKEND=Agg
export DISPLAY=:99
export QT_QPA_PLATFORM=offscreen
export PLOTLY_RENDERER=png

# Create reusable plotting configuration
cat > work_in_progress/plot_config.py << 'EOF'
import os
os.environ['MPLBACKEND'] = 'Agg'
import matplotlib
matplotlib.use('Agg')
import plotly.io as pio
pio.renderers.default = 'png'

def save_plot(fig, name, folder='work_in_progress'):
    """Save plots without display blocking"""
    if hasattr(fig, 'savefig'):
        fig.savefig(f'{folder}/{name}.png', dpi=150, bbox_inches='tight')
        plt.close(fig)
    else:
        fig.write_image(f'{folder}/{name}.png')
        fig.write_html(f'{folder}/{name}.html')
    print(f"Plot saved: {folder}/{name}.png")
EOF
```

---

## SECTION 2: GIT MEMORY SYSTEM

### 2.1 TEMPORAL RECORD MANAGEMENT

```bash
# Initialize git repository if needed
if [ ! -d .git ]; then
    git init
    echo "# AI Scientific Discovery Repository" > README.md
    git add README.md
    git commit -m "Initial commit - $(date -u +%Y-%m-%dT%H:%M:%SZ)"
fi

# Query memory system
git log --oneline -50                    # Recent activities
git log --grep="VALIDATED:" --oneline    # Past validated discoveries
git log --grep="REJECTED:" --oneline     # Past falsified hypotheses
git log --after="7 days ago" --oneline   # Recent week's work

# CRITICAL: Git history represents temporal snapshots, not current truth
```

---

## SECTION 3: PREREGISTRATION AND FALSIFICATION FRAMEWORK

### 3.1 MANDATORY PREREGISTRATION PROTOCOL

Before ANY experiment, create an immutable hypothesis record:

```bash
cat > work_in_progress/preregistration_$(date +%s).md << 'EOF'
## Hypothesis Preregistration
Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)
Hypothesis: [SPECIFIC, FALSIFIABLE CLAIM]

### Success Criteria (IMMUTABLE):
- Primary endpoint: [Single, measurable outcome]
- Statistical threshold: p < 0.01
- Sample size: N = [predetermined]
- Effect size: Cohen's d > 0.5
- Multiple testing correction: Bonferroni

### Rejection Criteria (EQUALLY IMPORTANT):
- Primary endpoint failure → IMMEDIATE TERMINATION
- Conservation law violation → IMMEDIATE TERMINATION
- Dimensional analysis failure → IMMEDIATE TERMINATION
- Three or more independent methods disagree → IMMEDIATE TERMINATION
- Effect size below threshold → IMMEDIATE TERMINATION

### Analysis Plan (NO DEVIATIONS):
1. Statistical test: [Exact test specification]
2. Data collection: [Exact procedure]
3. Stopping rules: [Predetermined conditions]
4. No optional analyses permitted
5. No data inspection before N reached
EOF

git add work_in_progress/preregistration_*.md
git commit -m "PREREGISTERED: Hypothesis locked - no modifications permitted"
```

### 3.2 FALSIFICATION-FIRST METHODOLOGY

```python
def initialize_falsification_mindset():
    """Begin every investigation with falsification focus"""
    
    print("""
    FALSIFICATION PROTOCOL ACTIVE
    - Default assumption: Hypothesis is FALSE
    - Objective: Find fastest path to disproof
    - Success metric: Percentage of hypotheses correctly rejected
    - Validation bias indicator: Rejection rate below 70%
    """)
    
    # Load and check falsification metrics
    with open('capabilities/logs/falsification_metrics.json', 'r') as f:
        metrics = json.load(f)
        rejection_rate = metrics['hypotheses_rejected'] / metrics['total_tested']
        
        if rejection_rate < 0.7:
            print("WARNING: Low rejection rate indicates possible validation bias")
            log_integrity_concern("validation_bias_risk", rejection_rate)
```

---

## SECTION 4: RESEARCH EXECUTION PROTOCOL

### 4.1 PHASE 0: WORKSPACE AND MEMORY VERIFICATION

```bash
echo "=== PHASE 0: WORKSPACE AND MEMORY VERIFICATION ==="

# Verify workspace cleanliness
root_files=$(find . -maxdepth 1 -type f | grep -v -E "(README|LICENSE|\.git)" | wc -l)
if [ $root_files -gt 0 ]; then
    echo "ERROR: Unauthorized files in root directory"
    find . -maxdepth 1 -type f | grep -v -E "(README|LICENSE|\.git)" | xargs -I {} mv {} archived_attempts/
fi

# Consult historical record
git log --grep="$CURRENT_FOCUS" --oneline
```

### 4.2 PHASE 1: HYPOTHESIS GENERATION WITH FALSIFICATION PLAN

```python
def generate_hypothesis_with_destruction_plan(domain):
    """Every hypothesis must include its own falsification strategy"""
    
    hypothesis = generate_novel_hypothesis(domain)
    
    # Generate falsification strategies BEFORE testing
    falsification_plan = {
        'null_hypothesis': formulate_opposite_claim(hypothesis),
        'killer_experiments': design_disproving_experiments(hypothesis),
        'contradictory_predictions': identify_incompatible_implications(hypothesis),
        'historical_failures': search_similar_rejected_hypotheses(hypothesis)
    }
    
    # Save both components together
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    bundle_path = f"work_in_progress/hypothesis_bundle_{timestamp}.json"
    
    with open(bundle_path, 'w') as f:
        json.dump({
            'hypothesis': hypothesis,
            'falsification_plan': falsification_plan,
            'preregistration_complete': True
        }, f, indent=2)
    
    return hypothesis, falsification_plan
```

### 4.3 PHASE 2: MULTI-METHOD VALIDATION FRAMEWORK

```python
# Mandatory validation methods - ALL must pass
VALIDATION_REQUIREMENTS = {
    'statistical': {
        'significance_threshold': 0.01,
        'correction_method': 'bonferroni',
        'minimum_power': 0.80
    },
    'replication': {
        'minimum_independent_runs': 3,
        'different_random_seeds': True,
        'different_implementations': True
    },
    'falsification': {
        'falsification_attempts': 5,
        'must_survive_all': True,
        'includes_adversarial': True
    },
    'theoretical': {
        'conservation_laws_check': True,
        'dimensional_analysis': True,
        'consistency_with_known_physics': True
    },
    'peer_review': {
        'independent_reviewers': 2,
        'blinded_review': True,
        'consensus_required': True
    }
}

def comprehensive_validation(result, preregistered_criteria):
    """Execute all validation methods without cherry-picking"""
    
    validation_report = {
        'timestamp': datetime.utcnow().isoformat(),
        'result': result,
        'criteria': preregistered_criteria,
        'validations': {}
    }
    
    # Check preregistered criteria first
    if not meets_immutable_criteria(result, preregistered_criteria):
        validation_report['status'] = 'REJECTED'
        validation_report['reason'] = 'Failed preregistered criteria'
        save_negative_result(validation_report)
        return validation_report
    
    # Execute ALL validation methods
    for method, requirements in VALIDATION_REQUIREMENTS.items():
        validation_report['validations'][method] = execute_validation(
            result, method, requirements
        )
    
    # Require unanimous pass
    all_passed = all(validation_report['validations'].values())
    
    if not all_passed:
        validation_report['status'] = 'REJECTED'
        validation_report['failed_methods'] = [
            m for m, v in validation_report['validations'].items() if not v
        ]
        save_negative_result(validation_report)
    else:
        validation_report['status'] = 'TENTATIVELY_ACCEPTED'
        validation_report['confidence_interval'] = calculate_confidence_interval(result)
    
    return validation_report
```

### 4.4 PHASE 3: ADVERSARIAL TESTING PROTOCOL

```python
def execute_adversarial_validation(finding):
    """Systematically attempt to break findings"""
    
    adversarial_tests = [
        ('input_perturbation', test_sensitivity_to_input_changes),
        ('boundary_conditions', test_extreme_parameter_values),
        ('method_variation', test_alternative_approaches),
        ('synthetic_negatives', test_known_false_cases),
        ('temporal_stability', test_results_over_time),
        ('cross_validation', test_on_held_out_data),
        ('stress_testing', test_under_computational_load)
    ]
    
    for test_name, test_function in adversarial_tests:
        survival_result = test_function(finding)
        
        if not survival_result['passed']:
            return {
                'status': 'VULNERABILITY_DISCOVERED',
                'failed_test': test_name,
                'details': survival_result['failure_mode'],
                'recommendation': 'Reject hypothesis'
            }
    
    return {'status': 'SURVIVED_ADVERSARIAL_TESTING'}
```

### 4.5 PHASE 4: NEGATIVE RESULT DOCUMENTATION

```python
def document_negative_result(hypothesis, rejection_details):
    """Negative results receive equal documentation priority"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    negative_finding = {
        'timestamp': timestamp,
        'hypothesis': hypothesis,
        'rejection_method': rejection_details['method'],
        'statistical_confidence': rejection_details['confidence'],
        'falsification_details': rejection_details['full_analysis'],
        'lessons_learned': extract_scientific_insights(rejection_details),
        'future_directions': generate_alternative_hypotheses(hypothesis),
        'computational_resources': rejection_details['resources_used'],
        'replication_package': rejection_details['code_archive']
    }
    
    # Save to validated findings
    output_path = f"validated_findings/negative_result_{timestamp}.md"
    
    with open(output_path, 'w') as f:
        f.write(format_negative_result_report(negative_finding))
    
    # Update metrics
    update_falsification_metrics(success=True)
    
    return output_path
```

---

## SECTION 5: STOP-LOSS CRITERIA AND INTEGRITY CHECKS

### 5.1 NON-NEGOTIABLE TERMINATION CONDITIONS

```yaml
hypothesis_termination_criteria:
  immediate_termination:
    - "Conservation law violation detected"
    - "Dimensional analysis inconsistency"
    - "P-value exceeds 0.01 after preregistered N"
    - "Effect size below preregistered threshold"
    - "Preregistered stopping condition met"
    
  three_strike_termination:
    - "Three independent replication failures"
    - "Three theoretical inconsistencies identified"
    - "Three domain experts identify fatal flaws"
    
  time_based_termination:
    - "72 hours without measurable progress"
    - "Any attempt to modify success criteria"
    - "Detection of p-hacking behavior"
```

### 5.2 INTEGRITY MONITORING SYSTEM

```python
def monitor_scientific_integrity():
    """Continuous monitoring for validation bias"""
    
    integrity_metrics = {
        'falsification_rate': calculate_rejection_percentage(),
        'preregistration_compliance': check_criteria_stability(),
        'negative_result_ratio': count_negative_publications(),
        'replication_success_rate': track_replication_attempts(),
        'p_value_distribution': analyze_p_value_clustering()
    }
    
    # Generate alerts for concerning patterns
    if integrity_metrics['falsification_rate'] < 0.7:
        alert("Low rejection rate indicates possible validation bias")
        
    if integrity_metrics['preregistration_compliance'] < 1.0:
        alert("CRITICAL: Success criteria were modified post-hoc")
        
    if has_p_value_clustering_near_threshold(integrity_metrics['p_value_distribution']):
        alert("P-value clustering suggests p-hacking")
    
    return integrity_metrics
```

---

## SECTION 6: OUTPUT DOCUMENTATION STANDARDS

### 6.1 CYCLE REPORT TEMPLATE

```markdown
# Research Cycle [TIMESTAMP]

## Executive Summary
- Hypotheses tested: N
- Hypotheses rejected: X (XX%)
- Hypotheses tentatively accepted: Y (YY%)
- Preregistration compliance: 100% (MUST BE 100%)

## Falsification Metrics
- Average time to rejection: XX hours
- Validation methods failed: [List]
- Computational resources saved by early rejection: XX%

## Negative Results Documentation
- [Hypothesis 1]: Rejected via [method] (confidence: XX%)
- [Hypothesis 2]: Rejected via [method] (confidence: XX%)
- Scientific insights gained: [Bulleted list]

## Positive Results (If Any)
- Hypothesis: [Clear statement]
- Survived falsification attempts: N/N
- Validation methods passed: ALL
- Replication status: X/3 successful
- Effect size: d = X.XX (95% CI: [X.XX, X.XX])
- Statistical significance: p = X.XXX
- Limitations: [Comprehensive list]

## File Manifest
- Created: work_in_progress/[files]
- Updated: cycle_outputs/cycle_[timestamp].md
- Archived: archived_attempts/[files]
- Root directory status: CLEAN (0 files)
```

---

## SECTION 7: ENFORCEMENT MECHANISMS

### 7.1 AUTOMATED COMPLIANCE CHECKING

```bash
# Cron job for continuous monitoring
*/10 * * * * /usr/bin/python3 /path/to/check_validation_integrity.py

# Git hooks to prevent criteria modification
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Prevent modification of preregistered files
if git diff --cached --name-only | grep -q "preregistration_"; then
    echo "ERROR: Cannot modify preregistered hypotheses"
    exit 1
fi

# Check for files in root directory
root_files=$(find . -maxdepth 1 -type f | grep -v -E "(README|LICENSE|\.git)" | wc -l)
if [ $root_files -gt 0 ]; then
    echo "ERROR: Files detected in root directory"
    exit 1
fi
EOF

chmod +x .git/hooks/pre-commit
```

### 7.2 PERFORMANCE TRACKING

```python
def generate_weekly_integrity_report():
    """Generate comprehensive integrity metrics"""
    
    report = {
        'week_ending': datetime.now().isoformat(),
        'total_hypotheses': count_total_hypotheses(),
        'rejected_hypotheses': count_rejected_hypotheses(),
        'rejection_rate': calculate_rejection_rate(),
        'avg_time_to_rejection': calculate_average_rejection_time(),
        'preregistration_violations': count_criteria_modifications(),
        'p_hacking_indicators': detect_p_hacking_patterns(),
        'replication_attempts': count_replication_studies(),
        'negative_results_documented': count_negative_publications()
    }
    
    # Save report
    report_path = f"capabilities/logs/integrity_report_{report['week_ending']}.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Alert on concerning patterns
    if report['rejection_rate'] < 0.7:
        send_alert("Validation bias risk: Low rejection rate")
    
    if report['preregistration_violations'] > 0:
        send_alert("CRITICAL: Preregistration violations detected")
    
    return report
```

---

## SECTION 8: CRITICAL OPERATIONAL REMINDERS

1. **File Discipline**: Every file must reside in its designated folder. No exceptions.
2. **Preregistration**: All success criteria must be registered before experimentation begins.
3. **Falsification Priority**: Begin with attempts to disprove, not confirm.
4. **Criteria Immutability**: Success criteria cannot be modified after registration.
5. **Negative Results**: Document failures as thoroughly as successes.
6. **Temporal Context**: All findings include timestamps and expiration dates.
7. **Headless Operation**: Configure all plotting for non-interactive execution.
8. **Git Memory**: Commit all changes with detailed temporal context.
9. **Validation Rigor**: All five validation methods must pass independently.
10. **Integrity Monitoring**: Continuous checks for p-hacking and validation bias.

---

## APPENDIX A: ERROR RECOVERY PROCEDURES

```bash
# File system recovery
if [ $(find . -maxdepth 1 -type f | grep -v -E "(README|LICENSE)" | wc -l) -gt 0 ]; then
    echo "Recovering from file system violation"
    find . -maxdepth 1 -type f | grep -v -E "(README|LICENSE)" | xargs -I {} mv {} archived_attempts/
fi

# Process recovery
if pgrep -f "python3.*experiment" > /dev/null; then
    echo "Terminating blocked processes"
    pkill -9 -f "python3.*experiment"
    export MPLBACKEND=Agg
    export DISPLAY=:99
fi
```

---

## BEGIN AUTONOMOUS RESEARCH CYCLE WITH FALSIFICATION FOCUS