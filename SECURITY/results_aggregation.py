# results_aggregation.py

import numpy as np
import matplotlib.pyplot as plt
from metrics_calculation import calculate_detection_rate, calculate_false_positives_negatives, calculate_energy_consumption, calculate_node_failure_rates
from intruder_attack_simulation import simulate_intruder_attack
from network_generation import generate_aperiodic_network, generate_hexagonal_network, generate_triangular_network, generate_square_network
import random

# Parameters
SENSOR_RADIUS = 10
NUM_ITERATIONS = 100

def aggregate_results(num_sensors, sensor_radius, num_iterations):
    # Generate networks
    aperiodic_network = generate_aperiodic_network(sensor_radius, num_sensors, num_iterations)
    hexagonal_network = generate_hexagonal_network(num_sensors, sensor_radius)
    triangular_network = generate_triangular_network(num_sensors, sensor_radius)
    square_network = generate_square_network(num_sensors, sensor_radius)

    # Base station positions (center of the network)
    aperiodic_base_station = tuple(np.mean(aperiodic_network, axis=0))
    hexagonal_base_station = tuple(np.mean(hexagonal_network, axis=0))
    triangular_base_station = tuple(np.mean(triangular_network, axis=0))
    square_base_station = tuple(np.mean(square_network, axis=0))

    network_types = ['Aperiodic', 'Hexagonal', 'Triangular', 'Square']
    networks = [aperiodic_network, hexagonal_network, triangular_network, square_network]
    base_stations = [aperiodic_base_station, hexagonal_base_station, triangular_base_station, square_base_station]
    
    metrics = {network_type: {'Detection Rate': [], 'False Positives': [], 'False Negatives': [], 'Energy Consumption': [], 'Node Failure Rate': []} for network_type in network_types}
    
    for i in range(num_iterations):
        for network_type, network, base_station in zip(network_types, networks, base_stations):
            intruder_initial_position = (random.uniform(-200, 200), random.uniform(-200, 200))
            path, _ = simulate_intruder_attack(network, intruder_initial_position, base_station, network_type)
            
            detection_rate = calculate_detection_rate(network, path)
            false_positives, false_negatives = calculate_false_positives_negatives(network, path)
            energy_consumption = calculate_energy_consumption(network, path)
            node_failure_rate = calculate_node_failure_rates(network, path)
            
            metrics[network_type]['Detection Rate'].append(detection_rate)
            metrics[network_type]['False Positives'].append(false_positives)
            metrics[network_type]['False Negatives'].append(false_negatives)
            metrics[network_type]['Energy Consumption'].append(energy_consumption)
            metrics[network_type]['Node Failure Rate'].append(node_failure_rate)
        
        print(f"Iteration {i + 1} completed.")
    
    avg_metrics = {network_type: {metric: np.mean(values) for metric, values in metrics[network_type].items()} for network_type in network_types}
    
    return avg_metrics

def plot_results(avg_metrics):
    fig, ax = plt.subplots(2, 2, figsize=(12, 12))
    fig.suptitle('Average Metrics for Different Network Topologies')

    network_types = list(avg_metrics.keys())

    detection_rates = [avg_metrics[nt]['Detection Rate'] for nt in network_types]
    false_positives = [avg_metrics[nt]['False Positives'] for nt in network_types]
    energy_consumptions = [avg_metrics[nt]['Energy Consumption'] for nt in network_types]
    node_failure_rates = [avg_metrics[nt]['Node Failure Rate'] for nt in network_types]

    ax[0, 0].bar(network_types, detection_rates, color=['red', 'green', 'blue', 'purple'])
    ax[0, 0].set_title('Average Detection Rate')
    ax[0, 0].set_ylabel('Detection Rate')

    ax[0, 1].bar(network_types, false_positives, color=['red', 'green', 'blue', 'purple'])
    ax[0, 1].set_title('Average False Positives')
    ax[0, 1].set_ylabel('False Positives')

    ax[1, 0].bar(network_types, energy_consumptions, color=['red', 'green', 'blue', 'purple'])
    ax[1, 0].set_title('Average Energy Consumption')
    ax[1, 0].set_ylabel('Energy Consumption')

    ax[1, 1].bar(network_types, node_failure_rates, color=['red', 'green', 'blue', 'purple'])
    ax[1, 1].set_title('Average Node Failure Rate')
    ax[1, 1].set_ylabel('Node Failure Rate')

    for a in ax.flat:
        a.set_xlabel('Network Topology')

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()

def main():
    num_sensors = 559
    sensor_radius = SENSOR_RADIUS
    num_iterations = NUM_ITERATIONS

    avg_metrics = aggregate_results(num_sensors, sensor_radius, num_iterations)
    plot_results(avg_metrics)

if __name__ == "__main__":
    main()
