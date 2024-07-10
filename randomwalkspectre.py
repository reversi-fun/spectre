import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon
from securitymetricsaperiodic_hexagonal import generate_aperiodic_network, generate_hexagonal_network

# Parameters
FIELD_SIZE = 500
SENSOR_RADIUS = 10  # Ensuring both networks use the same sensor radius
BASE_STATION_POSITION = (FIELD_SIZE / 2, FIELD_SIZE / 2)
INTRUDER_INITIAL_POSITION = (0, 0)
ANGLE_INCREMENT = 30  # Degrees
HOP_DISTANCE = SENSOR_RADIUS / 2  # Half the sensing range

def random_walk(intruder_position, angle):
    angle_rad = np.deg2rad(angle)
    new_position = (intruder_position[0] + HOP_DISTANCE * np.cos(angle_rad),
                    intruder_position[1] + HOP_DISTANCE * np.sin(angle_rad))
    return new_position

def simulate_intruder_attack(network, intruder_position):
    path = [intruder_position]
    angle = 0
    while not has_reached_base_station(intruder_position):
        intruder_position = random_walk(intruder_position, angle)
        path.append(intruder_position)
        angle = (angle + ANGLE_INCREMENT) % 360  # Iterate through angles
    return path

def has_reached_base_station(position):
    return np.linalg.norm(np.array(position) - np.array(BASE_STATION_POSITION)) <= SENSOR_RADIUS

def plot_path(path, network):
    plt.figure(figsize=(10, 10))
    for node in network:
        plt.plot(node[0], node[1], 'bo', markersize=2)
    path = np.array(path)
    plt.plot(path[:, 0], path[:, 1], 'r-')
    plt.plot(BASE_STATION_POSITION[0], BASE_STATION_POSITION[1], 'go', markersize=5)
    plt.title("Intruder Path to Base Station")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.grid(True)
    plt.show()

def run_simulation():
    global SENSOR_RADIUS  # Ensure the sensor radius is used globally

    aperiodic_network = generate_aperiodic_network(FIELD_SIZE, SENSOR_RADIUS)
    hexagonal_network = generate_hexagonal_network(FIELD_SIZE, SENSOR_RADIUS)
    aperiodic_path = simulate_intruder_attack(aperiodic_network, INTRUDER_INITIAL_POSITION)
    hexagonal_path = simulate_intruder_attack(hexagonal_network, INTRUDER_INITIAL_POSITION)
    
    print("Aperiodic Network Path Length:", len(aperiodic_path))
    print("Hexagonal Network Path Length:", len(hexagonal_path))
    
    plot_path(aperiodic_path, aperiodic_network)
    plot_path(hexagonal_path, hexagonal_network)

run_simulation()
