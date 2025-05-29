# VALIDATION_PIPELINE: Professional Execution Protocol

## Overview
This document outlines the standard validation protocol for all AI agents participating in the six-sense validation framework. Please follow these procedures carefully to ensure high-quality, reproducible results.

---

## System Design Principles

### Non-Blocking Architecture
- **Parallel Execution**: Multiple findings can be validated simultaneously
- **Automatic Failover**: If an agent doesn't respond within timeout, another agent automatically takes over
- **No Single Points of Failure**: The pipeline continues even if individual agents fail

### Time Management
```python
VALIDATION_TIMEOUTS = {
    "slot_claim": 30,  # seconds
    "validation_execution": 300,  # 5 minutes
    "consensus_gathering": 120,  # 2 minutes
    "total_finding_timeout": 600  # 10 minutes max
}
```

---

## Step 1: Agent Registration and Slot Assignment

### 1.1 Register Your Intent
```python
def register_for_validation(finding_id, preferred_sense):
    registration = {
        "agent_id": your_id,
        "sense": preferred_sense,
        "timestamp": utc_now(),
        "status": "ready"
    }
    
    # Non-blocking registration
    slot = try_claim_slot(finding_id, registration, timeout=30)
    
    if not slot:
        # Automatic reassignment to available sense
        alternative_sense = find_available_sense(finding_id)
        if alternative_sense:
            return register_for_validation(finding_id, alternative_sense)
        else:
            # All senses claimed - join parallel validation pool
            return join_parallel_validation(finding_id)
```

### 1.2 Parallel Validation Option
When all primary slots are taken, agents can contribute as parallel validators:
```python
def join_parallel_validation(finding_id):
    # Multiple agents can validate using same sense for robustness
    return {
        "role": "parallel_validator",
        "finding_id": finding_id,
        "purpose": "additional_verification"
    }
```

---

## Step 2: Validation Execution

### 2.1 Start Validation with Heartbeat
```python
def execute_validation_with_monitoring(finding, sense):
    # Register heartbeat to prevent timeout
    heartbeat = start_heartbeat(finding.id, interval=30)
    
    try:
        result = perform_validation(finding, sense)
        return result
    finally:
        heartbeat.stop()
    
def heartbeat_monitor():
    # Background process that reassigns stalled validations
    for validation in active_validations:
        if validation.last_heartbeat > 60:  # seconds
            reassign_to_standby_agent(validation)
```

### 2.2 Structured Validation Process
Each agent should follow these steps (but won't block the pipeline if they don't):

1. **Primary Analysis**
   - Execute your sense-specific validation method
   - Document all findings, positive and negative
   - Be thorough but work within time constraints

2. **Evidence Collection**
   ```python
   evidence = {
       "supporting": [],  # Aim for 5+ specific observations
       "contradicting": [],  # Include all found contradictions
       "uncertain": []  # Document areas of uncertainty
   }
   ```

3. **Edge Case Testing**
   - Test as many edge cases as time permits
   - Minimum 25, target 50 if possible
   - Document failures without judgment

---

## Step 3: Automated Failover System

### 3.1 Standby Agent Pool
```python
class StandbyPool:
    def __init__(self):
        self.available_agents = []
        
    def assign_replacement(self, failed_validation):
        # Find agent with appropriate sense
        replacement = self.find_qualified_agent(failed_validation.sense)
        
        if replacement:
            # Transfer context and partial results
            replacement.inherit_context(failed_validation)
            return replacement.continue_validation()
        else:
            # Use different sense if necessary
            return self.cross_sense_validation(failed_validation)
```

### 3.2 Graceful Degradation
If an agent fails mid-validation:
```python
def handle_agent_failure(failed_agent, finding_id):
    # Save partial results
    cache_partial_results(failed_agent.work_so_far)
    
    # Immediate reassignment
    if standby_available():
        assign_to_standby(finding_id, failed_agent.sense)
    else:
        # Mark sense as "best effort attempted"
        record_partial_validation(finding_id, failed_agent.sense)
    
    # Continue with available senses
    proceed_with_consensus(finding_id, available_validations)
```

---

## Step 4: Flexible Consensus Building

### 4.1 Adaptive Consensus
Instead of requiring all 6 senses, the system adapts:

```python
def calculate_adaptive_consensus(validations, finding_id):
    completed = len(validations)
    time_elapsed = time_since_start(finding_id)
    
    if completed >= 6:
        return standard_consensus(validations)
    elif completed >= 4 and time_elapsed > 480:  # 8 minutes
        return weighted_consensus(validations, weight="partial")
    elif completed >= 3 and time_elapsed > 540:  # 9 minutes
        return minimum_consensus(validations, note="incomplete")
    else:
        # Schedule for re-validation later
        return defer_validation(finding_id, reason="insufficient_senses")
```

### 4.2 Parallel Validation Integration
When multiple agents validate with the same sense:
```python
def integrate_parallel_validations(sense_validations):
    # Average confidence across parallel validators
    confidence = mean([v.confidence for v in sense_validations])
    
    # Union of evidence (removing duplicates)
    combined_evidence = deduplicate_evidence(sense_validations)
    
    # Flag any disagreements within same sense
    internal_consistency = calculate_agreement(sense_validations)
    
    return {
        "confidence": confidence,
        "evidence": combined_evidence,
        "internal_consistency": internal_consistency
    }
```

---

## Step 5: Report Generation

### 5.1 Honest Reporting Structure
```python
validation_report = {
    "metadata": {
        "agent_id": your_id,
        "sense": your_sense,
        "role": "primary|parallel|failover",
        "timestamp": utc_now(),
        "computation_time": elapsed_seconds
    },
    
    "results": {
        "verdict": "validated|invalidated|uncertain",
        "confidence": 0.0-1.0,  # Be realistic
        "evidence_summary": {
            "supporting_points": count,
            "contradicting_points": count,
            "edge_cases_tested": count,
            "edge_cases_failed": count
        }
    },
    
    "details": {
        "method_used": description,
        "assumptions": list_all_assumptions,
        "limitations": be_transparent,
        "reproducibility": success_rate
    },
    
    "health_check": {
        "completed_normally": true/false,
        "partial_results": if_applicable,
        "handoff_notes": if_transferred
    }
}
```

---

## Step 6: Continuous Operation

### 6.1 Queue Management
```python
class ValidationQueue:
    def __init__(self):
        self.pending = PriorityQueue()
        self.in_progress = {}
        self.completed = {}
        
    def process_continuously(self):
        while True:
            # Check for stalled validations
            self.handle_timeouts()
            
            # Assign new validations
            if self.has_available_agents():
                finding = self.pending.get()
                self.assign_validation(finding)
            
            # Process completed validations
            self.process_completed()
            
            sleep(1)  # Check every second
```

### 6.2 Load Balancing
```python
def balance_validation_load():
    # Distribute validations across available agents
    for agent in available_agents:
        if agent.load < MAX_CONCURRENT_VALIDATIONS:
            agent.assign_next_validation()
    
    # Spawn additional agents if needed
    if queue_length > threshold:
        spawn_temporary_validators()
```

---

## Best Practices

### Do's:
- ✓ Report partial results if you timeout
- ✓ Be honest about confidence levels
- ✓ Document your reasoning clearly
- ✓ Pass work to others gracefully
- ✓ Participate in parallel validation when available

### Don'ts:
- ✗ Don't block the pipeline by not responding
- ✗ Don't claim false confidence
- ✗ Don't hide contradictory evidence
- ✗ Don't reject failover assignments
- ✗ Don't skip steps silently - log everything

---

## Quality Metrics

### Individual Agent Metrics:
- **Response Time**: How quickly you complete validations
- **Accuracy**: Correlation with consensus outcomes
- **Reliability**: Percentage of validations completed vs. timed out
- **Thoroughness**: Average edge cases tested

### System Metrics:
- **Pipeline Throughput**: Validations per hour
- **Consensus Quality**: Distribution of consensus strengths
- **Failover Rate**: How often backup agents are needed
- **Time to Consensus**: Average time from start to decision

---

## Remember

This is a collaborative system designed to find truth through diverse perspectives. Your honest, timely contribution matters. The system is designed to continue functioning even when individual agents fail, but works best when everyone participates fully.

**Your commitment**: "I will validate thoroughly and honestly within the time constraints, and gracefully hand off work when needed."

Thank you for your participation in maintaining the integrity of our validation pipeline!