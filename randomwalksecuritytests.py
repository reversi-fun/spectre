import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon
from securitymetricsaperiodic_hexagonal import generate_spectre_tiles, generate_hexagonal_network, transPt, SPECTRE_POINTS

# Parameters
NUM_SENSORS = 760  # Number of sensors for fair comparison
SENSOR_RADIUS = 10  # Ensuring both networks use the same sensor radius
INTRUDER_INITIAL_POSITION = (0, -200)
HOP_DISTANCE = SENSOR_RADIUS  # The distance of one hop, which is the same as the sensor radius

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

def simulate_intruder_attack(network, intruder_position, base_station_position, regular=True):
    path = [intruder_position]
    max_steps = 1000  # Set a reasonable limit to prevent infinite loops
    steps = 0
    visited_nodes = set()

    while not has_reached_base_station(intruder_position, base_station_position) and steps < max_steps:
        visited_nodes.add(tuple(intruder_position))  # Convert to tuple
        if regular:
            intruder_position = smart_random_walk_regular(network, intruder_position, visited_nodes)
        else:
            intruder_position = smart_random_walk_irregular(network, intruder_position)
        
        path.append(intruder_position)
        steps += 1
    
    if steps >= max_steps:
        print("Max steps reached, simulation stopped.")
    return path

def smart_random_walk_regular(network, intruder_position, visited_nodes):
    # Intruder moves to the nearest unvisited node in the network, simulating a regular attack
    distances = np.linalg.norm(np.array(network) - np.array(intruder_position), axis=1)
    sorted_indices = np.argsort(distances)

    for idx in sorted_indices:
        nearest_node = network[idx]
        if tuple(nearest_node) not in visited_nodes:  # Convert to tuple
            return nearest_node
    
    # If all nodes have been visited, stay in the current position
    return intruder_position

def smart_random_walk_irregular(network, intruder_position):
    # Intruder moves in a random direction
    angle_rad = np.random.uniform(0, 2 * np.pi)
    new_position = (intruder_position[0] + HOP_DISTANCE * np.cos(angle_rad),
                    intruder_position[1] + HOP_DISTANCE * np.sin(angle_rad))
    return new_position

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
    global SENSOR_RADIUS  # Ensure the sensor radius is used globally

    # Generate networks
    aperiodic_network = generate_aperiodic_network(SENSOR_RADIUS, NUM_SENSORS)
    hexagonal_network = generate_hexagonal_network(NUM_SENSORS, SENSOR_RADIUS)
    triangular_network = generate_triangular_network(NUM_SENSORS, SENSOR_RADIUS)
    square_network = generate_square_network(NUM_SENSORS, SENSOR_RADIUS)
    
    # Adjust base station position to the center of each network
    aperiodic_center = np.mean(aperiodic_network, axis=0)
    hexagonal_center = np.mean(hexagonal_network, axis=0)
    triangular_center = np.mean(triangular_network, axis=0)
    square_center = np.mean(square_network, axis=0)
    
    aperiodic_base_station = tuple(aperiodic_center)
    hexagonal_base_station = tuple(hexagonal_center)
    triangular_base_station = tuple(triangular_center)
    square_base_station = tuple(square_center)
    
    # Simulate attacks
    aperiodic_path = simulate_intruder_attack(aperiodic_network, INTRUDER_INITIAL_POSITION, aperiodic_base_station, regular=False)
    hexagonal_path = simulate_intruder_attack(hexagonal_network, INTRUDER_INITIAL_POSITION, hexagonal_base_station, regular=True)
    triangular_path = simulate_intruder_attack(triangular_network, INTRUDER_INITIAL_POSITION, triangular_base_station, regular=True)
    square_path = simulate_intruder_attack(square_network, INTRUDER_INITIAL_POSITION, square_base_station, regular=True)
    
    # Print results
    print("Aperiodic Network Path Length:", len(aperiodic_path))
    print("Hexagonal Network Path Length:", len(hexagonal_path))
    print("Triangular Network Path Length:", len(triangular_path))
    print("Square Network Path Length:", len(square_path))
    
    # Plot paths
    plot_path(aperiodic_path, aperiodic_network, "Intruder Path in Aperiodic Network", aperiodic_base_station)
    plot_path(hexagonal_path, hexagonal_network, "Intruder Path in Hexagonal Network", hexagonal_base_station)
    plot_path(triangular_path, triangular_network, "Intruder Path in Triangular Network", triangular_base_station)
    plot_path(square_path, square_network, "Intruder Path in Square Network", square_base_station)

run_simulation()
