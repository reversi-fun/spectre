# File: security_tests.py

import numpy as np
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

def select_compromised_nodes(network):
    num_compromised = int(len(network) * COMPROMISE_RATIO)
    return np.random.choice(network, num_compromised, replace=False)

def selective_forwarding_attack(network, compromised_nodes, base_station_position):
    path = []
    time_steps = 0
    current_node = (np.random.uniform(-200, 200), np.random.uniform(-200, 200))
    
    while current_node != base_station_position:
        if current_node in compromised_nodes:
            if np.random.rand() > 0.5:
                # Drop packet
                continue
        
        path.append(current_node)
        time_steps += 1
        
        # Move towards the base station
        next_node = move_towards_base_station(current_node, base_station_position, network)
        current_node = next_node

    return path, time_steps

def dos_attack(network, base_station_position):
    path = []
    time_steps = 0
    current_node = (np.random.uniform(-200, 200), np.random.uniform(-200, 200))

    while current_node != base_station_position:
        path.append(current_node)
        time_steps += 1

        # Simulate DoS by randomly dropping packets
        if np.random.rand() > 0.5:
            continue

        next_node = move_towards_base_station(current_node, base_station_position, network)
        current_node = next_node

    return path, time_steps

def move_towards_base_station(current_node, base_station_position, network):
    # Simple heuristic to move towards the base station
    closest_node = min(network, key=lambda node: np.linalg.norm(np.array(node) - np.array(base_station_position)))
    return closest_node

def run_simulation(network, attack_type, base_station_position):
    compromised_nodes = select_compromised_nodes(network)
    
    if attack_type == "selective_forwarding":
        path, time_steps = selective_forwarding_attack(network, compromised_nodes, base_station_position)
    elif attack_type == "dos":
        path, time_steps = dos_attack(network, base_station_position)
    
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

def main():
    aperiodic_network, hexagonal_network, triangular_network, square_network = setup_network_topologies()

    networks = [
        {'network': aperiodic_network, 'label': 'Aperiodic'},
        {'network': hexagonal_network, 'label': 'Hexagonal'},
        {'network': triangular_network, 'label': 'Triangular'},
        {'network': square_network, 'label': 'Square'}
    ]

    attack_types = ["selective_forwarding", "dos"]

    for attack_type in attack_types:
        all_averaged_metrics = []

        for network in networks:
            all_rounds_metrics = []
            base_station_position = tuple(np.mean(network['network'], axis=0))
            for _ in range(NUM_ITERATIONS):
                path, time_steps = run_simulation(network['network'], attack_type, base_station_position)
                metrics = collect_metrics(network['network'], path)
                metrics['rounds'] = list(range(1, NUM_ITERATIONS + 1))
                all_rounds_metrics.append(metrics)
            averaged_metrics = average_metrics(all_rounds_metrics)
            averaged_metrics['label'] = network['label']
            all_averaged_metrics.append(averaged_metrics)

        visualize_results(all_averaged_metrics, attack_type)

def visualize_results(all_averaged_metrics, attack_type):
    rounds = list(range(1, NUM_ITERATIONS + 1))

    # Plot Detection Rate
    plt.figure()
    for metrics in all_averaged_metrics:
        plt.plot(rounds, [metrics['detection_rate']] * NUM_ITERATIONS, label=metrics['label'])
    plt.xlabel('Rounds')
    plt.ylabel('Detection Rate')
    plt.title(f'Comparison of Detection Rate ({attack_type.capitalize()})')
    plt.legend()
    plt.savefig(f'detection_rate_comparison_{attack_type}.png')
    plt.show()

    # Plot Energy Consumption
    plt.figure()
    for metrics in all_averaged_metrics:
        plt.plot(rounds, [metrics['energy_consumption']] * NUM_ITERATIONS, label=metrics['label'])
    plt.xlabel('Rounds')
    plt.ylabel('Energy Consumption (J)')
    plt.title(f'Comparison of Energy Consumption ({attack_type.capitalize()})')
    plt.legend()
    plt.savefig(f'energy_consumption_comparison_{attack_type}.png')
    plt.show()

    # Plot Node Failure Rate
    plt.figure()
    for metrics in all_averaged_metrics:
        plt.plot(rounds, [metrics['node_failure_rate']] * NUM_ITERATIONS, label=metrics['label'])
    plt.xlabel('Rounds')
    plt.ylabel('Node Failure Rate')
    plt.title(f'Comparison of Node Failure Rate ({attack_type.capitalize()})')
    plt.legend()
    plt.savefig(f'node_failure_rate_comparison_{attack_type}.png')
    plt.show()

if __name__ == "__main__":
    main()
