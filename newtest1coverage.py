import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, RegularPolygon
from spectre import buildSpectreBase, transPt, MetaTile, buildSupertiles, SPECTRE_POINTS

# Parameters
N_ITERATIONS = 2  # Adjust for different levels of supertiles
EDGE_A = 10.0
EDGE_B = 10.0
SENSOR_RADIUS = 10  # Adjust based on the actual sensing range required for 1-coverage

# Desired coverage level
K_COVERAGE = 1

def generate_spectre_tiles(n_iterations):
    tiles = buildSpectreBase()
    for _ in range(n_iterations):
        tiles = buildSupertiles(tiles)
    return tiles

def place_sensors_adaptively(tiles, k_coverage):
    sensor_positions = []
    
    def add_sensor_points(transformation, label):
        nonlocal sensor_positions
        tile_points = [transPt(transformation, pt) for pt in SPECTRE_POINTS]
        
        if label in ['H', 'T', 'P', 'F']:
            # Customize placement based on cluster type and desired k-coverage
            if k_coverage == 1:
                # For 1-coverage, place sensors at strategic points within the cluster
                centroid = np.mean(tile_points, axis=0)
                sensor_positions.append(centroid)
            elif k_coverage == 2:
                # For 2-coverage, place sensors at vertices and midpoints
                for pt in tile_points:
                    sensor_positions.append(pt)
                for i in range(len(tile_points)):
                    mid_point = (tile_points[i] + tile_points[(i + 1) % len(tile_points)]) / 2
                    sensor_positions.append(mid_point)
            elif k_coverage == 3:
                # For 3-coverage, place sensors at vertices, midpoints, and centroid
                for pt in tile_points:
                    sensor_positions.append(pt)
                for i in range(len(tile_points)):
                    mid_point = (tile_points[i] + tile_points[(i + 1) % len(tile_points)]) / 2
                    sensor_positions.append(mid_point)
                centroid = np.mean(tile_points, axis=0)
                sensor_positions.append(centroid)
            # Additional strategies can be added for higher k-coverage levels

    tiles["Delta"].forEachTile(add_sensor_points)
    return sensor_positions

def draw_hex_grid(ax, radius, grid_size):
    """Draw a hexagonal grid on the given axes."""
    hex_height = np.sqrt(3) * radius
    for x in range(-grid_size, grid_size + 1):
        for y in range(-grid_size, grid_size + 1):
            center_x = x * 1.5 * radius
            center_y = y * hex_height + (x % 2) * hex_height / 2
            hexagon = RegularPolygon((center_x, center_y), numVertices=6, radius=radius, 
                                     orientation=np.radians(30), edgecolor='lightgrey', fill=False, zorder=0)
            ax.add_patch(hexagon)

def plot_spectre_tiles_with_sensors(tiles, sensor_positions):
    fig, ax = plt.subplots(figsize=(15, 15))  # Enlarge the output graph
    all_points = []

    def draw_tile(transformation, label):
        points = [transPt(transformation, pt) for pt in SPECTRE_POINTS]
        all_points.extend(points)
        polygon = Polygon(points, closed=True, fill=None, edgecolor='b', zorder=1)
        ax.add_patch(polygon)

    # Draw hexagonal grid in the background
    draw_hex_grid(ax, EDGE_A, grid_size=15)

    tiles["Delta"].forEachTile(draw_tile)

    # Place sensors at the strategic points
    for sensor_pos in sensor_positions:
        circle = Circle(sensor_pos, SENSOR_RADIUS, color='r', fill=False, linestyle='dotted', zorder=2)
        ax.add_patch(circle)
        ax.plot(sensor_pos[0], sensor_pos[1], 'ko', markersize=2, zorder=3)  # Smaller black dot for the sensor node

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
    plt.grid(False)
    plt.title("Spectre Tile with Sensors for 1-Coverage")
    plt.savefig("spectre_with_sensors_adaptive_coverage.png")
    plt.show()

# Generate spectre tiles with specified number of iterations
tiles = generate_spectre_tiles(N_ITERATIONS)

# Place sensors adaptively for the desired k-coverage
sensor_positions = place_sensors_adaptively(tiles, K_COVERAGE)

# Plot the spectre tiles with sensor nodes
plot_spectre_tiles_with_sensors(tiles, sensor_positions)
