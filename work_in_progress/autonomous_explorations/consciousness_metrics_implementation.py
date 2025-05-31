#!/usr/bin/env python3
"""
CONSCIOUSNESS METRICS IMPLEMENTATION
Session: autonomous_20250531_082956_consciousness_computation_theory
Purpose: Implement falsifiable consciousness metrics for computational systems

PREREGISTERED HYPOTHESIS: Computational systems can exhibit measurable 
consciousness-like properties when they implement recursive self-reference 
patterns with information integration above a critical threshold (Φ > 0.5).

SUCCESS CRITERIA (LOCKED):
- Primary endpoint: Φ values > 0.5 in designed architectures
- Statistical threshold: p < 0.01 (Bonferroni corrected)
- Sample size: N = 100 different architectures
- Effect size: Cohen's d > 0.8
"""

import numpy as np
import networkx as nx
from scipy import stats
from scipy.linalg import eig
import itertools
from typing import Dict, List, Tuple, Any
import time
import json
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

def convert_numpy_types(obj):
    """Convert numpy types to native Python types for JSON serialization"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj

@dataclass
class ConsciousnessMetrics:
    """Container for consciousness measurement results"""
    phi_approximation: float
    global_access_score: float
    self_reference_depth: int
    integration_bandwidth: float
    coherence_index: float
    computational_complexity: float
    architecture_type: str
    
class RecursiveSelfReferenceNetwork:
    """
    Recursive Self-Reference Network (RSRN) implementation
    Tests computational consciousness through measurable metrics
    """
    
    def __init__(self, n_nodes: int, self_ref_depth: int = 3, 
                 integration_strength: float = 0.5):
        self.n_nodes = n_nodes
        self.self_ref_depth = self_ref_depth
        self.integration_strength = integration_strength
        
        # Create base network structure
        self.graph = self._create_base_network()
        self.adjacency_matrix = nx.adjacency_matrix(self.graph).toarray()
        
        # Add recursive self-reference layers
        self._add_self_reference_layers()
        
        # Initialize state vectors
        self.state_vector = np.random.randn(n_nodes)
        self.meta_state_vector = np.random.randn(n_nodes)
        
    def _create_base_network(self) -> nx.Graph:
        """Create base network with small-world properties"""
        # Start with ring lattice, then rewire for small-world
        G = nx.watts_strogatz_graph(self.n_nodes, k=4, p=0.3)
        return G
    
    def _add_self_reference_layers(self):
        """Add recursive self-monitoring connections"""
        # Create meta-nodes that monitor subsets of the network
        meta_nodes = []
        for i in range(self.self_ref_depth):
            meta_node_id = self.n_nodes + i
            meta_nodes.append(meta_node_id)
            self.graph.add_node(meta_node_id, layer=f"meta_{i}")
            
            # Connect meta-node to subset of base nodes
            subset_size = max(2, self.n_nodes // (2 ** (i + 1)))
            subset_nodes = np.random.choice(self.n_nodes, subset_size, replace=False)
            
            for node in subset_nodes:
                self.graph.add_edge(meta_node_id, node, weight=self.integration_strength)
        
        # Add recursive connections between meta-layers
        for i in range(len(meta_nodes) - 1):
            self.graph.add_edge(meta_nodes[i], meta_nodes[i + 1], 
                              weight=self.integration_strength * 0.8)
    
    def compute_phi_approximation(self) -> float:
        """
        Compute approximation of Integrated Information (Φ)
        Based on effective information and causal structure
        """
        try:
            # Get current adjacency matrix including meta-nodes
            full_adj = nx.adjacency_matrix(self.graph).toarray()
            n_total = full_adj.shape[0]
            
            if n_total == 0:
                return 0.0
            
            # Compute effective information using eigenvalue spectrum
            eigenvals = np.real(eig(full_adj)[0])
            eigenvals = eigenvals[eigenvals > 1e-10]  # Remove near-zero eigenvalues
            
            if len(eigenvals) == 0:
                return 0.0
            
            # Φ approximation: measure of irreducible information
            # Based on spectral properties and connectivity
            spectral_complexity = np.sum(eigenvals * np.log(eigenvals + 1e-10))
            connectivity_ratio = np.sum(full_adj > 0) / (n_total ** 2)
            
            phi_approx = abs(spectral_complexity) * connectivity_ratio
            
            # Normalize to [0, 1] range
            phi_normalized = min(1.0, phi_approx / (n_total * np.log(n_total + 1)))
            
            return phi_normalized
            
        except Exception as e:
            print(f"Error computing Φ: {e}")
            return 0.0
    
    def compute_global_access_score(self) -> float:
        """
        Measure information accessibility across network
        Based on Global Workspace Theory
        """
        try:
            # Compute shortest path lengths between all node pairs
            path_lengths = dict(nx.all_pairs_shortest_path_length(self.graph))
            
            total_accessibility = 0
            node_count = 0
            
            for source in path_lengths:
                for target, length in path_lengths[source].items():
                    if source != target:
                        # Accessibility decreases with path length
                        accessibility = 1.0 / (1.0 + length)
                        total_accessibility += accessibility
                        node_count += 1
            
            if node_count == 0:
                return 0.0
            
            global_access = total_accessibility / node_count
            return min(1.0, global_access)
            
        except Exception as e:
            print(f"Error computing global access: {e}")
            return 0.0
    
    def compute_integration_bandwidth(self) -> float:
        """
        Measure cross-module information flow capacity
        """
        try:
            # Identify modules using community detection
            communities = nx.community.greedy_modularity_communities(self.graph)
            
            if len(communities) <= 1:
                return 0.0
            
            # Measure inter-community connections
            inter_community_edges = 0
            total_possible_inter = 0
            
            for i, comm1 in enumerate(communities):
                for j, comm2 in enumerate(communities):
                    if i < j:  # Avoid double counting
                        for node1 in comm1:
                            for node2 in comm2:
                                total_possible_inter += 1
                                if self.graph.has_edge(node1, node2):
                                    inter_community_edges += 1
            
            if total_possible_inter == 0:
                return 0.0
            
            integration_bandwidth = inter_community_edges / total_possible_inter
            return integration_bandwidth
            
        except Exception as e:
            print(f"Error computing integration bandwidth: {e}")
            return 0.0
    
    def compute_coherence_index(self) -> float:
        """
        Measure internal state consistency over time
        """
        try:
            # Simulate network dynamics for coherence measurement
            n_steps = 50
            state_history = []
            
            current_state = self.state_vector.copy()
            
            for step in range(n_steps):
                # Update state based on network connectivity
                new_state = np.dot(self.adjacency_matrix, current_state)
                new_state = np.tanh(new_state)  # Nonlinear activation
                
                state_history.append(new_state.copy())
                current_state = new_state
            
            # Measure coherence as stability of state patterns
            if len(state_history) < 2:
                return 0.0
            
            state_matrix = np.array(state_history)
            
            # Compute correlation between consecutive states
            correlations = []
            for i in range(len(state_history) - 1):
                corr = np.corrcoef(state_history[i], state_history[i + 1])[0, 1]
                if not np.isnan(corr):
                    correlations.append(abs(corr))
            
            if len(correlations) == 0:
                return 0.0
            
            coherence = np.mean(correlations)
            return min(1.0, coherence)
            
        except Exception as e:
            print(f"Error computing coherence: {e}")
            return 0.0
    
    def compute_all_metrics(self) -> ConsciousnessMetrics:
        """Compute all consciousness metrics for this architecture"""
        start_time = time.time()
        
        phi = self.compute_phi_approximation()
        global_access = self.compute_global_access_score()
        integration_bw = self.compute_integration_bandwidth()
        coherence = self.compute_coherence_index()
        
        computational_time = time.time() - start_time
        
        return ConsciousnessMetrics(
            phi_approximation=phi,
            global_access_score=global_access,
            self_reference_depth=self.self_ref_depth,
            integration_bandwidth=integration_bw,
            coherence_index=coherence,
            computational_complexity=computational_time,
            architecture_type="RSRN"
        )

class RandomNetworkControl:
    """Random network control for falsification testing"""
    
    def __init__(self, n_nodes: int, edge_probability: float = 0.3):
        self.n_nodes = n_nodes
        self.graph = nx.erdos_renyi_graph(n_nodes, edge_probability)
        self.adjacency_matrix = nx.adjacency_matrix(self.graph).toarray()
    
    def compute_all_metrics(self) -> ConsciousnessMetrics:
        """Compute metrics for random network (should be low if hypothesis is correct)"""
        # Use same metric computation methods as RSRN
        rsrn_temp = RecursiveSelfReferenceNetwork(self.n_nodes, 0, 0)
        rsrn_temp.graph = self.graph
        rsrn_temp.adjacency_matrix = self.adjacency_matrix
        
        metrics = rsrn_temp.compute_all_metrics()
        metrics.architecture_type = "Random"
        metrics.self_reference_depth = 0
        
        return metrics

class ConsciousnessExperiment:
    """Main experimental framework for testing consciousness hypothesis"""
    
    def __init__(self):
        self.results = []
        self.start_time = time.time()
        
    def run_experiment(self, n_architectures: int = 100) -> Dict[str, Any]:
        """
        Run the complete consciousness experiment
        Following preregistered protocol exactly
        """
        print(f"Starting consciousness experiment with {n_architectures} architectures...")
        print("Preregistered success criteria: Φ > 0.5, p < 0.01, Cohen's d > 0.8")
        
        rsrn_results = []
        random_results = []
        
        # Test RSRN architectures with varying parameters
        for i in range(n_architectures // 2):
            # Vary network size and self-reference depth
            n_nodes = np.random.randint(10, 50)
            self_ref_depth = np.random.randint(1, 6)
            integration_strength = np.random.uniform(0.1, 0.9)
            
            rsrn = RecursiveSelfReferenceNetwork(n_nodes, self_ref_depth, integration_strength)
            metrics = rsrn.compute_all_metrics()
            rsrn_results.append(metrics)
            
            if (i + 1) % 10 == 0:
                print(f"Completed {i + 1} RSRN architectures...")
        
        # Test random network controls
        for i in range(n_architectures // 2):
            n_nodes = np.random.randint(10, 50)
            edge_prob = np.random.uniform(0.1, 0.5)
            
            random_net = RandomNetworkControl(n_nodes, edge_prob)
            metrics = random_net.compute_all_metrics()
            random_results.append(metrics)
            
            if (i + 1) % 10 == 0:
                print(f"Completed {i + 1} random controls...")
        
        # Statistical analysis
        analysis_results = self._analyze_results(rsrn_results, random_results)
        
        return analysis_results
    
    def _analyze_results(self, rsrn_results: List[ConsciousnessMetrics], 
                        random_results: List[ConsciousnessMetrics]) -> Dict[str, Any]:
        """Perform statistical analysis following preregistered plan"""
        
        # Extract Φ values for primary endpoint
        rsrn_phi = [r.phi_approximation for r in rsrn_results]
        random_phi = [r.phi_approximation for r in random_results]
        
        # Primary endpoint test: Φ > 0.5 in RSRN architectures
        rsrn_above_threshold = int(np.sum(np.array(rsrn_phi) > 0.5))
        rsrn_success_rate = rsrn_above_threshold / len(rsrn_phi)
        
        # Statistical significance test (Mann-Whitney U)
        statistic, p_value = stats.mannwhitneyu(rsrn_phi, random_phi, alternative='greater')
        
        # Effect size (Cohen's d)
        pooled_std = np.sqrt(((len(rsrn_phi) - 1) * np.var(rsrn_phi, ddof=1) + 
                             (len(random_phi) - 1) * np.var(random_phi, ddof=1)) / 
                            (len(rsrn_phi) + len(random_phi) - 2))
        
        if pooled_std > 0:
            cohens_d = (np.mean(rsrn_phi) - np.mean(random_phi)) / pooled_std
        else:
            cohens_d = 0.0
        
        # Bonferroni correction for multiple comparisons
        bonferroni_alpha = 0.01 / 5  # 5 metrics tested
        
        # Determine if hypothesis should be rejected
        primary_endpoint_met = rsrn_success_rate > 0.5  # Majority above threshold
        statistical_significance = p_value < bonferroni_alpha
        effect_size_adequate = abs(cohens_d) > 0.8
        
        hypothesis_supported = (primary_endpoint_met and 
                              statistical_significance and 
                              effect_size_adequate)
        
        results = {
            'experiment_duration': float(time.time() - self.start_time),
            'n_rsrn_architectures': len(rsrn_results),
            'n_random_controls': len(random_results),
            
            # Primary endpoint results
            'rsrn_phi_mean': float(np.mean(rsrn_phi)),
            'rsrn_phi_std': float(np.std(rsrn_phi)),
            'random_phi_mean': float(np.mean(random_phi)),
            'random_phi_std': float(np.std(random_phi)),
            'rsrn_above_threshold_count': rsrn_above_threshold,
            'rsrn_success_rate': float(rsrn_success_rate),
            
            # Statistical tests
            'mannwhitney_statistic': float(statistic),
            'p_value': float(p_value),
            'bonferroni_corrected_alpha': float(bonferroni_alpha),
            'cohens_d': float(cohens_d),
            
            # Success criteria evaluation
            'primary_endpoint_met': primary_endpoint_met,
            'statistical_significance': statistical_significance,
            'effect_size_adequate': effect_size_adequate,
            'hypothesis_supported': hypothesis_supported,
            
            # Detailed results (convert to JSON-serializable format)
            'rsrn_results': [convert_numpy_types(r.__dict__) for r in rsrn_results],
            'random_results': [convert_numpy_types(r.__dict__) for r in random_results]
        }
        
        return results

def main():
    """Execute the consciousness computation experiment"""
    print("=" * 60)
    print("CONSCIOUSNESS-COMPUTATION THEORY EXPERIMENT")
    print("Session: autonomous_20250531_082956_consciousness_computation_theory")
    print("=" * 60)
    
    experiment = ConsciousnessExperiment()
    results = experiment.run_experiment(n_architectures=100)
    
    # Save results
    timestamp = int(time.time())
    results_file = f"consciousness_experiment_results_{timestamp}.json"
    
    # Convert all numpy types to JSON-serializable types
    json_results = convert_numpy_types(results)
    
    with open(results_file, 'w') as f:
        json.dump(json_results, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 60)
    print("EXPERIMENT RESULTS SUMMARY")
    print("=" * 60)
    print(f"RSRN Φ mean: {results['rsrn_phi_mean']:.4f} ± {results['rsrn_phi_std']:.4f}")
    print(f"Random Φ mean: {results['random_phi_mean']:.4f} ± {results['random_phi_std']:.4f}")
    print(f"RSRN above threshold (Φ > 0.5): {results['rsrn_above_threshold_count']}/{results['n_rsrn_architectures']}")
    print(f"Success rate: {results['rsrn_success_rate']:.2%}")
    print(f"p-value: {results['p_value']:.6f}")
    print(f"Cohen's d: {results['cohens_d']:.4f}")
    print(f"Bonferroni corrected α: {results['bonferroni_corrected_alpha']:.6f}")
    
    print("\nSUCCESS CRITERIA EVALUATION:")
    print(f"Primary endpoint (majority Φ > 0.5): {'✓' if results['primary_endpoint_met'] else '✗'}")
    print(f"Statistical significance (p < 0.002): {'✓' if results['statistical_significance'] else '✗'}")
    print(f"Effect size (|d| > 0.8): {'✓' if results['effect_size_adequate'] else '✗'}")
    
    print(f"\nHYPOTHESIS STATUS: {'SUPPORTED' if results['hypothesis_supported'] else 'REJECTED'}")
    
    if not results['hypothesis_supported']:
        print("\n🎯 FALSIFICATION SUCCESSFUL!")
        print("This negative result advances scientific understanding by:")
        print("- Clarifying limitations of computational consciousness approaches")
        print("- Identifying methodological challenges in consciousness metrics")
        print("- Preventing pursuit of unproductive research directions")
    
    print(f"\nResults saved to: {results_file}")
    
    return results

if __name__ == "__main__":
    main() 