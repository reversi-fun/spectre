import numpy as np
import matplotlib.pyplot as plt

# Parameters
FIELD_SIZE = 500
SENSOR_RADIUS = 10  # Ensuring both networks use the same sensor radius
BASE_STATION_POSITION = (FIELD_SIZE / 2, FIELD_SIZE / 2)
INTRUDER_INITIAL_POSITION = (0, 0)
HOP_DISTANCE = SENSOR_RADIUS  # The distance of one hop, which is the same as the sensor radius

def generate_hexagonal_network(field_size, sensor_radius):
    # Create a hexagonal grid of sensor nodes
    side_length = sensor_radius * np.sqrt(3)
    x_coords = np.arange(0, field_size, side_length)
    y_coords = np.arange(0, field_size, side_length)
    hexagonal_network = []

    for i, x in enumerate(x_coords):
        for j, y in enumerate(y_coords):
            if j % 2 == 0:
                hexagonal_network.append((x, y))
            else:
                hexagonal_network.append((x + sensor_radius * 0.5, y))
    
    return hexagonal_network

def simulate_intruder_attack_hexagonal(network, intruder_position):
    path = [intruder_position]
    max_steps = 1000  # Set a reasonable limit to prevent infinite loops
    steps = 0
    visited_nodes = set()

    while not has_reached_base_station(intruder_position) and steps < max_steps:
        visited_nodes.add(intruder_position)
        intruder_position = smart_random_walk_regular(network, intruder_position, visited_nodes)
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
        if nearest_node not in visited_nodes:
            print(f"Intruder moving to nearest unvisited node at {nearest_node}")  # Debug statement
            return nearest_node
    
    # If all nodes have been visited, stay in the current position
    return intruder_position

def has_reached_base_station(position):
    reached = np.linalg.norm(np.array(position) - np.array(BASE_STATION_POSITION)) <= SENSOR_RADIUS
    if reached:
        print(f"Base station reached at position {position}")  # Debug statement
    return reached

def plot_path(path, network, title):
    plt.figure(figsize=(10, 10))
    for node in network:
        plt.plot(node[0], node[1], 'bo', markersize=2)
    path = np.array(path)
    plt.plot(path[:, 0], path[:, 1], 'r-')
    plt.plot(BASE_STATION_POSITION[0], BASE_STATION_POSITION[1], 'go', markersize=5)
    plt.title(title)
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.grid(True)
    plt.show()

def run_simulation():
    global SENSOR_RADIUS  # Ensure the sensor radius is used globally

    # Generate hexagonal network
    hexagonal_network = generate_hexagonal_network(FIELD_SIZE, SENSOR_RADIUS)
    print(f"Generated hexagonal network with {len(hexagonal_network)} nodes.")  # Debug statement
    
    # Simulate attack
    hexagonal_path = simulate_intruder_attack_hexagonal(hexagonal_network, INTRUDER_INITIAL_POSITION)
    
    # Print results
    print("Hexagonal Network Path Length:", len(hexagonal_path))
    
    # Plot path
    plot_path(hexagonal_path, hexagonal_network, "Intruder Path in Hexagonal Network")

run_simulation()
