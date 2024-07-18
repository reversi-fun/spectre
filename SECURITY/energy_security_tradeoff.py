# File: energy_security_tradeoff_simulation.py

import numpy as np
import matplotlib.pyplot as plt
import random
from network_generation import generate_aperiodic_network, generate_hexagonal_network, generate_triangular_network, generate_square_network
from securitymetricsaperiodic_hexagonal import calculate_total_energy_consumption
from claude_clone_simulation import simulate_clone_attack, SENSOR_RADIUS, COMMUNICATION_RANGE, CLONE_PERCENTAGE, DETECTION_THRESHOLD
import scienceplots
import os

plt.style.use(['science', 'ieee'])
plt.rcParams.update({'figure.dpi': 100})

# Parameters
NUM_SENSORS = 559
NUM_ITERATIONS = 1
NUM_ROUNDS = 100
TRANSMISSION_ENERGY = 0.1  # Energy consumed for each transmission
IDLE_ENERGY = 0.01  # Energy consumed when idle

def generate_networks(sensor_radius, num_sensors):
    aperiodic_network = generate_aperiodic_network(sensor_radius, num_sensors, 3)
    hexagonal_network = generate_hexagonal_network(num_sensors, sensor_radius)
    triangular_network = generate_triangular_network(num_sensors, sensor_radius)
    square_network = generate_square_network(num_sensors, sensor_radius)
    return {
        'Aperiodic': aperiodic_network,
        'Hexagonal': hexagonal_network,
        'Triangular': triangular_network,
        'Square': square_network
    }

def calculate_energy_efficiency(network, paths):
    total_energy = calculate_total_energy_consumption(network)
    for path in paths:
        total_energy += len(path) * TRANSMISSION_ENERGY
    total_energy += len(network) * IDLE_ENERGY * NUM_ROUNDS
    return total_energy

def calculate_security_metric(detections, total_clones, compromised_nodes, network_size):
    detection_rate = detections / total_clones if total_clones > 0 else 1
    compromise_rate = compromised_nodes / network_size
    return (detection_rate + (1 - compromise_rate)) / 2

def run_energy_security_simulation():
    networks = generate_networks(SENSOR_RADIUS, NUM_SENSORS)
    results = {network_type: {'energy_efficiency': 0, 'security_metric': 0} for network_type in networks.keys()}

    for network_type, network in networks.items():
        print(f"Simulating {network_type} network...")
        total_energy = 0
        total_security = 0
        
        for round_num in range(NUM_ROUNDS):
            print(f"Round {round_num + 1}/{NUM_ROUNDS} for {network_type} network...")
            clone_positions = np.random.choice(len(network), size=int(CLONE_PERCENTAGE * len(network)), replace=False)
            clone_positions = [tuple(network[i]) for i in clone_positions]
            
            detections, paths, _, _, detected_clones, compromised_nodes = simulate_clone_attack(
                network, clone_positions, tuple(np.mean(network, axis=0))
            )
            
            energy = calculate_energy_efficiency(network, paths)
            security = calculate_security_metric(len(detected_clones), len(clone_positions), compromised_nodes, len(network))
            
            total_energy += energy
            total_security += security
        
        results[network_type]['energy_efficiency'] = total_energy / NUM_ROUNDS
        results[network_type]['security_metric'] = total_security / NUM_ROUNDS

    return results

def plot_results(results):
    network_types = list(results.keys())
    energy_efficiency = [results[nt]['energy_efficiency'] for nt in network_types]
    security_metric = [results[nt]['security_metric'] for nt in network_types]

    # Energy Consumption Plot
    fig, ax1 = plt.subplots(figsize=(3.5, 2.5))
    ax1.set_xlabel('Network Topology')
    ax1.set_ylabel('Energy Consumption', color='tab:red')
    ax1.plot(network_types, energy_efficiency, color='tab:red', marker='o')
    ax1.tick_params(axis='y', labelcolor='tab:red')
    plt.title('Energy Efficiency')
    plt.tight_layout()
    plt.savefig('figures/energy_efficiency.png', dpi=600)
    plt.show()

    # Security Metric Plot
    fig, ax2 = plt.subplots(figsize=(3.5, 2.5))
    ax2.set_xlabel('Network Topology')
    ax2.set_ylabel('Security Metric', color='tab:blue')
    ax2.plot(network_types, security_metric, color='tab:blue', marker='s')
    ax2.tick_params(axis='y', labelcolor='tab:blue')
    plt.title('Security Metric')
    plt.tight_layout()
    plt.savefig('figures/security_metric.png', dpi=600)
    plt.show()

if __name__ == "__main__":
    results = run_energy_security_simulation()
    print("Simulation Results:")
    for network_type, metrics in results.items():
        print(f"{network_type} Network:")
        print(f"  Energy Efficiency: {metrics['energy_efficiency']:.2f}")
        print(f"  Security Metric: {metrics['security_metric']:.2f}")
    
    plot_results(results)
