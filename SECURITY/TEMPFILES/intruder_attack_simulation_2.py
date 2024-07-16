# intruder_attack_simulation.py

import numpy as np
import matplotlib.pyplot as plt
from network_generation import generate_aperiodic_network, generate_hexagonal_network, generate_triangular_network, generate_square_network
import random

# Parameters
SENSOR_RADIUS = 10
HOP_DISTANCE = SENSOR_RADIUS * 2
MAX_HOPS = 1000

def simulate_intruder_attack(network, intruder_position, base_station_position, network_type):
    path = [intruder_position]
    time_steps = 0
    visited_nodes = set()
    is_aperiodic = network_type == 'aperiodic'
    hops = 0
    first_hop = True

    while not has_reached_base_station(intruder_position, base_station_position) and hops < MAX_HOPS:
        visited_nodes.add(tuple(intruder_position))
        intruder_position, step_time, hop_distance, pattern_found = smart_random_walk(network, intruder_position, visited_nodes, is_aperiodic, first_hop)
        path.append(intruder_position)
        time_steps += step_time
        hops += 1
        first_hop = False

        print(f"New intruder position: {intruder_position}, Step time: {step_time}, Hop distance: {hop_distance}, Pattern found: {pattern_found}")
        
        if hop_distance > SENSOR_RADIUS:
            print(f"Flagged hop: {hop_distance}")

    return path, time_steps, hops

def smart_random_walk(network, intruder_position, visited_nodes, is_aperiodic, first_hop):
    distances = np.linalg.norm(np.array(network) - np.array(intruder_position), axis=1)
    sorted_indices = np.argsort(distances)
    for idx in sorted_indices:
        nearest_node = network[idx]
        hop_distance = np.linalg.norm(np.array(nearest_node) - np.array(intruder_position))
        if tuple(nearest_node) not in visited_nodes and (first_hop or hop_distance <= SENSOR_RADIUS):
            step_time = calculate_time_step(nearest_node, intruder_position, network)
            pattern_found = detect_pattern(nearest_node, network)
            return nearest_node, step_time, hop_distance, pattern_found
    # If no new node found within range, return to a visited node
    for idx in sorted_indices:
        nearest_node = network[idx]
        hop_distance = np.linalg.norm(np.array(nearest_node) - np.array(intruder_position))
        if hop_distance <= SENSOR_RADIUS:
            step_time = calculate_time_step(nearest_node, intruder_position, network)
            pattern_found = detect_pattern(nearest_node, network)
            return nearest_node, step_time, hop_distance, pattern_found
    return intruder_position, 0, 0, False

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
        sensor_circle = plt.Circle(node, SENSOR_RADIUS, color='yellow', alpha=0.2)
        comm_circle = plt.Circle(node, SENSOR_RADIUS * 2, color='purple', alpha=0.1)
        ax.add_artist(sensor_circle)
        ax.add_artist(comm_circle)
        plt.plot(node[0], node[1], 'bo', markersize=2)
    
    # Plot base station
    plt.plot(base_station_position[0], base_station_position[1], 'go', markersize=10, label='Base Station')
    
    # Plot intruder path
    for i in range(1, len(path)):
        linestyle = 'dotted' if i > 0 and np.linalg.norm(path[i] - path[i-1]) < HOP_DISTANCE else 'solid'
        plt.plot(path[i-1:i+1, 0], path[i-1:i+1, 1], 'r-', linewidth=1, linestyle=linestyle)
        plt.arrow(path[i-1][0], path[i-1][1], path[i][0]-path[i-1][0], path[i][1]-path[i-1][1], head_width=2, head_length=2, fc='r', ec='r')

    plt.title(title)
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.legend()
    plt.grid(True)
    plt.axis('equal')
    plt.show()

def run_simulation():
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

    for network_type, network, base_station in zip(network_types, networks, base_stations):
        intruder_initial_position = (random.uniform(-200, 200), random.uniform(-200, 200))
        path, time_steps, hops = simulate_intruder_attack(network, intruder_initial_position, base_station, network_type)
        
        print(f"{network_type} Network - Total hops: {hops}, Time steps: {time_steps}")
        plot_network_with_path(network, path, base_station, f'{network_type} Network')

if __name__ == "__main__":
    run_simulation()
