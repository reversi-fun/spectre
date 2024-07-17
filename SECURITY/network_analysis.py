import numpy as np
import random
import matplotlib.pyplot as plt
from network_generation import generate_aperiodic_network, generate_hexagonal_network, generate_triangular_network, generate_square_network
from intruder_attack_simulation import simulate_intruder_attack
from energy_analysis import calculate_network_energy_usage

# Parameters
SENSOR_RADIUS = 10
ENERGY_DETECTION = 0.1  # Energy cost for detection
ENERGY_COMMUNICATION = 0.05  # Energy cost for communication
NUM_SENSORS = 559

def non_periodic_patterns_test(network, intruder_initial_position, base_station_position, network_type):
    path, _ = simulate_intruder_attack(network, intruder_initial_position, base_station_position, network_type)
    coverage_map = np.zeros((100, 100))  # Example coverage map
    for position in path:
        detecting_sensors = [sensor for sensor in network if np.linalg.norm(np.array(sensor) - np.array(position)) <= SENSOR_RADIUS]
        for sensor in detecting_sensors:
            x, y = sensor
            coverage_map[int(x) % 100, int(y) % 100] += 1
    return coverage_map

def efficient_communication_test(network, base_station_position):
    # Calculate average number of hops required for communication
    total_hops = 0
    for sensor in network:
        distance = np.linalg.norm(np.array(sensor) - np.array(base_station_position))
        total_hops += distance / SENSOR_RADIUS
    avg_hops = total_hops / len(network)
    return avg_hops

def fault_tolerance_test(network, failure_rate=0.1):
    failed_network = network.copy()
    num_failures = int(len(network) * failure_rate)
    failed_nodes = random.sample(range(len(failed_network)), num_failures)
    failed_network = [node for i, node in enumerate(failed_network) if i not in failed_nodes]

    if not failed_network:
        return False  # All nodes failed

    remaining_nodes = [tuple(node) for node in failed_network]
    if not remaining_nodes:
        return False  # All nodes failed

    # Check if network is still connected
    start_node = remaining_nodes[0]
    visited = set()
    stack = [start_node]
    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            neighbors = [tuple(n) for n in remaining_nodes if np.linalg.norm(np.array(node) - np.array(n)) <= SENSOR_RADIUS]
            stack.extend(neighbors)

    return len(visited) == len(remaining_nodes)  # Check if all remaining nodes are connected

def redundancy_and_backup_paths_test(network):
    # Check for multiple paths between nodes
    paths = []
    for i, node in enumerate(network):
        for j in range(i + 1, len(network)):
            other_node = network[j]
            distance = np.linalg.norm(np.array(node) - np.array(other_node))
            if distance <= SENSOR_RADIUS * 2:
                paths.append((tuple(node), tuple(other_node)))

    # Check if there are multiple paths
    multiple_paths = len(paths) > len(network)
    return multiple_paths

def plot_results(metrics, rounds):
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # Average Hops
    for network_type in metrics:
        axes[0, 0].plot(rounds, metrics[network_type]['avg_hops'], label=network_type)
    axes[0, 0].set_title('Average Hops')
    axes[0, 0].set_xlabel('Rounds')
    axes[0, 0].set_ylabel('Average Hops')
    axes[0, 0].legend()

    # Fault Tolerance
    for network_type in metrics:
        axes[0, 1].plot(rounds, metrics[network_type]['fault_tolerant'], label=network_type)
    axes[0, 1].set_title('Fault Tolerance')
    axes[0, 1].set_xlabel('Rounds')
    axes[0, 1].set_ylabel('Fault Tolerance (1=True, 0=False)')
    axes[0, 1].legend()

    # Multiple Paths
    for network_type in metrics:
        axes[1, 0].plot(rounds, metrics[network_type]['multiple_paths'], label=network_type)
    axes[1, 0].set_title('Multiple Paths')
    axes[1, 0].set_xlabel('Rounds')
    axes[1, 0].set_ylabel('Multiple Paths (1=True, 0=False)')
    axes[1, 0].legend()

    plt.tight_layout()
    plt.show()

def main(num_rounds=5):
    random.seed()  # Ensure randomness in each simulation run

    # Generate networks
    aperiodic_network = generate_aperiodic_network(SENSOR_RADIUS, NUM_SENSORS, num_rounds)
    hexagonal_network = generate_hexagonal_network(NUM_SENSORS, SENSOR_RADIUS)
    triangular_network = generate_triangular_network(NUM_SENSORS, SENSOR_RADIUS)
    square_network = generate_square_network(NUM_SENSORS, SENSOR_RADIUS)

    # Base station positions (center of the network)
    aperiodic_base_station = tuple(np.mean(aperiodic_network, axis=0))
    hexagonal_base_station = tuple(np.mean(hexagonal_network, axis=0))
    triangular_base_station = tuple(np.mean(triangular_network, axis=0))
    square_base_station = tuple(np.mean(square_network, axis=0))

    network_types = ['Aperiodic', 'Hexagonal', 'Triangular', 'Square']
    networks = [aperiodic_network, hexagonal_network, triangular_network, square_network]
    base_stations = [aperiodic_base_station, hexagonal_base_station, triangular_base_station, square_base_station]

    # Results storage
    metrics = {network_type: {'avg_hops': [], 'fault_tolerant': [], 'multiple_paths': []} for network_type in network_types}
    rounds = list(range(1, num_rounds + 1))

    for round_num in rounds:
        for network_type, network, base_station in zip(network_types, networks, base_stations):
            intruder_initial_position = (random.uniform(-200, 200), random.uniform(-200, 200))

            # Efficient Communication Test
            avg_hops = efficient_communication_test(network, base_station)
            metrics[network_type]['avg_hops'].append(avg_hops)

            # Fault Tolerance Test
            fault_tolerant = fault_tolerance_test(network)
            metrics[network_type]['fault_tolerant'].append(int(fault_tolerant))

            # Redundancy and Backup Paths Test
            multiple_paths = redundancy_and_backup_paths_test(network)
            metrics[network_type]['multiple_paths'].append(int(multiple_paths))

        print(f"Round {round_num} completed.")

    # Display metrics
    for network_type in metrics:
        print(f"{network_type} Network:")
        print(f"  Average Hops: {metrics[network_type]['avg_hops']}")
        print(f"  Fault Tolerance: {metrics[network_type]['fault_tolerant']}")
        print(f"  Multiple Paths: {metrics[network_type]['multiple_paths']}")

    # Plot results
    plot_results(metrics, rounds)

if __name__ == "__main__":
    main(num_rounds=5)
