import sys
sys.path.append('VALIDATION_TOOLS')
from scientific_reasoning_methods import ScientificReasoningMethods

with open('00-INTAKE/optimized_validation_research.txt', 'r') as f:
    content = f.read()

methods = ScientificReasoningMethods()
results = methods.validate_with_all_methods(content)

screening_methods = ['methodical_skepticism', 'occams_razor', 'dimensional_analysis', 'physics_consistency', 'literature_conflict_detection']
print('Optimized Research - Initial Screening Methods:')
screening_scores = []
for method in screening_methods:
    if method in results:
        score = results[method]
        screening_scores.append(score)
        print(f'{method:30s}: {score:.3f}')

if screening_scores:
    avg_screening = sum(screening_scores) / len(screening_scores)
    print(f'Screening Average: {avg_screening:.3f}')
    print(f'Pass/Fail: {"PASS" if avg_screening >= 0.8 else "FAIL"}') 