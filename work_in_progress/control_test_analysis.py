#!/usr/bin/env python3
"""
CONTROL TEST - Checking for Analysis Method Bias
================================================

Critical test: Does our 3-4:2 analysis method inherently produce 
false positives due to mathematical artifacts?

If we detect 3-4:2 signatures in EVERY random dataset, 
then our method is fundamentally flawed.
"""

import numpy as np
import matplotlib.pyplot as plt

def generate_pure_random_data():
    """Generate completely random galaxy positions - no structure at all"""
    
    n_galaxies = 50000
    
    # Completely random redshifts
    redshifts = np.random.uniform(0.1, 2.0, n_galaxies)
    
    # Completely random sky positions
    ra = np.random.uniform(0, 360, n_galaxies)
    dec = np.random.uniform(-30, 60, n_galaxies)
    
    # Convert to distances
    c = 299792.458
    H0 = 67.4
    distances = (c/H0) * redshifts
    
    print(f"🎲 Generated PURE RANDOM galaxy distribution")
    print(f"   No structure, no patterns, no signals injected")
    print(f"   Galaxies: {n_galaxies:,}")
    
    return {
        'ra': ra,
        'dec': dec,
        'redshift': redshifts,
        'distances': distances
    }

def test_analysis_method_on_random(data):
    """Test our 3-4:2 analysis on pure random data"""
    
    print(f"\n🔬 TESTING ANALYSIS METHOD ON PURE RANDOM DATA")
    print("=" * 55)
    print("❓ Question: Does our method find 3-4:2 signatures in random noise?")
    
    # Convert to Cartesian
    ra_rad = np.radians(data['ra'])
    dec_rad = np.radians(data['dec'])
    distances = data['distances']
    
    x = distances * np.cos(dec_rad) * np.cos(ra_rad)
    y = distances * np.cos(dec_rad) * np.sin(ra_rad)
    z = distances * np.sin(dec_rad)
    
    # Apply same analysis as before
    k1_range = np.logspace(-3, -1, 50)
    detections = []
    
    for k1 in k1_range:
        k2 = 2 * k1
        k3 = 3 * k1
        
        signal_1 = np.mean(np.cos(k1 * x) * np.cos(k1 * y) * np.cos(k1 * z))
        signal_2 = np.mean(np.cos(k2 * x) * np.cos(k2 * y) * np.cos(k2 * z))
        signal_3 = np.mean(np.cos(k3 * x) * np.cos(k3 * y) * np.cos(k3 * z))
        
        combined = abs(signal_1) + abs(signal_2) + abs(signal_3)
        
        if combined > 0.001:
            ratio_2_1 = k2/k1
            ratio_3_1 = k3/k1
            ratio_3_2 = k3/k2
            
            dev_2_1 = abs(ratio_2_1 - 2.0) / 2.0
            dev_3_1 = abs(ratio_3_1 - 3.0) / 3.0
            dev_3_2 = abs(ratio_3_2 - 1.5) / 1.5
            
            avg_deviation = (dev_2_1 + dev_3_1 + dev_3_2) / 3
            
            detections.append({
                'k1': k1,
                'combined_signal': combined,
                'deviation': avg_deviation
            })
    
    return detections

def multiple_random_trials(n_trials=5):
    """Run multiple trials on different random datasets"""
    
    print(f"\n🎯 RUNNING {n_trials} INDEPENDENT RANDOM TRIALS")
    print("=" * 50)
    
    trial_results = []
    
    for trial in range(n_trials):
        print(f"\n📊 Trial {trial+1}/{n_trials}: Pure random data")
        
        # Generate new random dataset
        random_data = generate_pure_random_data()
        
        # Test our analysis method
        detections = test_analysis_method_on_random(random_data)
        
        # Count "significant" detections
        tolerance = 0.1
        good_matches = [d for d in detections if d['deviation'] < tolerance]
        
        trial_results.append({
            'trial': trial + 1,
            'total_detections': len(detections),
            'good_matches': len(good_matches),
            'best_deviation': min(d['deviation'] for d in detections) if detections else 1.0
        })
        
        print(f"   Total detections: {len(detections)}")
        print(f"   'Good' matches: {len(good_matches)}")
        if detections:
            print(f"   Best deviation: {min(d['deviation'] for d in detections)*100:.1f}%")
    
    return trial_results

def interpret_control_results(results):
    """Interpret what the control test reveals"""
    
    print(f"\n🔬 CONTROL TEST ANALYSIS")
    print("=" * 40)
    
    total_good_matches = sum(r['good_matches'] for r in results)
    total_trials = len(results)
    
    print(f"Summary across {total_trials} random trials:")
    for r in results:
        print(f"  Trial {r['trial']}: {r['good_matches']} 'detections', best dev: {r['best_deviation']*100:.1f}%")
    
    avg_false_positives = total_good_matches / total_trials
    
    print(f"\n⚖️  VERDICT:")
    
    if avg_false_positives > 10:
        print("❌ MAJOR PROBLEM: Analysis method is severely biased!")
        print(f"   Average false positives per trial: {avg_false_positives:.1f}")
        print("   Our method finds 3-4:2 signatures even in pure random noise")
        print("   ALL previous results are likely artifacts")
        print("   Framework validation is INVALID")
        
    elif avg_false_positives > 2:
        print("⚠️  MODERATE BIAS: Analysis method has some false positive rate")
        print(f"   Average false positives per trial: {avg_false_positives:.1f}")
        print("   Need to adjust thresholds and significance criteria")
        print("   Previous results need reinterpretation")
        
    elif avg_false_positives < 0.5:
        print("✅ GOOD: Low false positive rate")
        print(f"   Average false positives per trial: {avg_false_positives:.1f}")
        print("   Analysis method appears robust")
        print("   Previous detections may be genuine")
        
    else:
        print("🤔 UNCLEAR: Borderline false positive rate")
        print(f"   Average false positives per trial: {avg_false_positives:.1f}")
        print("   Need more sophisticated statistical analysis")

def main():
    """Main control test"""
    
    print("""
🧪 CONTROL TEST FOR 3-4:2 ANALYSIS METHOD
==========================================

CRITICAL QUESTION: Are we detecting real 3-4:2 signatures, 
or are they mathematical artifacts of our analysis method?

Testing approach: Run our analysis on pure random data.
- If we still find 3-4:2 signatures → Method is biased (FALSE POSITIVES)
- If we find no signatures → Method may be valid

This will determine if our previous results mean anything.
""")
    
    # Run multiple control trials
    results = multiple_random_trials(5)
    
    # Interpret what this means for our framework
    interpret_control_results(results)
    
    print(f"\n🎓 SCIENTIFIC IMPLICATION:")
    print("If this control test shows high false positives,")
    print("then BOTH the mock data AND realistic data results are meaningless.")
    print("The analysis method itself would be fundamentally flawed.")

if __name__ == "__main__":
    main() 