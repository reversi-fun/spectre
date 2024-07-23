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
NUM_SENSORS = 71
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
    total_energy += len(network) * IDLE_ENERGY
    return total_energy / NUM_ROUNDS

def calculate_detection_rate(detections, total_clones):
    return detections / total_clones if total_clones > 0 else 1

def calculate_compromise_rate(compromised_nodes, network_size):
    return compromised_nodes / network_size

def calculate_security_metric(detection_rate, compromise_rate):
    return (detection_rate + (1 - compromise_rate)) / 2

def run_energy_security_simulation():
    networks = generate_networks(SENSOR_RADIUS, NUM_SENSORS)
    results = {network_type: {'energy_efficiency': [], 'detection_rate': [], 'compromise_rate': [], 'security_metric': []} for network_type in networks.keys()}

    for network_type, network in networks.items():
        print(f"Simulating {network_type} network...")
        
        for round_num in range(NUM_ROUNDS):
            print(f"Round {round_num + 1}/{NUM_ROUNDS} for {network_type} network...")
            clone_positions = np.random.choice(len(network), size=int(CLONE_PERCENTAGE * len(network)), replace=False)
            clone_positions = [tuple(network[i]) for i in clone_positions]
            
            detections, paths, _, _, detected_clones, compromised_nodes = simulate_clone_attack(
                network, clone_positions, tuple(np.mean(network, axis=0))
            )
            
            energy = calculate_energy_efficiency(network, paths)
            detection_rate = calculate_detection_rate(len(detected_clones), len(clone_positions))
            compromise_rate = calculate_compromise_rate(compromised_nodes, len(network))
            security = calculate_security_metric(detection_rate, compromise_rate)
            
            results[network_type]['energy_efficiency'].append(energy)
            results[network_type]['detection_rate'].append(detection_rate)
            results[network_type]['compromise_rate'].append(compromise_rate)
            results[network_type]['security_metric'].append(security)
    
    return results

def plot_results(results):
    network_types = list(results.keys())
    
    # Plot each metric separately
    metrics = ['energy_efficiency', 'detection_rate', 'compromise_rate', 'security_metric']
    y_labels = ['Average Energy Consumption', 'Detection Rate', 'Compromise Rate', 'Security Metric']
    titles = ['Average Energy Efficiency', 'Detection Rate', 'Compromise Rate', 'Security Metric']

    for metric, y_label, title in zip(metrics, y_labels, titles):
        for network_type in network_types:
            plt.figure(figsize=(3.5, 2.5))
            plt.plot(range(NUM_ROUNDS), results[network_type][metric], marker='o', linestyle='-')
            plt.title(f'{title} for {network_type} Network')
            plt.xlabel('Rounds')
            plt.ylabel(y_label)
            plt.tight_layout()
            plt.savefig(f'figures/{network_type}_{metric}.png', dpi=600)
            plt.show()

if __name__ == "__main__":
    results = run_energy_security_simulation()
    print("Simulation Results:")
    for network_type, metrics in results.items():
        print(f"{network_type} Network:")
        avg_energy_efficiency = np.mean(metrics['energy_efficiency'])
        avg_detection_rate = np.mean(metrics['detection_rate'])
        avg_compromise_rate = np.mean(metrics['compromise_rate'])
        avg_security_metric = np.mean(metrics['security_metric'])
        print(f"  Average Energy Efficiency: {avg_energy_efficiency:.2f}")
        print(f"  Average Detection Rate: {avg_detection_rate:.2f}")
        print(f"  Average Compromise Rate: {avg_compromise_rate:.2f}")
        print(f"  Average Security Metric: {avg_security_metric:.2f}")
    
    plot_results(results)
