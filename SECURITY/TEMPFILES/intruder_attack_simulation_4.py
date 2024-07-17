# File: intruder_attack_simulation.py

import numpy as np
import matplotlib.pyplot as plt
from network_generation import generate_aperiodic_network, generate_hexagonal_network, generate_triangular_network, generate_square_network
import random

# Parameters
SENSOR_RADIUS = 10
<<<<<<< Updated upstream
COMMUNICATION_RANGE = SENSOR_RADIUS * 2
COMPROMISED_PERCENTAGE = 0.01
=======
HOP_DISTANCE = SENSOR_RADIUS * 2
>>>>>>> Stashed changes

def simulate_intruder_attack(network, compromised_positions, base_station_position, network_type):
    paths = []
    time_steps = 0
    total_hops = 0
    visited_nodes = set()
    reached_base = False
    is_aperiodic = network_type == 'aperiodic'
<<<<<<< Updated upstream

    for intruder_position in compromised_positions:
        path = [intruder_position]
        while not has_reached_base_station(intruder_position, base_station_position):
            visited_nodes.add(tuple(intruder_position))
            next_position, step_time, pattern_found = smart_random_walk(network, intruder_position, visited_nodes, is_aperiodic, base_station_position)
            if np.linalg.norm(np.array(next_position) - np.array(intruder_position)) > COMMUNICATION_RANGE:
                print(f"Invalid hop detected from {intruder_position} to {next_position}, stopping simulation for this node.")
                break
            intruder_position = next_position
            path.append(intruder_position)
            time_steps += step_time
            total_hops += 1
        if has_reached_base_station(intruder_position, base_station_position):
            reached_base = True
        paths.append(path)
    
    return paths, time_steps, total_hops, reached_base

def smart_random_walk(network, intruder_position, visited_nodes, is_aperiodic, base_station_position):
=======
    while not has_reached_base_station(intruder_position, base_station_position):
        visited_nodes.add(tuple(intruder_position))
        intruder_position, step_time, reachable = smart_random_walk(network, intruder_position, visited_nodes, is_aperiodic)
        if not reachable:
            break
        path.append(intruder_position)
        time_steps += step_time
    return path, time_steps

def smart_random_walk(network, intruder_position, visited_nodes, is_aperiodic):
>>>>>>> Stashed changes
    distances = np.linalg.norm(np.array(network) - np.array(intruder_position), axis=1)
    sorted_indices = np.argsort(distances)
    for idx in sorted_indices:
        nearest_node = network[idx]
        if tuple(nearest_node) not in visited_nodes:
<<<<<<< Updated upstream
            step_time = calculate_time_step(nearest_node, intruder_position, network)
            pattern_found = detect_pattern(nearest_node, network)
            angle_to_base = calculate_angle_to_base(nearest_node, base_station_position)
            if angle_to_base <= 45 or angle_to_base >= 315:
                return nearest_node, step_time, pattern_found
    return intruder_position, 0, False

def calculate_angle_to_base(nearest_node, base_station_position):
    vector = np.array(base_station_position) - np.array(nearest_node)
    angle = np.degrees(np.arctan2(vector[1], vector[0]))
    if angle < 0:
        angle += 360
    return angle
=======
            step_time = calculate_time_step(nearest_node, intruder_position, network, is_aperiodic)
            return nearest_node, step_time, True
    return intruder_position, 0, False
>>>>>>> Stashed changes

def calculate_time_step(nearest_node, current_node, network, is_aperiodic):
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

<<<<<<< Updated upstream
def detect_pattern(current_node, network):
    unique_angles, unique_distances = get_unique_angles_distances(current_node, network)
    
    max_angles = 6
    max_distances = 2
    
    return len(unique_angles) <= max_angles and len(unique_distances) <= max_distances

def has_reached_base_station(position, base_station_position):
    return np.linalg.norm(np.array(position) - np.array(base_station_position)) <= SENSOR_RADIUS

def plot_network_with_paths(network, paths, base_station_position, title):
=======
def has_reached_base_station(position, base_station_position):
    return np.linalg.norm(np.array(position) - np.array(base_station_position)) <= SENSOR_RADIUS

def plot_network_with_path(network, path, base_station_position, title):
>>>>>>> Stashed changes
    fig, ax = plt.subplots()
    network = np.array(network)
    
    # Plot sensors and their ranges
    for node in network:
        sensor_circle = plt.Circle(node, SENSOR_RADIUS, color='blue', alpha=0.2)
        ax.add_artist(sensor_circle)
        plt.plot(node[0], node[1], 'bo', markersize=2, label='Uncompromised Nodes' if 'Uncompromised Nodes' not in plt.gca().get_legend_handles_labels()[1] else "")
    
    # Plot base station
    plt.plot(base_station_position[0], base_station_position[1], 'go', markersize=10, label='Base Station')
    
    # Plot intruder paths
    for path in paths:
        path = np.array(path)
        for i in range(1, len(path)):
            plt.plot(path[i-1:i+1, 0], path[i-1:i+1, 1], 'r-', linewidth=1, label='Compromised Nodes' if i == 1 and 'Compromised Nodes' not in plt.gca().get_legend_handles_labels()[1] else "")
            plt.arrow(path[i-1][0], path[i-1][1], path[i][0]-path[i-1][0], path[i][1]-path[i-1][1], head_width=2, head_length=2, fc='r', ec='r')

    plt.title(title)
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.legend()
    plt.grid(True)
    plt.axis('equal')
    plt.show()

<<<<<<< Updated upstream
def run_simulation(num_iterations=1, num_rounds=10):
=======
def run_simulation(num_iterations=10):
>>>>>>> Stashed changes
    random.seed()  # Ensure randomness in each simulation run

    global SENSOR_RADIUS
    num_sensors = 559  # Example value
    sensor_radius = SENSOR_RADIUS

    # Generate networks
    aperiodic_network = generate_aperiodic_network(sensor_radius, num_sensors, 3)
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
    
<<<<<<< Updated upstream
    results = {network_type: {'time_steps': [], 'total_hops': [], 'compromised_nodes': [], 'reached_base': []} for network_type in network_types}
    
    for round in range(num_rounds):
        compromised_positions = [tuple(network[idx]) for network in networks for idx in np.random.choice(len(network), int(len(network) * COMPROMISED_PERCENTAGE), replace=False)]
        for i in range(num_iterations):
            for network_type, network, base_station in zip(network_types, networks, base_stations):
                paths, time_steps, total_hops, reached_base = simulate_intruder_attack(network, compromised_positions, base_station, network_type)
                results[network_type]['time_steps'].append(time_steps)
                results[network_type]['total_hops'].append(total_hops)
                results[network_type]['compromised_nodes'].append(len(compromised_positions))
                results[network_type]['reached_base'].append(reached_base)
                if round == 0 and i == 0:
                    plot_network_with_paths(network, paths, base_station, f'{network_type} Network')
            print(f"Iteration {i + 1} of round {round + 1} completed.")

    # Calculate average metrics
    avg_metrics = {network_type: {
        'avg_time_steps': np.mean(results[network_type]['time_steps']),
        'avg_total_hops': np.mean(results[network_type]['total_hops']),
        'avg_compromised_nodes': np.mean(results[network_type]['compromised_nodes']),
        'reached_base_percentage': np.mean(results[network_type]['reached_base']) * 100
    } for network_type in network_types}

    # Plot results
    plot_results(avg_metrics)

def plot_results(avg_metrics):
    fig, ax = plt.subplots()
    network_types = list(avg_metrics.keys())
    avg_time_steps = [avg_metrics[network_type]['avg_time_steps'] for network_type in network_types]
    avg_total_hops = [avg_metrics[network_type]['avg_total_hops'] for network_type in network_types]
    avg_compromised_nodes = [avg_metrics[network_type]['avg_compromised_nodes'] for network_type in network_types]
    reached_base_percentage = [avg_metrics[network_type]['reached_base_percentage'] for network_type in network_types]

    width = 0.2  # width of bars
    x = np.arange(len(network_types))

    ax.bar(x - width, avg_time_steps, width, label='Average Time Steps', color='red')
    ax.bar(x, avg_total_hops, width, label='Average Total Hops', color='green')
    ax.bar(x + width, avg_compromised_nodes, width, label='Average Compromised Nodes', color='blue')

    for i in range(len(x)):
        ax.text(x[i], reached_base_percentage[i] + 0.5, f'{reached_base_percentage[i]:.2f}%', ha='center', color='black')

    ax.set_xlabel('Network Topology')
    ax.set_ylabel('Metrics')
    ax.set_title('Average Metrics for Different Network Topologies')
    ax.set_xticks(x)
    ax.set_xticklabels(network_types)
    ax.legend()

=======
    results = {network_type: [] for network_type in network_types}
    
    for i in range(num_iterations):
        for network_type, network, base_station in zip(network_types, networks, base_stations):
            intruder_initial_position = (random.uniform(-200, 200), random.uniform(-200, 200))
            path, time_steps = simulate_intruder_attack(network, intruder_initial_position, base_station, network_type)
            results[network_type].append(time_steps)
            plot_network_with_path(network, path, base_station, f'{network_type} Network')
        print(f"Iteration {i + 1} completed.")

    # Calculate average time steps
    avg_time_steps = {network_type: np.mean(results[network_type]) for network_type in network_types}

    # Plot results
    plot_results(avg_time_steps)

def plot_results(avg_time_steps):
    fig, ax = plt.subplots()
    network_types = list(avg_time_steps.keys())
    avg_times = list(avg_time_steps.values())
    
    ax.bar(network_types, avg_times, color=['red', 'green', 'blue', 'purple'])
    
    ax.set_xlabel('Network Topology')
    ax.set_ylabel('Average Time Steps')
    ax.set_title('Average Time Steps for Different Network Topologies')
    
>>>>>>> Stashed changes
    plt.show()

if __name__ == "__main__":
    run_simulation(num_iterations=1)
