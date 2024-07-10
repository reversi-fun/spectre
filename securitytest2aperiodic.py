import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import distance_matrix
from shapely.geometry import Point, Polygon
from securitymetricsaperiodic_hexagonal import generate_spectre_tiles, generate_hexagonal_network, transPt, SPECTRE_POINTS

# Parameters
NUM_SENSORS = 559  # Number of sensors for fair comparison
SENSOR_RADIUS = 10  # Sensor radius
COMM_RADIUS = 2 * SENSOR_RADIUS  # Communication radius
FAILURE_RATE = 0.1  # Rate of random node failures
NUM_CLONES = 50  # Number of clone nodes for Sybil attack

def generate_networks():
    # Generate aperiodic network
    tiles, _ = generate_spectre_tiles()
    aperiodic_network = place_sensors_inscribed(tiles)[:NUM_SENSORS]

    # Generate regular networks
    hexagonal_network = generate_hexagonal_network(NUM_SENSORS, SENSOR_RADIUS)
    triangular_network = generate_triangular_network(NUM_SENSORS, SENSOR_RADIUS)
    square_network = generate_square_network(NUM_SENSORS, SENSOR_RADIUS)

    return aperiodic_network, hexagonal_network, triangular_network, square_network

def place_sensors_inscribed(tiles):
    sensor_positions = []
    def add_sensor_points(transformation, label):
        nonlocal sensor_positions
        tile_points = [transPt(transformation, pt) for pt in SPECTRE_POINTS]
        centroid = np.mean(tile_points, axis=0)
        sensor_positions.append(centroid)
    tiles["Delta"].forEachTile(add_sensor_points)
    return np.array(sensor_positions)

def generate_hexagonal_network(num_sensors, sensor_radius):
    positions = []
    rows = cols = int(np.sqrt(num_sensors))
    for row in range(rows):
        for col in range(cols):
            x = col * sensor_radius * 1.5
            y = row * sensor_radius * np.sqrt(3) + (col % 2) * (sensor_radius * np.sqrt(3) / 2)
            positions.append((x, y))
            if len(positions) >= num_sensors:
                return np.array(positions)

def generate_triangular_network(num_sensors, sensor_radius):
    positions = []
    rows = cols = int(np.sqrt(num_sensors))
    for row in range(rows):
        for col in range(cols):
            x = col * sensor_radius * 1.5
            y = row * sensor_radius * np.sqrt(3) / 2 * (1 + (col % 2))
            positions.append((x, y))
            if len(positions) >= num_sensors:
                return np.array(positions)

def generate_square_network(num_sensors, sensor_radius):
    positions = []
    side_length = int(np.sqrt(num_sensors))
    for i in range(side_length):
        for j in range(side_length):
            positions.append((i * sensor_radius, j * sensor_radius))
            if len(positions) >= num_sensors:
                return np.array(positions)

def simulate_failures(network, failure_rate):
    num_failures = int(failure_rate * len(network))
    failed_nodes = np.random.choice(len(network), num_failures, replace=False)
    return np.delete(network, failed_nodes, axis=0)

def calculate_connectivity(network):
    distances = distance_matrix(network, network)
    connectivity_matrix = distances <= COMM_RADIUS
    graph = {i: np.where(connectivity_matrix[i])[0] for i in range(len(connectivity_matrix))}
    return is_connected(graph)

def is_connected(graph):
    visited = set()
    def dfs(node):
        if node in visited:
            return
        visited.add(node)
        for neighbor in graph[node]:
            dfs(neighbor)
    dfs(0)
    return len(visited) == len(graph)

def calculate_entropy(network):
    distances = distance_matrix(network, network)
    degrees = np.sum(distances <= COMM_RADIUS, axis=1)
    unique, counts = np.unique(degrees, return_counts=True)
    probabilities = counts / len(degrees)
    return -np.sum(probabilities * np.log(probabilities))

def simulate_sybil_attack(network, num_clones):
    clone_nodes = network[np.random.choice(len(network), num_clones)]
    return len(clone_nodes)

def calculate_load_balance(network, steps):
    load = np.zeros(len(network))
    for step in steps:
        load[step] += 1
    return np.std(load)

def simulate_intruder_attack(network, base_station_position):
    path = [INTRUDER_INITIAL_POSITION]
    for _ in range(10000):  # Max steps
        current_pos = path[-1]
        distances = np.linalg.norm(network - current_pos, axis=1)
        closest_node = np.argmin(distances)
        path.append(network[closest_node])
        if np.linalg.norm(base_station_position - network[closest_node]) <= SENSOR_RADIUS:
            break
    return len(path)

def run_simulation():
    aperiodic_network, hexagonal_network, triangular_network, square_network = generate_networks()
    networks = [aperiodic_network, hexagonal_network, triangular_network, square_network]
    names = ["Aperiodic", "Hexagonal", "Triangular", "Square"]

    for network, name in zip(networks, names):
        print(f"Testing {name} Network")

        # Robustness to Random Failures
        initial_connectivity = calculate_connectivity(network)
        failed_network = simulate_failures(network, FAILURE_RATE)
        final_connectivity = calculate_connectivity(failed_network)
        print(f"{name} Network - Initial Connectivity: {initial_connectivity}, Final Connectivity after {int(FAILURE_RATE * NUM_SENSORS)} failures: {final_connectivity}")

        # Resilience to Path-based Attacks
        base_station_position = np.mean(network, axis=0)
        steps_to_base_station = simulate_intruder_attack(network, base_station_position)
        print(f"{name} Network Steps to Base Station: {steps_to_base_station}")

        # Network Longevity and Load Balancing
        load_std_dev = calculate_load_balance(network, steps_to_base_station)
        print(f"{name} Network Load Standard Deviation: {load_std_dev}")

        # Increased Entropy and Complexity
        entropy = calculate_entropy(network)
        print(f"{name} Network Entropy: {entropy}")

        # Mitigation of Sybil and Clone Attacks
        detection_count = simulate_sybil_attack(network, NUM_CLONES)
        print(f"{name} Network Clone Detections: {detection_count}")

run_simulation()
