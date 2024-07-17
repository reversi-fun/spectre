# File: clone_attack_detection_simulation.py

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from network_generation import generate_aperiodic_network, generate_hexagonal_network, generate_triangular_network, generate_square_network
import random

# Parameters
SENSOR_RADIUS = 10
COMMUNICATION_RANGE = SENSOR_RADIUS * 2
CLONE_PERCENTAGE = 0.01
DETECTION_THRESHOLD = 0.1  # Probability threshold for detecting a cloned node

# Seaborn settings for professional plots
sns.set(style="whitegrid")

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

def get_cloned_positions(network, seed, clone_percentage):
    random.seed(seed)
    num_clones = int(len(network) * clone_percentage)
    clone_indices = np.random.choice(len(network), num_clones, replace=False)
    return [tuple(network[idx]) for idx in clone_indices]

def simulate_clone_attack(network, clone_positions, base_station_position):
    detections = 0
    paths = []
    time_steps = 0
    total_hops = 0
    detected_clones = set()
    compromised_nodes = set(clone_positions)
    base_station_reached = False

    for clone_position in clone_positions:
        path = [clone_position]
        visited_nodes = set()
        while not has_reached_base_station(clone_position, base_station_position):
            visited_nodes.add(tuple(clone_position))
            next_position, step_time, pattern_found = smart_random_walk(network, clone_position, visited_nodes)
            if next_position is None:
                print(f"Clone at {clone_position} could not move further.")
                break
            if np.linalg.norm(np.array(next_position) - np.array(clone_position)) > COMMUNICATION_RANGE:
                print(f"Invalid hop detected from {clone_position} to {next_position}, stopping simulation for this node.")
                break
            clone_position = next_position
            compromised_nodes.add(tuple(clone_position))
            path.append(clone_position)
            time_steps += step_time
            total_hops += 1
            if random.random() < DETECTION_THRESHOLD:
                detected_clones.add(tuple(clone_position))
                detections += 1
                break
            if has_reached_base_station(clone_position, base_station_position):
                base_station_reached = True
                break
        paths.append(path)
        if base_station_reached:
            break
    
    return detections, paths, time_steps, total_hops, detected_clones, len(compromised_nodes), base_station_reached

def smart_random_walk(network, intruder_position, visited_nodes):
    distances = np.linalg.norm(np.array(network) - np.array(intruder_position), axis=1)
    sorted_indices = np.argsort(distances)
    for idx in sorted_indices:
        nearest_node = network[idx]
        if tuple(nearest_node) not in visited_nodes and np.linalg.norm(nearest_node - intruder_position) <= COMMUNICATION_RANGE:
            step_time = calculate_time_step(nearest_node, intruder_position, network)
            pattern_found = detect_pattern(nearest_node, network)
            return nearest_node, step_time, pattern_found
    return None, 0, False

def calculate_time_step(nearest_node, current_node, network):
    distance = np.linalg.norm(np.array(nearest_node) - np.array(current_node))
    unique_angles, unique_distances = get_unique_angles_distances(current_node, network)
    complexity_factor = len(unique_angles) + len(unique_distances)
    return distance / SENSOR_RADIUS * complexity_factor

def get_unique_angles_distances(current_node, network):
    current_node = np.array(current_node)
    unique_angles = set()
    unique_distances = set()
    
    for node in network:
        node = np.array(node)
        vector = node - current_node
        distance = np.linalg.norm(vector)
        unique_distances.add(distance)
        
        angle = np.degrees(np.arctan2(vector[1], vector[0]))
        if angle < 0:
            angle += 360
        unique_angles.add(angle)
    
    return unique_angles, unique_distances

def detect_pattern(current_node, network):
    unique_angles, unique_distances = get_unique_angles_distances(current_node, network)
    
    max_angles = 6
    max_distances = 2
    
    return len(unique_angles) <= max_angles and len(unique_distances) <= max_distances

def has_reached_base_station(position, base_station_position):
    return np.linalg.norm(np.array(position) - np.array(base_station_position)) <= SENSOR_RADIUS

def plot_network_with_paths(network, paths, clone_positions, detected_clones, base_station_position, title):
    fig, ax = plt.subplots()
    network = np.array(network)
    
    # Plot sensors and their ranges
    for node in network:
        sensor_circle = plt.Circle(node, SENSOR_RADIUS, color='blue', alpha=0.2)
        ax.add_artist(sensor_circle)
        plt.plot(node[0], node[1], 'bo', markersize=2, label='Uncompromised Nodes' if 'Uncompromised Nodes' not in plt.gca().get_legend_handles_labels()[1] else "")
    
    # Plot base station
    plt.plot(base_station_position[0], base_station_position[1], 'go', markersize=10, label='Base Station')
    
    # Plot cloned nodes
    for pos in clone_positions:
        plt.plot(pos[0], pos[1], 'ro', markersize=5, label='Cloned Nodes' if 'Cloned Nodes' not in plt.gca().get_legend_handles_labels()[1] else "")
    
    # Plot detected cloned nodes
    for pos in detected_clones:
        plt.plot(pos[0], pos[1], 'go', markersize=5, label='Detected Cloned Nodes' if 'Detected Cloned Nodes' not in plt.gca().get_legend_handles_labels()[1] else "")
    
    # Plot paths
    for path in paths:
        path = np.array(path)
        plt.plot(path[:, 0], path[:, 1], 'r-', linewidth=1)

    plt.title(title)
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.legend()
    plt.grid(True)
    plt.axis('equal')
    plt.show()

def run_simulation(num_sensors=559, num_iterations=1, num_rounds=10):
    sensor_radius = SENSOR_RADIUS
    networks = generate_networks(sensor_radius, num_sensors)
    results = {network_type: {'detections': 0, 'paths': [], 'time_steps': 0, 'total_hops': 0, 'base_station_reached': 0, 'detected_clones': set(), 'compromised_nodes': 0} for network_type in networks.keys()}
    
    for round_idx in range(num_rounds):
        print(f"Round {round_idx + 1}")
        round_seed = round_idx  # Use round index as the seed for consistency
        clone_positions_per_network = {network_type: get_cloned_positions(network, round_seed, CLONE_PERCENTAGE) for network_type, network in networks.items()}
        
        for network_type, network in networks.items():
            clone_positions = clone_positions_per_network[network_type]
            for iteration in range(num_iterations):
                detections, paths, time_steps, total_hops, detected_clones, compromised_nodes, base_station_reached = simulate_clone_attack(network, clone_positions, tuple(np.mean(network, axis=0)))
                results[network_type]['detections'] += detections
                results[network_type]['paths'].extend(paths)
                results[network_type]['time_steps'] += time_steps
                results[network_type]['total_hops'] += total_hops
                results[network_type]['detected_clones'].update(detected_clones)
                results[network_type]['compromised_nodes'] += compromised_nodes
                if base_station_reached:
                    results[network_type]['base_station_reached'] += 1
            if round_idx == 0 and iteration == 0:
                plot_network_with_paths(network, results[network_type]['paths'], clone_positions, results[network_type]['detected_clones'], tuple(np.mean(network, axis=0)), f'{network_type} Network')
    
    for network_type in results.keys():
        print(f"{network_type} Network: {results[network_type]['detections']} detections, {results[network_type]['base_station_reached']} base stations reached out of {num_iterations * num_rounds} total rounds")
        print(f"Average time steps: {results[network_type]['time_steps'] / (num_iterations * num_rounds)}")
        print(f"Average total hops: {results[network_type]['total_hops'] / (num_iterations * num_rounds)}")
        print(f"Total detected cloned nodes: {len(results[network_type]['detected_clones'])}")
        print(f"Total compromised nodes: {results[network_type]['compromised_nodes'] / (num_iterations * num_rounds)}")
        print(f"Base station reached percentage: {(results[network_type]['base_station_reached'] / (num_iterations * num_rounds)) * 100}%")
    
    plot_metrics(results, num_rounds)

def plot_metrics(results, num_rounds):
    network_types = list(results.keys())
    avg_time_steps = [results[network_type]['time_steps'] / num_rounds for network_type in network_types]
    avg_total_hops = [results[network_type]['total_hops'] / num_rounds for network_type in network_types]
    base_station_reached_percentage = [(results[network_type]['base_station_reached'] / num_rounds) * 100 for network_type in network_types]
    avg_compromised_nodes = [results[network_type]['compromised_nodes'] / num_rounds for network_type in network_types]
    total_detections = [results[network_type]['detections'] for network_type in network_types]

    markers = ['o', 's', 'D', '^']  # Different markers for each network type
    
    fig, axs = plt.subplots(5, 1, figsize=(10, 20))

    for i, network_type in enumerate(network_types):
        sns.lineplot(x=range(num_rounds), y=[results[network_type]['time_steps'] / (round + 1) for round in range(num_rounds)], marker=markers[i], ax=axs[0], label=network_type)
    axs[0].set_xlabel('Round')
    axs[0].set_ylabel('Average Time Steps')
    axs[0].set_title('Average Time Steps for Different Network Topologies')

    for i, network_type in enumerate(network_types):
        sns.lineplot(x=range(num_rounds), y=[results[network_type]['total_hops'] / (round + 1) for round in range(num_rounds)], marker=markers[i], ax=axs[1], label=network_type)
    axs[1].set_xlabel('Round')
    axs[1].set_ylabel('Average Total Hops')
    axs[1].set_title('Average Total Hops for Different Network Topologies')

    for i, network_type in enumerate(network_types):
        sns.lineplot(x=range(num_rounds), y=[(results[network_type]['base_station_reached'] / (round + 1)) * 100 for round in range(num_rounds)], marker=markers[i], ax=axs[2], label=network_type)
    axs[2].set_xlabel('Round')
    axs[2].set_ylabel('Base Station Reached Percentage')
    axs[2].set_title('Base Station Reached Percentage for Different Network Topologies')

    for i, network_type in enumerate(network_types):
        sns.lineplot(x=range(num_rounds), y=[results[network_type]['compromised_nodes'] / (round + 1) for round in range(num_rounds)], marker=markers[i], ax=axs[3], label=network_type)
    axs[3].set_xlabel('Round')
    axs[3].set_ylabel('Average Compromised Nodes')
    axs[3].set_title('Average Compromised Nodes for Different Network Topologies')

    for i, network_type in enumerate(network_types):
        sns.lineplot(x=range(num_rounds), y=[results[network_type]['detections'] for _ in range(num_rounds)], marker=markers[i], ax=axs[4], label=network_type)
    axs[4].set_xlabel('Round')
    axs[4].set_ylabel('Total Detections')
    axs[4].set_title('Total Detections for Different Network Topologies')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_simulation(num_iterations=1, num_rounds=100)
