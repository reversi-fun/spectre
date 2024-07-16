# File: enhanced_intruder_attack_simulation.py

import numpy as np
import matplotlib.pyplot as plt
from network_generation import generate_aperiodic_network, generate_hexagonal_network, generate_triangular_network, generate_square_network
from metrics_calculation import calculate_detection_rate, calculate_false_positives_negatives, calculate_energy_consumption, calculate_node_failure_rates

SENSOR_RADIUS = 10
NUM_SENSORS = 559
NUM_ITERATIONS = 3
COMPROMISE_RATIO = 0.1  # 10% of nodes are compromised

def setup_network_topologies():
    aperiodic_network = generate_aperiodic_network(SENSOR_RADIUS, NUM_SENSORS, NUM_ITERATIONS)
    hexagonal_network = generate_hexagonal_network(NUM_SENSORS, SENSOR_RADIUS)
    triangular_network = generate_triangular_network(NUM_SENSORS, SENSOR_RADIUS)
    square_network = generate_square_network(NUM_SENSORS, SENSOR_RADIUS)
    return aperiodic_network, hexagonal_network, triangular_network, square_network

def validate_network(network):
    for pos in network:
        try:
            np.array(pos, dtype=float)
        except ValueError as e:
            print(f"Invalid position in network: {pos} - {e}")
            raise

def select_compromised_nodes(network_positions):
    num_compromised = int(len(network_positions) * COMPROMISE_RATIO)
    return np.random.choice(list(network_positions.keys()), num_compromised, replace=False)

def selective_forwarding_attack(network_positions, network_edges, compromised_nodes, base_station_position):
    path = []
    time_steps = 0
    current_node = np.random.choice(list(network_positions.keys()))
    
    while tuple(network_positions[current_node]) != tuple(base_station_position):
        if current_node in compromised_nodes:
            if np.random.rand() > 0.5:
                # Drop packet
                continue
        
        path.append(current_node)
        time_steps += 1
        
        # Move towards the base station
        next_node = move_towards_base_station(current_node, base_station_position, network_positions, network_edges)
        current_node = next_node

    return path, time_steps

def move_towards_base_station(current_node, base_station_position, network_positions, network_edges):
    # Simple heuristic to move towards the base station
    closest_node = min(network_positions.keys(), key=lambda node: np.linalg.norm(network_positions[node] - base_station_position))
    return closest_node

def run_simulation(network_positions, network_edges, network_type, base_station_position):
    compromised_nodes = select_compromised_nodes(network_positions)
    path, time_steps = selective_forwarding_attack(network_positions, network_edges, compromised_nodes, base_station_position)
    return path, time_steps

def collect_metrics(network_positions, path):
    detection_rate = calculate_detection_rate(network_positions, path)
    false_positives, false_negatives = calculate_false_positives_negatives(network_positions, path)
    energy_consumption = calculate_energy_consumption(network_positions, path)
    node_failure_rate = calculate_node_failure_rates(network_positions, path)
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
    rounds = list(range(1, NUM_ITERATIONS + 1))

    # Plot Detection Rate
    plt.figure()
    for metrics in all_averaged_metrics:
        plt.plot(rounds, [metrics['detection_rate']] * NUM_ITERATIONS, label=metrics['label'])
    plt.xlabel('Rounds')
    plt.ylabel('Detection Rate')
    plt.title('Comparison of Detection Rate')
    plt.legend()
    plt.savefig('detection_rate_comparison.png')
    plt.show()

    # Plot Energy Consumption
    plt.figure()
    for metrics in all_averaged_metrics:
        plt.plot(rounds, [metrics['energy_consumption']] * NUM_ITERATIONS, label=metrics['label'])
    plt.xlabel('Rounds')
    plt.ylabel('Energy Consumption (J)')
    plt.title('Comparison of Energy Consumption')
    plt.legend()
    plt.savefig('energy_consumption_comparison.png')
    plt.show()

    # Plot Node Failure Rate
    plt.figure()
    for metrics in all_averaged_metrics:
        plt.plot(rounds, [metrics['node_failure_rate']] * NUM_ITERATIONS, label=metrics['label'])
    plt.xlabel('Rounds')
    plt.ylabel('Node Failure Rate')
    plt.title('Comparison of Node Failure Rate')
    plt.legend()
    plt.savefig('node_failure_rate_comparison.png')
    plt.show()

def main():
    aperiodic_network, hexagonal_network, triangular_network, square_network = setup_network_topologies()

    networks = [
        {'network': aperiodic_network, 'label': 'Aperiodic'},
        {'network': hexagonal_network, 'label': 'Hexagonal'},
        {'network': triangular_network, 'label': 'Triangular'},
        {'network': square_network, 'label': 'Square'}
    ]

    all_averaged_metrics = []

    for network_info in networks:
        network_positions = {i: np.array(pos, dtype=float) for i, pos in enumerate(network_info['network'])}
        validate_network(network_positions)  # Ensure all positions are valid
        all_rounds_metrics = []
        network_edges = [(i, j) for i, pos_i in network_positions.items() for j, pos_j in network_positions.items() if np.linalg.norm(pos_i - pos_j) < SENSOR_RADIUS and i != j]
        base_station_position = np.mean(list(network_positions.values()), axis=0)
        for _ in range(NUM_ITERATIONS):
            path, time_steps = run_simulation(network_positions, network_edges, network_info['label'], base_station_position)
            metrics = collect_metrics(network_positions, path)
            metrics['rounds'] = list(range(1, NUM_ITERATIONS + 1))
            all_rounds_metrics.append(metrics)
        averaged_metrics = average_metrics(all_rounds_metrics)
        averaged_metrics['label'] = network_info['label']
        all_averaged_metrics.append(averaged_metrics)

    visualize_results(all_averaged_metrics)

if __name__ == "__main__":
    main()