# File: intruder_attack_simulation.py

import numpy as np
import matplotlib.pyplot as plt
from network_generation import generate_aperiodic_network, generate_hexagonal_network, generate_triangular_network, generate_square_network
import random
from scipy.spatial import distance_matrix

# Parameters
SENSOR_RADIUS = 10
HOP_DISTANCE = SENSOR_RADIUS

def simulate_intruder_attack(network, intruder_position, base_station_position, network_type):
    path = [intruder_position]
    time_steps = 0
    visited_nodes = set()
    is_aperiodic = network_type == 'aperiodic'
    
    while not has_reached_base_station(intruder_position, base_station_position):
        visited_nodes.add(tuple(intruder_position))
        intruder_position, step_time, pattern_found = smart_random_walk(network, intruder_position, visited_nodes, is_aperiodic)
        
        if np.linalg.norm(np.array(intruder_position) - np.array(path[-1])) > HOP_DISTANCE:
            intruder_position = path[-1]  # Revert to the last valid position
            intruder_position, step_time, pattern_found = traveling_salesman_step(network, intruder_position, visited_nodes)
            if intruder_position is None:
                print("Intruder could not make a valid hop. Ending simulation.")
                break
        
        path.append(intruder_position)
        time_steps += step_time

    return path, time_steps

def smart_random_walk(network, intruder_position, visited_nodes, is_aperiodic):
    distances = np.linalg.norm(np.array(network) - np.array(intruder_position), axis=1)
    sorted_indices = np.argsort(distances)
    for idx in sorted_indices:
        nearest_node = network[idx]
        if tuple(nearest_node) not in visited_nodes:
            step_time = calculate_time_step(nearest_node, intruder_position, network)
            pattern_found = detect_pattern(nearest_node, network)
            return nearest_node, step_time, pattern_found
    return intruder_position, 0, False

def traveling_salesman_step(network, current_position, visited_nodes):
    remaining_nodes = [node for node in network if tuple(node) not in visited_nodes]
    if not remaining_nodes:
        return None, 0, False
    
    distances = distance_matrix([current_position], remaining_nodes)
    nearest_idx = np.argmin(distances)
    nearest_node = remaining_nodes[nearest_idx]
    
    step_time = calculate_time_step(nearest_node, current_position, network)
    pattern_found = detect_pattern(nearest_node, network)
    
    return nearest_node, step_time, pattern_found

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
    return len(unique_angles) <= 3 and len(unique_distances) <= 3

def has_reached_base_station(position, base_station_position):
    return np.linalg.norm(np.array(position) - np.array(base_station_position)) <= SENSOR_RADIUS

def plot_network_with_path(network, path, base_station_position, title):
    fig, ax = plt.subplots()
    network = np.array(network)
    path = np.array(path)
    
    # Plot sensors and their ranges
    for node in network:
        sensor_circle = plt.Circle(node, SENSOR_RADIUS, color='blue', alpha=0.2)
        ax.add_artist(sensor_circle)
        plt.plot(node[0], node[1], 'bo', markersize=2)
    
    # Plot base station
    plt.plot(base_station_position[0], base_station_position[1], 'go', markersize=10, label='Base Station')
    
    # Plot intruder path
    for i in range(1, len(path)):
        plt.plot(path[i-1:i+1, 0], path[i-1:i+1, 1], 'r-', linewidth=1)
        plt.arrow(path[i-1][0], path[i-1][1], path[i][0]-path[i-1][0], path[i][1]-path[i-1][1], head_width=2, head_length=2, fc='r', ec='r')

    plt.title(title)
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.legend()
    plt.grid(True)
    plt.axis('equal')
    plt.show()

def run_simulation(num_iterations=100):
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
    
    results = {network_type: [] for network_type in network_types}
    paths = {network_type: [] for network_type in network_types}
    
    for i in range(num_iterations):
        for network_type, network, base_station in zip(network_types, networks, base_stations):
            intruder_initial_position = (random.uniform(-200, 200), random.uniform(-200, 200))
            path, time_steps = simulate_intruder_attack(network, intruder_initial_position, base_station, network_type)
            results[network_type].append(time_steps)
            if i == 0:  # Save path for the first iteration
                paths[network_type] = path
        print(f"Iteration {i + 1} completed.")

    # Calculate average time steps
    avg_time_steps = {network_type: np.mean(results[network_type]) for network_type in network_types}

    # Plot results
    plot_results(avg_time_steps)
    
    # Plot paths for the first round
    for network_type, network, base_station in zip(network_types, networks, base_stations):
        plot_network_with_path(network, paths[network_type], base_station, f'{network_type} Network - First Round Intruder Path')

def plot_results(avg_time_steps):
    fig, ax = plt.subplots()
    network_types = list(avg_time_steps.keys())
    avg_times = list(avg_time_steps.values())
    
    ax.bar(network_types, avg_times, color=['red', 'green', 'blue', 'purple'])
    
    ax.set_xlabel('Network Topology')
    ax.set_ylabel('Average Time Steps')
    ax.set_title('Average Time Steps for Different Network Topologies')
    
    plt.show()

if __name__ == "__main__":
    run_simulation(num_iterations=10)
