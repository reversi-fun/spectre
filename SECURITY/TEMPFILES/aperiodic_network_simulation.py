# File: aperiodic_network_simulation.py

import numpy as np
import matplotlib.pyplot as plt
from network_generation import generate_aperiodic_network, generate_triangular_network, generate_square_network, generate_hexagonal_network
from intruder_attack_simulation import simulate_intruder_attack
from metrics_calculation import calculate_detection_rate, calculate_false_positives_negatives, calculate_energy_consumption, calculate_node_failure_rates

SENSOR_RADIUS = 10
NUM_SENSORS = 559
NUM_ITERATIONS = 3
NUM_ROUNDS = 10

def setup_network_topologies():
    aperiodic_network = generate_aperiodic_network(SENSOR_RADIUS, NUM_SENSORS, NUM_ITERATIONS)
    triangular_network = generate_triangular_network(NUM_SENSORS, SENSOR_RADIUS)
    square_network = generate_square_network(NUM_SENSORS, SENSOR_RADIUS)
    hexagonal_network = generate_hexagonal_network(NUM_SENSORS, SENSOR_RADIUS)
    return aperiodic_network, triangular_network, square_network, hexagonal_network

def run_simulation(network, network_type, base_station_position):
    intruder_initial_position = (np.random.uniform(-200, 200), np.random.uniform(-200, 200))
    path, time_steps = simulate_intruder_attack(network, intruder_initial_position, base_station_position, network_type)
    return path, time_steps

def collect_metrics(network, path):
    detection_rate = calculate_detection_rate(network, path)
    false_positives, false_negatives = calculate_false_positives_negatives(network, path)
    energy_consumption = calculate_energy_consumption(network, path)
    node_failure_rate = calculate_node_failure_rates(network, path)
    return {
        'detection_rate': detection_rate,
        'false_positives': false_positives,
        'false_negatives': false_negatives,
        'energy_consumption': energy_consumption,
        'node_failure_rate': node_failure_rate
    }

def average_metrics(metrics_list):
    averaged_metrics = {}
    for key in metrics_list[0]:
        averaged_metrics[key] = np.mean([metrics[key] for metrics in metrics_list])
    return averaged_metrics

def visualize_results(all_averaged_metrics):
    # Plot Detection Rate
    plt.figure()
    for metrics in all_averaged_metrics:
        plt.plot(metrics['rounds'], metrics['detection_rate'], label=metrics['label'])
    plt.xlabel('Rounds')
    plt.ylabel('Detection Rate')
    plt.title('Comparison of Detection Rate')
    plt.legend()
    plt.savefig('detection_rate_comparison.png')
    plt.show()

    # Plot Energy Consumption
    plt.figure()
    for metrics in all_averaged_metrics:
        plt.plot(metrics['rounds'], metrics['energy_consumption'], label=metrics['label'])
    plt.xlabel('Rounds')
    plt.ylabel('Energy Consumption (J)')
    plt.title('Comparison of Energy Consumption')
    plt.legend()
    plt.savefig('energy_consumption_comparison.png')
    plt.show()

    # Plot Node Failure Rate
    plt.figure()
    for metrics in all_averaged_metrics:
        plt.plot(metrics['rounds'], metrics['node_failure_rate'], label=metrics['label'])
    plt.xlabel('Rounds')
    plt.ylabel('Node Failure Rate')
    plt.title('Comparison of Node Failure Rate')
    plt.legend()
    plt.savefig('node_failure_rate_comparison.png')
    plt.show()

def main():
    aperiodic_network, triangular_network, square_network, hexagonal_network = setup_network_topologies()

    networks = [
        {'network': aperiodic_network, 'label': 'Aperiodic'},
        {'network': triangular_network, 'label': 'Triangular'},
        {'network': square_network, 'label': 'Square'},
        {'network': hexagonal_network, 'label': 'Hexagonal'}
    ]

    all_averaged_metrics = []

    for network in networks:
        all_rounds_metrics = []
        base_station_position = tuple(np.mean(network['network'], axis=0))
        for _ in range(NUM_ROUNDS):
            path, time_steps = run_simulation(network['network'], network['label'], base_station_position)
            metrics = collect_metrics(network['network'], path)
            metrics['rounds'] = list(range(1, NUM_ROUNDS + 1))
            all_rounds_metrics.append(metrics)
        averaged_metrics = average_metrics(all_rounds_metrics)
        averaged_metrics['label'] = network['label']
        all_averaged_metrics.append(averaged_metrics)

    visualize_results(all_averaged_metrics)

if __name__ == "__main__":
    main()
