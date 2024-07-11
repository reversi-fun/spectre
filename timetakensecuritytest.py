import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon
from securitymetricsaperiodic_hexagonal import generate_spectre_tiles, generate_hexagonal_network, transPt, SPECTRE_POINTS

# Parameters
NUM_SENSORS = 559
SENSOR_RADIUS = 10
INTRUDER_INITIAL_POSITION = (100, -100)
HOP_DISTANCE = SENSOR_RADIUS

def generate_aperiodic_network(sensor_radius, num_sensors):
    tiles, _ = generate_spectre_tiles()
    sensor_positions = place_sensors_inscribed(tiles)
    return sensor_positions[:num_sensors]

def place_sensors_inscribed(tiles):
    sensor_positions = []
    def add_sensor_points(transformation, label):
        nonlocal sensor_positions
        tile_points = [transPt(transformation, pt) for pt in SPECTRE_POINTS]
        centroid = np.mean(tile_points, axis=0)
        sensor_positions.append(tuple(centroid))
    tiles["Delta"].forEachTile(add_sensor_points)
    return sensor_positions

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
    return sensor_positions

def generate_square_network(num_sensors, sensor_radius):
    sensor_positions = []
    side_length = int(np.sqrt(num_sensors))
    x_offset = sensor_radius
    y_offset = sensor_radius
    for i in range(side_length):
        for j in range(side_length):
            sensor_positions.append((i * x_offset, j * y_offset))
            if len(sensor_positions) >= num_sensors:
                break
        if len(sensor_positions) >= num_sensors:
            break
    return sensor_positions

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
    if is_aperiodic:
        return smart_random_walk_aperiodic(network, intruder_position, visited_nodes)
    else:
        return smart_random_walk_regular(network, intruder_position, visited_nodes)

def smart_random_walk_regular(network, intruder_position, visited_nodes):
    distances = np.linalg.norm(np.array(network) - np.array(intruder_position), axis=1)
    sorted_indices = np.argsort(distances)
    for idx in sorted_indices:
        nearest_node = network[idx]
        if tuple(nearest_node) not in visited_nodes:
            step_time = distances[idx] / SENSOR_RADIUS  # assuming uniform time per hop
            return nearest_node, step_time
    return intruder_position, 0

def smart_random_walk_aperiodic(network, intruder_position, visited_nodes):
    distances = np.linalg.norm(np.array(network) - np.array(intruder_position), axis=1)
    sorted_indices = np.argsort(distances)
    for idx in sorted_indices:
        nearest_node = network[idx]
        if tuple(nearest_node) not in visited_nodes:
            step_time = distances[idx] / SENSOR_RADIUS
            return nearest_node, step_time
    return intruder_position, 0

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

def run_simulation():
    global SENSOR_RADIUS

    aperiodic_network = generate_aperiodic_network(SENSOR_RADIUS, NUM_SENSORS)
    hexagonal_network = generate_hexagonal_network(NUM_SENSORS, SENSOR_RADIUS)
    triangular_network = generate_triangular_network(NUM_SENSORS, SENSOR_RADIUS)
    square_network = generate_square_network(NUM_SENSORS, SENSOR_RADIUS)

    aperiodic_center = np.mean(aperiodic_network, axis=0)
    hexagonal_center = np.mean(hexagonal_network, axis=0)
    triangular_center = np.mean(triangular_network, axis=0)
    square_center = np.mean(square_network, axis=0)

    aperiodic_base_station = tuple(aperiodic_center)
    hexagonal_base_station = tuple(hexagonal_center)
    triangular_base_station = tuple(triangular_center)
    square_base_station = tuple(square_center)

    aperiodic_path, aperiodic_time = simulate_intruder_attack(aperiodic_network, INTRUDER_INITIAL_POSITION, aperiodic_base_station, is_aperiodic=True)
    hexagonal_path, hexagonal_time = simulate_intruder_attack(hexagonal_network, INTRUDER_INITIAL_POSITION, hexagonal_base_station, is_aperiodic=False)
    triangular_path, triangular_time = simulate_intruder_attack(triangular_network, INTRUDER_INITIAL_POSITION, triangular_base_station, is_aperiodic=False)
    square_path, square_time = simulate_intruder_attack(square_network, INTRUDER_INITIAL_POSITION, square_base_station, is_aperiodic=False)

    print("Aperiodic Network Path Length:", len(aperiodic_path), "Time Steps:", aperiodic_time)
    print("Hexagonal Network Path Length:", len(hexagonal_path), "Time Steps:", hexagonal_time)
    print("Triangular Network Path Length:", len(triangular_path), "Time Steps:", triangular_time)
    print("Square Network Path Length:", len(square_path), "Time Steps:", square_time)

    plot_path(aperiodic_path, aperiodic_network, "Intruder Path in Aperiodic Network", aperiodic_base_station)
    plot_path(hexagonal_path, hexagonal_network, "Intruder Path in Hexagonal Network", hexagonal_base_station)
    plot_path(triangular_path, triangular_network, "Intruder Path in Triangular Network", triangular_base_station)
    plot_path(square_path, square_network, "Intruder Path in Square Network", square_base_station)

run_simulation()
