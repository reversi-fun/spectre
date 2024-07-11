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
MAX_ITERATIONS = 10  # Maximum number of iterations to prevent infinite loops
SENSOR_RADIUS = 10  # Example sensor radius

def calculate_sensor_radius(tile_points):
    """Calculate the sensor radius to inscribe the spectre monotile within a circle."""
    longest_distance = max(np.linalg.norm(pt - np.mean(tile_points, axis=0)) for pt in tile_points)
    return longest_distance

def generate_spectre_tiles(num_iterations):
    tiles = buildSpectreBase()
    for _ in range(num_iterations):
        tiles = buildSupertiles(tiles)
        print(f"Iteration {_+1} completed.")
    return tiles

def place_sensors_inscribed(tiles):
    sensor_positions = []
    def add_sensor_points(transformation, label):
        nonlocal sensor_positions
        tile_points = [transPt(transformation, pt) for pt in SPECTRE_POINTS]
        centroid = np.mean(tile_points, axis=0)
        sensor_positions.append(centroid)
    tiles["Delta"].forEachTile(add_sensor_points)
    return sensor_positions

def generate_aperiodic_network(sensor_radius, num_sensors, num_iterations):
    tiles = generate_spectre_tiles(num_iterations)
    sensor_positions = place_sensors_inscribed(tiles)
    return np.array(sensor_positions)[:num_sensors]

def generate_hexagonal_network(num_sensors, sensor_radius):
    """Generate a hexagonal network of sensors."""
    sensor_positions = []
    hex_height = np.sqrt(3) * sensor_radius
    x_offset = 1.5 * sensor_radius
    num_rows = int(np.ceil(np.sqrt(num_sensors)))
    num_cols = int(np.ceil(num_sensors / num_rows))

    for x in range(num_cols):
        for y in range(num_rows):
            center_x = x * x_offset
            center_y = y * hex_height + (x % 2) * hex_height / 2
            sensor_positions.append((center_x, center_y))
            if len(sensor_positions) >= num_sensors:
                return np.array(sensor_positions)
    
    return np.array(sensor_positions)

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
    return np.array(sensor_positions)[:num_sensors]

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
    return np.array(sensor_positions)[:num_sensors]

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

def run_simulation(num_iterations=3):
    global SENSOR_RADIUS

    num_sensors_per_iteration = [9, 71, 559, 4401]
    num_sensors = num_sensors_per_iteration[num_iterations - 1]

    aperiodic_network = generate_aperiodic_network(SENSOR_RADIUS, num_sensors, num_iterations)
    hexagonal_network = generate_hexagonal_network(num_sensors, SENSOR_RADIUS)
    triangular_network = generate_triangular_network(num_sensors, SENSOR_RADIUS)
    square_network = generate_square_network(num_sensors, SENSOR_RADIUS)

    aperiodic_center = np.mean(aperiodic_network, axis=0)
    hexagonal_center = np.mean(hexagonal_network, axis=0)
    triangular_center = np.mean(triangular_network, axis=0)
    square_center = np.mean(square_network, axis=0)

    aperiodic_base_station = tuple(aperiodic_center)
    hexagonal_base_station = tuple(hexagonal_center)
    triangular_base_station = tuple(triangular_center)
    square_base_station = tuple(square_center)

    print(f"Total number of sensors: {num_sensors}")
    print(f"Aperiodic network sensors: {len(aperiodic_network)}")
    print(f"Hexagonal network sensors: {len(hexagonal_network)}")
    print(f"Triangular network sensors: {len(triangular_network)}")
    print(f"Square network sensors: {len(square_network)}")

run_simulation(num_iterations=2)
