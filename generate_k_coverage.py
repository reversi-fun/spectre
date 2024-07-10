import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as mplPolygon, Circle
from matplotlib.colors import ListedColormap
from shapely.geometry import Point
from spectre import buildSpectreBase, transPt, buildSupertiles, SPECTRE_POINTS

# Parameters
GRID_RESOLUTION = 1  # Resolution of the coverage grid
MAX_ITERATIONS = 3  # Maximum number of iterations to generate spectre tiles
K_COVERAGE = 2  # Desired level of k-coverage
MAX_ADDITIONAL_SENSORS = 5000  # Maximum number of additional sensors to ensure K-coverage
MAX_K_COVERAGE_ITERATIONS = 3  # Maximum iterations for ensuring K-coverage

def calculate_sensor_radius(tile_points):
    """Calculate the sensor radius to inscribe the spectre monotile within a circle."""
    longest_distance = max(np.linalg.norm(pt - np.mean(tile_points, axis=0)) for pt in tile_points)
    return longest_distance

def generate_spectre_tiles():
    tiles = buildSpectreBase()
    iterations = 0
    while iterations < MAX_ITERATIONS:
        tiles = buildSupertiles(tiles)
        iterations += 1
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

def calculate_coverage(sensor_positions, sensor_radius, grid_resolution):
    x_coords = np.arange(0, np.max(sensor_positions[:,0]) + grid_resolution, grid_resolution)
    y_coords = np.arange(0, np.max(sensor_positions[:,1]) + grid_resolution, grid_resolution)
    coverage_map = np.zeros((len(x_coords), len(y_coords)))
    for sensor in sensor_positions:
        for i, x in enumerate(x_coords):
            for j, y in enumerate(y_coords):
                if np.linalg.norm(sensor - np.array([x, y])) <= sensor_radius:
                    coverage_map[i, j] += 1
    return x_coords, y_coords, coverage_map

def ensure_k_coverage(sensor_positions, k, sensor_radius, grid_resolution):
    iteration = 0
    while iteration < MAX_K_COVERAGE_ITERATIONS:
        x_coords, y_coords, coverage_map = calculate_coverage(sensor_positions, sensor_radius, grid_resolution)
        if np.min(coverage_map) >= k:
            break
        additional_positions = []
        for sensor in sensor_positions:
            for _ in range(k):
                shift = np.random.normal(scale=sensor_radius, size=2)
                new_pos = sensor + shift
                additional_positions.append(new_pos)
        sensor_positions = np.concatenate((sensor_positions, additional_positions), axis=0)
        iteration += 1
        print(f"Iteration {iteration}: Minimum coverage = {np.min(coverage_map)}, Total sensors = {len(sensor_positions)}")
        if len(sensor_positions) > MAX_ADDITIONAL_SENSORS:
            print("Maximum additional sensors limit reached.")
            break
    return x_coords, y_coords, coverage_map, sensor_positions

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

# Generate spectre tiles and count sensors per iteration
tiles = generate_spectre_tiles()

# Place sensors inscribed within each tile
sensor_positions = place_sensors_inscribed(tiles)
sensor_positions = np.array(sensor_positions)

# Calculate sensor radius
example_tile_points = [transPt(np.eye(3), pt) for pt in SPECTRE_POINTS]  # Using identity matrix for transformation
SENSOR_RADIUS = calculate_sensor_radius(example_tile_points)

# Ensure k-coverage
x_coords, y_coords, coverage_map, sensor_positions = ensure_k_coverage(sensor_positions, K_COVERAGE, SENSOR_RADIUS, GRID_RESOLUTION)

# Plot the coverage map
plot_coverage_map(x_coords, y_coords, coverage_map)

# Plot the spectre tiles with sensor nodes
plot_spectre_tiles_with_sensors(tiles, sensor_positions, SENSOR_RADIUS)
