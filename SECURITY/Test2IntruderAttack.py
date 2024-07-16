# File: clone_attack_simulation.py

import numpy as np
import matplotlib.pyplot as plt
from network_generation import generate_aperiodic_network, generate_hexagonal_network, generate_triangular_network, generate_square_network
import random

# Parameters
SENSOR_RADIUS = 10
COMMUNICATION_RANGE = SENSOR_RADIUS * 2
CLONE_PERCENTAGE = 0.01

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

def simulate_clone_attack(network, clone_positions):
    detections = 0
    paths = []
    
    for clone_position in clone_positions:
        path = [clone_position]
        if detect_clone_via_random_walk(network, clone_position, path):
            detections += 1
        paths.append(path)
    
    return detections, paths

def detect_clone_via_random_walk(network, start_position, path):
    visited_nodes = set()
    current_position = start_position
    detection_found = False
    
    while len(path) < 100:  # Arbitrary step limit to prevent infinite loops
        visited_nodes.add(tuple(current_position))
        next_position = random_walk_step(network, current_position, visited_nodes)
        if next_position is None:
            break
        path.append(next_position)
        if detect_clone(current_position, next_position):
            detection_found = True
            break
        current_position = next_position
    
    return detection_found

def random_walk_step(network, current_position, visited_nodes):
    distances = np.linalg.norm(np.array(network) - np.array(current_position), axis=1)
    sorted_indices = np.argsort(distances)
    for idx in sorted_indices:
        nearest_node = network[idx]
        if tuple(nearest_node) not in visited_nodes and np.linalg.norm(nearest_node - current_position) <= COMMUNICATION_RANGE:
            return nearest_node
    return None

def detect_clone(current_position, next_position):
    # Implement a more sophisticated detection mechanism here if needed
    return np.linalg.norm(np.array(current_position) - np.array(next_position)) > SENSOR_RADIUS

def plot_network_with_paths(network, paths, clone_positions, title):
    fig, ax = plt.subplots()
    network = np.array(network)
    
    # Plot sensors and their ranges
    for node in network:
        sensor_circle = plt.Circle(node, SENSOR_RADIUS, color='blue', alpha=0.2)
        ax.add_artist(sensor_circle)
        plt.plot(node[0], node[1], 'bo', markersize=2, label='Uncompromised Nodes' if 'Uncompromised Nodes' not in plt.gca().get_legend_handles_labels()[1] else "")
    
    # Plot cloned nodes
    for pos in clone_positions:
        plt.plot(pos[0], pos[1], 'ro', markersize=5, label='Cloned Nodes' if 'Cloned Nodes' not in plt.gca().get_legend_handles_labels()[1] else "")
    
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

def run_simulation(num_sensors=559, num_iterations=10):
    sensor_radius = SENSOR_RADIUS
    networks = generate_networks(sensor_radius, num_sensors)
    results = {network_type: {'detections': 0, 'paths': []} for network_type in networks.keys()}
    
    for network_type, network in networks.items():
        clone_positions = [tuple(network[idx]) for idx in np.random.choice(len(network), int(len(network) * CLONE_PERCENTAGE), replace=False)]
        for _ in range(num_iterations):
            detections, paths = simulate_clone_attack(network, clone_positions)
            results[network_type]['detections'] += detections
            results[network_type]['paths'].extend(paths)
        plot_network_with_paths(network, results[network_type]['paths'], clone_positions, f'{network_type} Network')
    
    for network_type in results.keys():
        print(f"{network_type} Network: {results[network_type]['detections']} detections out of {num_iterations * len(clone_positions)} clones")

if __name__ == "__main__":
    run_simulation()
