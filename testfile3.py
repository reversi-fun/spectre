import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon, Circle
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

from spectre import buildSpectreBase, transPt, MetaTile, buildSupertiles, SPECTRE_POINTS

# Parameters
N_ITERATIONS = 1
EDGE_A = 10.0
EDGE_B = 10.0
SENSOR_RADIUS = 10  # Adjust based on the actual sensing range required for 1-coverage
GRID_RESOLUTION = 1  # Resolution of the coverage grid

def generate_spectre_tiles():
    tiles = buildSpectreBase()
    for _ in range(N_ITERATIONS):
        tiles = buildSupertiles(tiles)
    return tiles

def place_sensors_for_1_coverage(tiles):
    sensor_positions = []
    
    def add_sensor_points(transformation, label):
        nonlocal sensor_positions
        tile_points = [transPt(transformation, pt) for pt in SPECTRE_POINTS]
        
        # Place sensors at strategic points (e.g., vertices, midpoints, centroids)
        for pt in tile_points:
            sensor_positions.append(pt)
        
        # Place a sensor at the centroid of the tile
        centroid = np.mean(tile_points, axis=0)
        sensor_positions.append(centroid)

    tiles["Delta"].forEachTile(add_sensor_points)
    return sensor_positions

def calculate_coverage(sensor_positions, sensor_radius, grid_resolution):
    x_coords = np.arange(-200, 200, grid_resolution)
    y_coords = np.arange(-200, 200, grid_resolution)
    coverage_map = np.zeros((len(x_coords), len(y_coords)))
    
    for sensor in sensor_positions:
        for i, x in enumerate(x_coords):
            for j, y in enumerate(y_coords):
                if np.linalg.norm(sensor - np.array([x, y])) <= sensor_radius:
                    coverage_map[i, j] += 1
    
    return x_coords, y_coords, coverage_map

def plot_combined_map(tiles, sensor_positions, x_coords, y_coords, coverage_map):
    max_coverage = int(np.max(coverage_map))
    colors = ['white', 'lightblue', 'blue', 'darkblue', 'purple', 'red', 'darkred', 'orange', 'yellow', 'green', 'darkgreen', 'black']
    
    fig, ax = plt.subplots(figsize=(15, 15))
    
    # Plot coverage map
    coverage_map_transposed = coverage_map.T
    for level in range(1, max_coverage + 1):
        if level < len(colors):
            level_mask = coverage_map_transposed == level
            ax.contourf(x_coords, y_coords, level_mask, levels=[0.5, 1.5], colors=[colors[level]])
    
    # Plot spectre tiles and sensors
    all_points = []

    def draw_tile(transformation, label):
        points = [transPt(transformation, pt) for pt in SPECTRE_POINTS]
        all_points.extend(points)
        polygon = MplPolygon(points, closed=True, fill=None, edgecolor='b')
        ax.add_patch(polygon)

    tiles["Delta"].forEachTile(draw_tile)

    for sensor_pos in sensor_positions:
        circle = Circle(sensor_pos, SENSOR_RADIUS, color='r', fill=False, linestyle='dotted')
        ax.add_patch(circle)
        ax.plot(sensor_pos[0], sensor_pos[1], 'ko', markersize=2)  # Smaller black dot for the sensor node

    if all_points:
        all_points = np.array(all_points)
        x_min, x_max = all_points[:, 0].min(), all_points[:, 0].max()
        y_min, y_max = all_points[:, 1].min(), all_points[:, 1].max()
        x_center = (x_min + x_max) / 2
        y_center = (y_min + y_max) / 2
        plot_width = x_max - x_min + 20  # Adjust padding as necessary
        plot_height = y_max - y_min + 20  # Adjust padding as necessary

        ax.set_xlim(x_center - plot_width / 2, x_center + plot_width / 2)
        ax.set_ylim(y_center - plot_height / 2, y_center + plot_height / 2)

    ax.set_aspect('equal', adjustable='box')
    plt.grid(False)
    plt.title("Spectre Tile with Sensors and Coverage Map")
    plt.gca().set_facecolor('white')
    plt.savefig("spectre_with_sensors_and_coverage_map.png", facecolor='white')
    plt.show()

# Generate spectre tiles
tiles = generate_spectre_tiles()

# Place sensors for 1-coverage
sensor_positions = place_sensors_for_1_coverage(tiles)

# Calculate coverage
x_coords, y_coords, coverage_map = calculate_coverage(sensor_positions, SENSOR_RADIUS, GRID_RESOLUTION)

# Plot combined map
plot_combined_map(tiles, sensor_positions, x_coords, y_coords, coverage_map)
