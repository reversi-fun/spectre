import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, RegularPolygon
from spectre import buildSpectreBase, transPt, MetaTile, buildSupertiles, SPECTRE_POINTS

# Parameters
N_ITERATIONS = 1
EDGE_A = 10.0
EDGE_B = 10.0
SENSOR_RADIUS = 10  # Adjust based on the actual sensing range required for 1-coverage

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

def draw_hex_grid(ax, radius, grid_size):
    """Draw a hexagonal grid on the given axes."""
    hex_height = np.sqrt(3) * radius
    for x in range(-grid_size, grid_size + 1):
        for y in range(-grid_size, grid_size + 1):
            center_x = x * 1.5 * radius
            center_y = y * hex_height + (x % 2) * hex_height / 2
            hexagon = RegularPolygon((center_x, center_y), numVertices=6, radius=radius, 
                                     orientation=np.radians(30), edgecolor='lightgrey', fill=False)
            ax.add_patch(hexagon)

def compute_coverage_map(sensor_positions, sensor_radius, grid_resolution=1):
    """Compute a coverage map indicating the number of sensors covering each point."""
    # Determine the bounding box of the sensor positions
    sensor_positions = np.array(sensor_positions)
    x_min, y_min = sensor_positions.min(axis=0) - sensor_radius
    x_max, y_max = sensor_positions.max(axis=0) + sensor_radius
    
    # Create a grid of points within the bounding box
    x_coords = np.arange(x_min, x_max, grid_resolution)
    y_coords = np.arange(y_min, y_max, grid_resolution)
    coverage_map = np.zeros((len(x_coords), len(y_coords)))
    
    # Compute coverage
    for sensor_pos in sensor_positions:
        for i, x in enumerate(x_coords):
            for j, y in enumerate(y_coords):
                if np.linalg.norm(sensor_pos - np.array([x, y])) <= sensor_radius:
                    coverage_map[i, j] += 1
    
    return x_coords, y_coords, coverage_map

def plot_coverage_map(x_coords, y_coords, coverage_map):
    fig, ax = plt.subplots(figsize=(15, 15))
    c = ax.pcolormesh(x_coords, y_coords, coverage_map.T, shading='auto', cmap='viridis')
    fig.colorbar(c, ax=ax)
    ax.set_aspect('equal', adjustable='box')
    plt.title("Coverage Map")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.show()

def plot_spectre_tiles_with_sensors(tiles, sensor_positions):
    fig, ax = plt.subplots(figsize=(15, 15))  # Enlarge the output graph
    all_points = []

    def draw_tile(transformation, label):
        points = [transPt(transformation, pt) for pt in SPECTRE_POINTS]
        all_points.extend(points)
        polygon = Polygon(points, closed=True, fill=None, edgecolor='b')
        ax.add_patch(polygon)

    tiles["Delta"].forEachTile(draw_tile)

    # Place sensors at the strategic points
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
    plt.grid(False)
    plt.title("Spectre Tile with Sensors for 1-Coverage")
    
    # Draw hexagonal grid in the background
    draw_hex_grid(ax, EDGE_A, grid_size=15)
    
    plt.savefig("spectre_with_sensors_1_coverage_optimized_with_hex_grid.png")
    plt.show()

# Generate spectre tiles
tiles = generate_spectre_tiles()

# Place sensors for 1-coverage
sensor_positions = place_sensors_for_1_coverage(tiles)

# Plot the spectre tiles with sensor nodes
plot_spectre_tiles_with_sensors(tiles, sensor_positions)

# Compute and plot the coverage map
x_coords, y_coords, coverage_map = compute_coverage_map(sensor_positions, SENSOR_RADIUS)
plot_coverage_map(x_coords, y_coords, coverage_map)
