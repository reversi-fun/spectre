import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle
from spectre import buildSpectreBase, transPt, MetaTile, buildSupertiles, SPECTRE_POINTS

# Parameters
N_ITERATIONS = 1
SENSOR_RADIUS = 10  # Adjust based on the actual sensing range
EDGE_A = 10.0
EDGE_B = 10.0

def generate_spectre_tiles():
    tiles = buildSpectreBase()
    for _ in range(N_ITERATIONS):
        tiles = buildSupertiles(tiles)
    return tiles

def place_sensors_optimized(tiles):
    sensor_positions = []
    
    def add_sensor_points(transformation, label):
        nonlocal sensor_positions
        tile_points = [transPt(transformation, pt) for pt in SPECTRE_POINTS]
        
        # Add vertices as sensor points
        sensor_positions.extend(tile_points)
        
        # Add midpoint of the tile
        midpoint = np.mean(tile_points, axis=0)
        sensor_positions.append(midpoint)
        
        # Add additional strategic points within the tile if needed
        # Example: Adding centroids of smaller triangles formed within the tile
        for i in range(len(tile_points)):
            for j in range(i + 1, len(tile_points)):
                midpoint_ij = (tile_points[i] + tile_points[j]) / 2
                sensor_positions.append(midpoint_ij)

    tiles["Delta"].forEachTile(add_sensor_points)
    return sensor_positions

def plot_spectre_tiles_with_sensors(tiles, sensor_positions):
    fig, ax = plt.subplots(figsize=(15, 15))  # Enlarge the output graph
    all_points = []

    def draw_tile(transformation, label):
        points = [transPt(transformation, pt) for pt in SPECTRE_POINTS]
        all_points.extend(points)
        polygon = Polygon(points, closed=True, fill=None, edgecolor='b')
        ax.add_patch(polygon)

    tiles["Delta"].forEachTile(draw_tile)

    # Place sensors at the vertices
    for sensor_pos in sensor_positions:
        circle = Circle(sensor_pos, SENSOR_RADIUS, color='r', fill=False, linestyle='dotted')
        ax.add_patch(circle)
        ax.plot(sensor_pos[0], sensor_pos[1], 'ko', markersize=2)  # Smaller black dot for the sensor node

    # Calculate limits to center the plot
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
    plt.grid(True)
    plt.title("Spectre Tile with Sensors for 1-Coverage")
    plt.savefig("spectre_with_sensors_1_coverage_optimized.png")
    plt.show()

# Generate spectre tiles
tiles = generate_spectre_tiles()

# Place sensors at optimized positions
sensor_positions = place_sensors_optimized(tiles)

# Plot the spectre tiles with sensor nodes
plot_spectre_tiles_with_sensors(tiles, sensor_positions)
