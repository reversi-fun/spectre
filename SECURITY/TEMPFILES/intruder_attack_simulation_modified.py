import numpy as np
import matplotlib.pyplot as plt
from network_generation import generate_aperiodic_network, generate_hexagonal_network, generate_triangular_network, generate_square_network
import random

# Parameters
SENSOR_RADIUS = 10
HOP_DISTANCE = SENSOR_RADIUS
MAX_HOPS = 1000

def simulate_intruder_attack(network, intruder_position, base_station_position, network_type):
    path = [intruder_position]
    time_steps = 0
    visited_nodes = set()
    is_aperiodic = network_type == 'Aperiodic'
    stack = [intruder_position]
    hop_count = 0
    pattern_found = False

    while not has_reached_base_station(intruder_position, base_station_position) and hop_count < MAX_HOPS:
        next_position, step_time, backtracked, pattern_found = smart_move(network, intruder_position, visited_nodes, is_aperiodic, stack, pattern_found, base_station_position)
        
        if backtracked:
            stack.pop()
        else:
            stack.append(next_position)
        
        intruder_position = next_position
        visited_nodes.add(tuple(intruder_position))
        path.append(intruder_position)
        time_steps += step_time
        hop_count += 1

    reached_base_station = has_reached_base_station(intruder_position, base_station_position)
    return path, time_steps, reached_base_station, hop_count, pattern_found

def smart_move(network, intruder_position, visited_nodes, is_aperiodic, stack, pattern_found, base_station_position):
    if pattern_found and not is_aperiodic:
        return move_towards_base_station(network, intruder_position, base_station_position), 1, False, True
    
    distances = np.linalg.norm(np.array(network) - np.array(intruder_position), axis=1)
    reachable_nodes = network[distances <= SENSOR_RADIUS]
    
    if not reachable_nodes.size:
        return intruder_position, 0, False, pattern_found
    
    unvisited_nodes = [node for node in reachable_nodes if tuple(node) not in visited_nodes or (stack and np.array_equal(node, stack[-1]))]
    
    if unvisited_nodes:
        next_node = min(unvisited_nodes, key=lambda node: np.linalg.norm(np.array(node) - np.array(intruder_position)))
        step_time = calculate_time_step(next_node, intruder_position, network)
        pattern_found = detect_pattern(intruder_position, next_node, network) if not is_aperiodic else False
        return next_node, step_time, False, pattern_found
    elif len(stack) > 1:
        previous_node = stack[-2]
        step_time = calculate_time_step(previous_node, intruder_position, network)
        return previous_node, step_time, True, pattern_found
    else:
        return intruder_position, 0, False, pattern_found

def move_towards_base_station(network, intruder_position, base_station_position):
    direction = np.array(base_station_position) - np.array(intruder_position)
    direction /= np.linalg.norm(direction)
    next_position = np.array(intruder_position) + direction * SENSOR_RADIUS
    return tuple(next_position)

def detect_pattern(current_node, next_node, network):
    angles, distances = get_unique_angles_distances(current_node, network)
    return len(set(angles)) <= 6 and len(set(distances)) <= 2

def calculate_time_step(nearest_node, current_node, network):
    distance = np.linalg.norm(np.array(nearest_node) - np.array(current_node))
    unique_angles, unique_distances = get_unique_angles_distances(current_node, network)
    complexity_factor = len(unique_angles) + len(unique_distances)
    return distance / SENSOR_RADIUS * complexity_factor

def get_unique_angles_distances(current_node, network):
    current_node = np.array(current_node)
    vectors = np.array(network) - current_node
    distances = np.linalg.norm(vectors, axis=1)
    angles = np.degrees(np.arctan2(vectors[:, 1], vectors[:, 0])) % 360
    return angles, distances

def has_reached_base_station(position, base_station_position):
    return np.linalg.norm(np.array(position) - np.array(base_station_position)) <= SENSOR_RADIUS

def run_simulation(num_iterations=10):
    random.seed(42)  # For reproducibility
    num_sensors = 559
    sensor_radius = SENSOR_RADIUS

    networks = {
        'Aperiodic': generate_aperiodic_network(sensor_radius, num_sensors, 3),
        'Hexagonal': generate_hexagonal_network(num_sensors, sensor_radius),
        'Triangular': generate_triangular_network(num_sensors, sensor_radius),
        'Square': generate_square_network(num_sensors, sensor_radius)
    }

    base_stations = {net_type: tuple(np.mean(network, axis=0)) for net_type, network in networks.items()}
    
    results = {net_type: {'time_steps': [], 'reached_base_station': [], 'hop_count': [], 'pattern_found': [], 'paths': []} for net_type in networks.keys()}
    
    for i in range(num_iterations):
        for net_type, network in networks.items():
            intruder_initial_position = network[0]  # Start at the first node, assumed to be compromised
            path, time_steps, reached_base_station, hop_count, pattern_found = simulate_intruder_attack(network, intruder_initial_position, base_stations[net_type], net_type)
            results[net_type]['time_steps'].append(time_steps)
            results[net_type]['reached_base_station'].append(reached_base_station)
            results[net_type]['hop_count'].append(hop_count)
            results[net_type]['pattern_found'].append(pattern_found)
            results[net_type]['paths'].append(path)
        print(f"Iteration {i + 1} completed.")

    plot_results(networks, base_stations, results)

def plot_results(networks, base_stations, results):
    for net_type, network in networks.items():
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.scatter(network[:, 0], network[:, 1], c='blue', alpha=0.5, label='Sensor')
        ax.scatter(*base_stations[net_type], c='green', s=100, label='Base Station')
        
        # Plot sensor ranges
        for sensor in network:
            circle = plt.Circle(sensor, SENSOR_RADIUS, color='lightblue', fill=False, alpha=0.3)
            ax.add_artist(circle)
        
        # Plot intruder path
        path = np.array(results[net_type]['paths'][0])  # Use the first simulation path
        ax.plot(path[:, 0], path[:, 1], c='red', label='Intruder Path')
        ax.scatter(*path[0], c='orange', s=100, label='Intruder Start')
        
        ax.set_title(f"{net_type} Network")
        ax.set_xlabel("X Coordinate")
        ax.set_ylabel("Y Coordinate")
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.7)

        plt.tight_layout()
        plt.savefig(f'{net_type}_network.png')
        plt.show()

    # Plot statistics
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, figsize=(20, 5))
    network_types = list(networks.keys())

    ax1.bar(network_types, [np.mean(results[nt]['time_steps']) for nt in network_types])
    ax1.set_title("Average Time Steps")
    ax1.set_ylabel("Time Steps")

    ax2.bar(network_types, [np.mean(results[nt]['reached_base_station']) for nt in network_types])
    ax2.set_title("Success Rate")
    ax2.set_ylabel("Rate")

    ax3.bar(network_types, [np.mean(results[nt]['hop_count']) for nt in network_types])
    ax3.set_title("Average Hop Count")
    ax3.set_ylabel("Hop Count")

    ax4.bar(network_types, [np.mean(results[nt]['pattern_found']) for nt in network_types])
    ax4.set_title("Pattern Recognition Rate")
    ax4.set_ylabel("Rate")

    for ax in (ax1, ax2, ax3, ax4):
        ax.set_xlabel("Network Topology")
        ax.tick_params(axis='x', rotation=45)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_simulation()
