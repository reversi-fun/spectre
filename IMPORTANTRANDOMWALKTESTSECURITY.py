import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon
from securitymetricsaperiodic_hexagonal import generate_aperiodic_network, generate_hexagonal_network, transPt, SPECTRE_POINTS
import random

# Parameters
SENSOR_RADIUS = 10
HOP_DISTANCE = SENSOR_RADIUS

def calculate_pairwise_distances(sensor_positions):
    num_sensors = len(sensor_positions)
    distances = []
    for i in range(num_sensors):
        for j in range(i + 1, num_sensors):
            distance = np.linalg.norm(np.array(sensor_positions[i]) - np.array(sensor_positions[j]))
            distances.append(distance)
    return distances

def create_distance_histogram(distances, num_bins=30):
    histogram, bin_edges = np.histogram(distances, bins=num_bins, density=True)
    return histogram, bin_edges

def calculate_probability_distribution(histogram):
    probability_distribution = histogram / np.sum(histogram)
    return probability_distribution

def calculate_entropy(probability_distribution):
    entropy = -np.sum(probability_distribution * np.log(probability_distribution + 1e-9))  # Adding a small value to avoid log(0)
    return entropy

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

def simulate_intruder_attack(network, intruder_position, base_station_position, network_type):
    path = [intruder_position]
    time_steps = 0
    visited_nodes = set()
    pattern_found = False
    hops = 0
    while not has_reached_base_station(intruder_position, base_station_position):
        visited_nodes.add(tuple(intruder_position))
        intruder_position, step_time, pattern_found = smart_random_walk(network, intruder_position, visited_nodes, network_type, pattern_found, hops)
        path.append(intruder_position)
        time_steps += step_time
        hops += 1
    return path, time_steps

def smart_random_walk(network, intruder_position, visited_nodes, network_type, pattern_found, hops):
    if not pattern_found:
        return initial_random_walk(network, intruder_position, visited_nodes, network_type, hops)
    else:
        return follow_pattern_walk(network, intruder_position, visited_nodes, network_type, hops)

def initial_random_walk(network, intruder_position, visited_nodes, network_type, hops):
    distances = np.linalg.norm(np.array(network) - np.array(intruder_position), axis=1)
    sorted_indices = np.argsort(distances)
    for idx in sorted_indices:
        nearest_node = network[idx]
        if tuple(nearest_node) not in visited_nodes and distances[idx] <= SENSOR_RADIUS:
            step_time = non_linear_time_function(hops, network_type, pattern_found=False)
            return nearest_node, step_time, detect_pattern(nearest_node, network)
    return intruder_position, 0, False

def follow_pattern_walk(network, intruder_position, visited_nodes, network_type, hops):
    distances = np.linalg.norm(np.array(network) - np.array(intruder_position), axis=1)
    sorted_indices = np.argsort(distances)
    for idx in sorted_indices:
        nearest_node = network[idx]
        if tuple(nearest_node) not in visited_nodes and distances[idx] <= SENSOR_RADIUS:
            step_time = non_linear_time_function(hops, network_type, pattern_found=True)
            return nearest_node, step_time, True
    return intruder_position, 0, True

def non_linear_time_function(hops, network_type, pattern_found):
    # Parameters
    initial_time = 10.0  # Initial time taken for the first hop
    complexity_metric = COMPLEXITY_METRICS[network_type]
    
    if network_type == 'aperiodic':
        # For aperiodic networks, use a slower exponential decay
        time_per_hop = initial_time * (complexity_metric / (hops + 1))
    else:
        if not pattern_found:
            # During exploration, use an exponential decay
            time_per_hop = initial_time * (complexity_metric / np.log1p(hops + 1))
        else:
            # During exploitation, use a faster decay
            time_per_hop = initial_time * (complexity_metric / (2 * np.log1p(hops + 1)))
    
    return time_per_hop

def detect_pattern(current_node, network):
    angles = np.linspace(0, 2 * np.pi, 6, endpoint=False)
    distances = np.linalg.norm(np.array(network) - np.array(current_node), axis=1)
    sorted_distances = np.sort(distances)
    return np.allclose(sorted_distances[:6], sorted_distances[0], atol=0.1)

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

# Complexity metrics for different network types
COMPLEXITY_METRICS = {}

def run_simulation(num_iterations=3):
    random.seed()  # Ensure randomness in each simulation run

    global SENSOR_RADIUS
    global COMPLEXITY_METRICS

    num_sensors_per_iteration = [9, 71, 559, 4401]
    num_sensors = num_sensors_per_iteration[num_iterations - 1]

    # Generate networks
    aperiodic_network = generate_aperiodic_network(SENSOR_RADIUS, num_sensors, num_iterations)
    hexagonal_network = generate_hexagonal_network(num_sensors, SENSOR_RADIUS)
    triangular_network = generate_triangular_network(num_sensors, SENSOR_RADIUS)
    square_network = generate_square_network(num_sensors, SENSOR_RADIUS)

    # Calculate entropy for each network
    aperiodic_distances = calculate_pairwise_distances(aperiodic_network)
    hexagonal_distances = calculate_pairwise_distances(hexagonal_network)
    triangular_distances = calculate_pairwise_distances(triangular_network)
    square_distances = calculate_pairwise_distances(square_network)
    
    aperiodic_histogram, _ = create_distance_histogram(aperiodic_distances)
    hexagonal_histogram, _ = create_distance_histogram(hexagonal_distances)
    triangular_histogram, _ = create_distance_histogram(triangular_distances)
    square_histogram, _ = create_distance_histogram(square_distances)
    
    aperiodic_probability_distribution = calculate_probability_distribution(aperiodic_histogram)
    hexagonal_probability_distribution = calculate_probability_distribution(hexagonal_histogram)
    triangular_probability_distribution = calculate_probability_distribution(triangular_histogram)
    square_probability_distribution = calculate_probability_distribution(square_histogram)
    
    aperiodic_entropy = calculate_entropy(aperiodic_probability_distribution)
    hexagonal_entropy = calculate_entropy(hexagonal_probability_distribution)
    triangular_entropy = calculate_entropy(triangular_probability_distribution)
    square_entropy = calculate_entropy(square_probability_distribution)

    # Print entropy values
    print(f"Aperiodic Network Entropy: {aperiodic_entropy}")
    print(f"Hexagonal Network Entropy: {hexagonal_entropy}")
    print(f"Triangular Network Entropy: {triangular_entropy}")
    print(f"Square Network Entropy: {square_entropy}")

    # Assign complexity metrics based on entropy
    COMPLEXITY_METRICS = {
        'aperiodic': aperiodic_entropy,
        'hexagonal': hexagonal_entropy,
        'triangular': triangular_entropy,
        'square': square_entropy
    }

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

    aperiodic_path, aperiodic_time = simulate_intruder_attack(aperiodic_network, intruder_initial_position, aperiodic_base_station, 'aperiodic')
    hexagonal_path, hexagonal_time = simulate_intruder_attack(hexagonal_network, intruder_initial_position, hexagonal_base_station, 'hexagonal')
    triangular_path, triangular_time = simulate_intruder_attack(triangular_network, intruder_initial_position, triangular_base_station, 'triangular')
    square_path, square_time = simulate_intruder_attack(square_network, intruder_initial_position, square_base_station, 'square')

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
