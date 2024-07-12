import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon
from securitymetricsaperiodic_hexagonal import generate_aperiodic_network, generate_hexagonal_network, transPt, SPECTRE_POINTS
import random

# Parameters
SENSOR_RADIUS = 10
HOP_DISTANCE = SENSOR_RADIUS / 3

def generate_triangular_network(num_sensors, sensor_radius):
    sensor_positions = []
    row = 0
    col = 0
    y_offset = np.sqrt(3) * sensor_radius
    x_offset = 1.5 * sensor_radius
    while len(sensor_positions) < num_sensors:
        x = col * x_offset
        y = row * y_offset
        sensor_positions.append((x, y))
        col += 1
        if col * x_offset > np.sqrt(num_sensors) * x_offset:
            row += 1
            if row % 2 == 0:
                col = 0
            else:
                col = 0.5
    return sensor_positions[:num_sensors]

def generate_square_network(num_sensors, sensor_radius):
    sensor_positions = []
    side_length = int(np.ceil(np.sqrt(num_sensors)))
    x_offset = sensor_radius
    y_offset = sensor_radius
    for i in range(side_length):
        for j in range(side_length):
            sensor_positions.append((i * x_offset, j * y_offset))
            if len(sensor_positions) >= num_sensors:
                break
        if len(sensor_positions) >= num_sensors:
            break
    return sensor_positions[:num_sensors]

def simulate_intruder_attack(network, intruder_position, base_station_position, is_aperiodic=False):
    path = [intruder_position]
    time_steps = 0
    visited_nodes = set()
    while not has_reached_base_station(intruder_position, base_station_position):
        visited_nodes.add(tuple(intruder_position))
        intruder_position, step_time = smart_random_walk(network, intruder_position, visited_nodes, is_aperiodic)
        path.append(intruder_position)
        time_steps += step_time
    return path, time_steps

def smart_random_walk(network, intruder_position, visited_nodes, is_aperiodic):
    distances = np.linalg.norm(np.array(network) - np.array(intruder_position), axis=1)
    sorted_indices = np.argsort(distances)
    for idx in sorted_indices:
        nearest_node = network[idx]
        if tuple(nearest_node) not in visited_nodes:
            step_time = calculate_time_step(nearest_node, intruder_position, network, is_aperiodic)
            return nearest_node, step_time
    return intruder_position, 0

def calculate_time_step(nearest_node, current_node, network, is_aperiodic):
    distance = np.linalg.norm(np.array(nearest_node) - np.array(current_node))
    unique_angles, unique_distances = get_unique_angles_distances(current_node, network)
    complexity_factor = len(unique_angles) + len(unique_distances)
    
    if is_aperiodic:
        complexity_factor *= 1.0  # Adjust complexity factor for aperiodic networks
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

def has_reached_base_station(position, base_station_position):
    return np.linalg.norm(np.array(position) - np.array(base_station_position)) <= SENSOR_RADIUS

def plot_path(path, network, title, base_station_position):
    plt.figure(figsize=(10, 10))
    for node in network:
        plt.plot(node[0], node[1], 'bo', markersize=2)
    path = np.array(path)
    plt.plot(path[:, 0], path[:, 1], 'r-')
    plt.plot(base_station_position[0], base_station_position[1], 'go', markersize=5)
    plt.title(title)
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.grid(True)
    plt.show()

def run_simulation(num_iterations=3):
    random.seed()  # Ensure randomness in each simulation run

    global SENSOR_RADIUS

    num_sensors_per_iteration = [9, 71, 559, 4401]
    num_sensors = num_sensors_per_iteration[num_iterations - 1]

    # Generate networks
    aperiodic_network = generate_aperiodic_network(SENSOR_RADIUS, num_sensors, num_iterations)
    hexagonal_network = generate_hexagonal_network(num_sensors, SENSOR_RADIUS)
    triangular_network = generate_triangular_network(num_sensors, SENSOR_RADIUS)
    square_network = generate_square_network(num_sensors, SENSOR_RADIUS)

    # Ensure all networks use the same number of sensors
    aperiodic_network = aperiodic_network[:num_sensors]
    hexagonal_network = hexagonal_network[:num_sensors]
    triangular_network = triangular_network[:num_sensors]
    square_network = square_network[:num_sensors]

    # Check if all networks have the same number of sensors
    assert len(aperiodic_network) == num_sensors, f"Aperiodic network sensors: {len(aperiodic_network)}"
    assert len(hexagonal_network) == num_sensors, f"Hexagonal network sensors: {len(hexagonal_network)}"
    assert len(triangular_network) == num_sensors, f"Triangular network sensors: {len(triangular_network)}"
    assert len(square_network) == num_sensors, f"Square network sensors: {len(square_network)}"

    # Random initial position for intruder
    intruder_initial_position = (
        random.uniform(-200, 200), random.uniform(-200, 200)
    )

    aperiodic_center = np.mean(aperiodic_network, axis=0)
    hexagonal_center = np.mean(hexagonal_network, axis=0)
    triangular_center = np.mean(triangular_network, axis=0)
    square_center = np.mean(square_network, axis=0)

    aperiodic_base_station = tuple(aperiodic_center)
    hexagonal_base_station = tuple(hexagonal_center)
    triangular_base_station = tuple(triangular_center)
    square_base_station = tuple(square_center)

    aperiodic_path, aperiodic_time = simulate_intruder_attack(aperiodic_network, intruder_initial_position, aperiodic_base_station, is_aperiodic=True)
    hexagonal_path, hexagonal_time = simulate_intruder_attack(hexagonal_network, intruder_initial_position, hexagonal_base_station, is_aperiodic=False)
    triangular_path, triangular_time = simulate_intruder_attack(triangular_network, intruder_initial_position, triangular_base_station, is_aperiodic=False)
    square_path, square_time = simulate_intruder_attack(square_network, intruder_initial_position, square_base_station, is_aperiodic=False)

    aperiodic_time_per_hop = aperiodic_time / len(aperiodic_path)
    hexagonal_time_per_hop = hexagonal_time / len(hexagonal_path)
    triangular_time_per_hop = triangular_time / len(triangular_path)
    square_time_per_hop = square_time / len(square_path)

    print(f"Total number of sensors: {num_sensors}")
    print("Aperiodic Network Path Length:", len(aperiodic_path), "Time Steps:", aperiodic_time, "Time per Hop:", aperiodic_time_per_hop)
    print("Hexagonal Network Path Length:", len(hexagonal_path), "Time Steps:", hexagonal_time, "Time per Hop:", hexagonal_time_per_hop)
    print("Triangular Network Path Length:", len(triangular_path), "Time Steps:", triangular_time, "Time per Hop:", triangular_time_per_hop)
    print("Square Network Path Length:", len(square_path), "Time Steps:", square_time, "Time per Hop:", square_time_per_hop)

    plot_path(aperiodic_path, aperiodic_network, "Intruder Path in Aperiodic Network", aperiodic_base_station)
    plot_path(hexagonal_path, hexagonal_network, "Intruder Path in Hexagonal Network", hexagonal_base_station)
    plot_path(triangular_path, triangular_network, "Intruder Path in Triangular Network", triangular_base_station)
    plot_path(square_path, square_network, "Intruder Path in Square Network", square_base_station)

run_simulation(num_iterations=3)
