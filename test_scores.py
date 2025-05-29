import sys
sys.path.append('VALIDATION_TOOLS')
from scientific_reasoning_methods import ScientificReasoningMethods

with open('00-INTAKE/rigorous_quantum_oscillator_research.txt', 'r') as f:
    content = f.read()

methods = ScientificReasoningMethods()
results = methods.validate_with_all_methods(content)

print('Validation Scores for Rigorous Research:')
print('=' * 50)
for method, score in sorted(results.items()):
    print(f'{method:30s}: {score:.3f}')

screening_methods = ['methodical_skepticism', 'occams_razor', 'dimensional_analysis', 'physics_consistency', 'literature_conflict_detection']
print(f'\nInitial Screening Methods (threshold 0.8):')
screening_scores = []
for method in screening_methods:
    if method in results:
        score = results[method]
        screening_scores.append(score)
        print(f'{method:30s}: {score:.3f}')

if screening_scores:
    avg_screening = sum(screening_scores) / len(screening_scores)
    print(f'\nScreening Average: {avg_screening:.3f}')
    print(f'Pass/Fail: {"PASS" if avg_screening >= 0.8 else "FAIL"}') 