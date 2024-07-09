import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as mplPolygon, Circle
from matplotlib.colors import ListedColormap
from shapely.geometry import Polygon
from spectre import buildSpectreBase, transPt, MetaTile, buildSupertiles, SPECTRE_POINTS

# Parameters
GRID_RESOLUTION = 1  # Resolution of the coverage grid
FIELD_SIZE = 500  # Size of the field to cover (500x500 meters)
ENERGY_CONSUMPTION_RATE = 1  # Example value for energy consumption per sensor

def calculate_sensor_radius(tile_points):
    """Calculate the sensor radius to inscribe the spectre monotile within a circle."""
    longest_distance = max(np.linalg.norm(pt - np.mean(tile_points, axis=0)) for pt in tile_points)
    return longest_distance

def generate_spectre_tiles():
    tiles = buildSpectreBase()
    iterations = 0
    while not is_field_covered(tiles, FIELD_SIZE):
        tiles = buildSupertiles(tiles)
        iterations += 1
    return tiles, iterations

def is_field_covered(tiles, field_size):
    all_points = []
    tiles["Delta"].forEachTile(lambda t, l: all_points.extend([transPt(t, pt) for pt in SPECTRE_POINTS]))
    all_points = np.array(all_points)
    x_min, x_max = all_points[:, 0].min(), all_points[:, 0].max()
    y_min, y_max = all_points[:, 1].min(), all_points[:, 1].max()
    return x_max - x_min >= field_size and y_max - y_min >= field_size

def place_sensors_inscribed(tiles):
    sensor_positions = []
    
    def add_sensor_points(transformation, label):
        nonlocal sensor_positions
        tile_points = [transPt(transformation, pt) for pt in SPECTRE_POINTS]
        centroid = np.mean(tile_points, axis=0)
        sensor_positions.append(centroid)
    
    tiles["Delta"].forEachTile(add_sensor_points)
    return sensor_positions

def generate_hexagonal_network(field_size, sensor_radius):
    """Generate a hexagonal network for the given field size and sensor radius."""
    hex_height = np.sqrt(3) * sensor_radius
    sensor_positions = []
    
    for x in np.arange(0, field_size, 1.5 * sensor_radius):
        for y in np.arange(0, field_size, hex_height):
            offset = (x // (1.5 * sensor_radius)) % 2 * (hex_height / 2)
            sensor_positions.append((x, y + offset))
    
    return np.array(sensor_positions)

def calculate_coverage(sensor_positions, sensor_radius, grid_resolution, field_size):
    x_coords = np.arange(0, field_size, grid_resolution)
    y_coords = np.arange(0, field_size, grid_resolution)
    coverage_map = np.zeros((len(x_coords), len(y_coords)))

    for sensor in sensor_positions:
        for i, x in enumerate(x_coords):
            for j, y in enumerate(y_coords):
                if np.linalg.norm(sensor - np.array([x, y])) <= sensor_radius:
                    coverage_map[i, j] += 1

    return x_coords, y_coords, coverage_map

def calculate_metrics(sensor_positions, coverage_map):
    total_area = coverage_map.size
    covered_area = np.sum(coverage_map > 0)
    sensor_density = len(sensor_positions) / total_area

    overlap_sum = np.sum(coverage_map) - covered_area
    rate_of_overlap = overlap_sum / total_area
    coverage_quality = 1 / rate_of_overlap if rate_of_overlap > 0 else float('inf')

    return sensor_density, rate_of_overlap, coverage_quality

def calculate_total_energy_consumption(sensor_positions):
    return len(sensor_positions) * ENERGY_CONSUMPTION_RATE

def plot_coverage_map(x_coords, y_coords, coverage_map):
    fig, ax = plt.subplots(figsize=(15, 15))
    cmap = ListedColormap(['white', 'lightblue', 'blue', 'darkblue', 'purple'])
    c = ax.pcolormesh(x_coords, y_coords, coverage_map.T, shading='auto', cmap=cmap)
    fig.colorbar(c, ax=ax, ticks=np.arange(0, np.max(coverage_map) + 1, 1))
    ax.set_aspect('equal', adjustable='box')
    plt.title("Coverage Map")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.show()

def plot_spectre_tiles_with_sensors(tiles, sensor_positions, sensor_radius):
    fig, ax = plt.subplots(figsize=(15, 15))
    all_points = []

    def draw_tile(transformation, label):
        points = [transPt(transformation, pt) for pt in SPECTRE_POINTS]
        all_points.extend(points)
        polygon = mplPolygon(points, closed=True, fill=None, edgecolor='b')
        ax.add_patch(polygon)

    tiles["Delta"].forEachTile(draw_tile)

    for sensor_pos in sensor_positions:
        circle = Circle(sensor_pos, sensor_radius, color='r', fill=False, linestyle='dotted')
        ax.add_patch(circle)
        ax.plot(sensor_pos[0], sensor_pos[1], 'ko', markersize=2)

    if all_points:
        all_points = np.array(all_points)
        x_min, x_max = all_points[:, 0].min(), all_points[:, 0].max()
        y_min, y_max = all_points[:, 1].min(), all_points[:, 1].max()
        x_center = (x_min + x_max) / 2
        y_center = (y_min + y_max) / 2
        plot_width = x_max - x_min + 20
        plot_height = y_max - y_min + 20

        ax.set_xlim(x_center - plot_width / 2, x_center + plot_width / 2)
        ax.set_ylim(y_center - plot_height / 2, y_center + plot_height / 2)

    ax.set_aspect('equal', adjustable='box')
    plt.grid(True)
    plt.title("Spectre Tile with Sensors Inscribed for Coverage")
    plt.savefig("spectre_with_sensors_inscribed_coverage.png")
    plt.show()

def simulate_clone_attack(network, num_clones):
    cloned_nodes = np.random.choice(len(network), num_clones, replace=False)
    attacker_nodes = np.array(network)[cloned_nodes] + np.random.normal(0, 1, (num_clones, 2))  # Slightly offset the clones
    return attacker_nodes

def detect_clone_attack(network, attacker_nodes, detection_radius):
    detection_time = 0
    detected_clones = []
    for attacker in attacker_nodes:
        for sensor in network:
            if np.linalg.norm(attacker - sensor) < detection_radius:
                detected_clones.append(attacker)
                break
        detection_time += 1  # Increment time for each check
    return detection_time, detected_clones

def measure_metrics(network, attacker_nodes, detection_radius):
    detection_time, detected_clones = detect_clone_attack(network, attacker_nodes, detection_radius)
    num_compromised = len(attacker_nodes) - len(detected_clones)
    network_connectivity = check_network_connectivity(network, detected_clones)
    coverage = check_coverage(network, detected_clones)
    energy_consumption = calculate_energy_consumption(network, detection_time)
    return detection_time, num_compromised, network_connectivity, coverage, energy_consumption

def check_network_connectivity(network, detected_clones):
    # Implement a method to check if the network remains connected
    return True  # Placeholder

def check_coverage(network, detected_clones):
    # Implement a method to check if coverage is maintained
    return True  # Placeholder

def calculate_energy_consumption(network, detection_time):
    return len(network) * detection_time * ENERGY_CONSUMPTION_RATE

def run_simulation():
    field_size = 500
    num_clones = 5

    # Generate networks
    aperiodic_tiles, iterations = generate_spectre_tiles()
    aperiodic_network = place_sensors_inscribed(aperiodic_tiles)

    # Calculate sensor radius based on spectre tiles
    example_tile_points = [transPt(np.eye(3), pt) for pt in SPECTRE_POINTS]
    sensor_radius = calculate_sensor_radius(example_tile_points)

    hexagonal_network = generate_hexagonal_network(field_size, sensor_radius)

    # Simulate attacks
    aperiodic_attackers = simulate_clone_attack(aperiodic_network, num_clones)
    hexagonal_attackers = simulate_clone_attack(hexagonal_network, num_clones)

    # Measure metrics
    aperiodic_metrics = measure_metrics(aperiodic_network, aperiodic_attackers, detection_radius=2 * sensor_radius)
    hexagonal_metrics = measure_metrics(hexagonal_network, hexagonal_attackers, detection_radius=2 * sensor_radius)

    # Print results
    print("Aperiodic Network Metrics:", aperiodic_metrics)
    print("Hexagonal Network Metrics:", hexagonal_metrics)

run_simulation()
