import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle
from matplotlib.colors import ListedColormap
from spectre import buildSpectreBase, transPt, MetaTile, buildSupertiles, SPECTRE_POINTS

# Parameters
N_ITERATIONS = 1
SENSOR_RADIUS = 10  # Adjust based on the actual sensing range required
K_COVERAGE = 2  # Desired level of k-coverage
GRID_RESOLUTION = 1  # Resolution of the coverage grid

def generate_spectre_tiles(n_iterations):
    tiles = buildSpectreBase()
    for _ in range(n_iterations):
        tiles = buildSupertiles(tiles)
    return tiles

def place_sensors_adaptive(tiles, k_coverage):
    sensor_positions = []
    
    def add_sensor_points(transformation, label, level):
        nonlocal sensor_positions
        tile_points = [transPt(transformation, pt) for pt in SPECTRE_POINTS]
        
        # Place sensors at strategic points within the cluster
        cluster_centroid = np.mean(tile_points, axis=0)
        sensor_positions.append(cluster_centroid)
        for pt in tile_points:
            sensor_positions.append(pt)
            midpoint = (pt + cluster_centroid) / 2
            sensor_positions.append(midpoint)
        
        if k_coverage > 1:
            extra_sensors = [((pt + cluster_centroid) / 2) for pt in tile_points]
            sensor_positions.extend(extra_sensors)
    
    for level in range(1, N_ITERATIONS + 1):
        tiles["Delta"].forEachTile(lambda t, l: add_sensor_points(t, l, level))
    
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

def calculate_sensor_area_usage(coverage_map, sensor_radius, grid_resolution):
    total_area = coverage_map.size * grid_resolution**2
    sensor_area = np.pi * sensor_radius**2
    covered_area = np.sum(coverage_map > 0) * grid_resolution**2
    percentage_usage = (covered_area / total_area) * 100
    return percentage_usage

def plot_coverage_map(x_coords, y_coords, coverage_map, k_coverage):
    cmap = ListedColormap(['white', 'lightblue', 'blue', 'darkblue', 'purple'])
    fig, ax = plt.subplots(figsize=(15, 15))
    c = ax.pcolormesh(x_coords, y_coords, coverage_map.T, shading='auto', cmap=cmap, vmin=0, vmax=k_coverage+1)
    fig.colorbar(c, ax=ax, ticks=np.arange(0, k_coverage + 2, 1))
    ax.set_aspect('equal', adjustable='box')
    plt.title(f"Coverage Map for {k_coverage}-Coverage")
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
    plt.title(f"Spectre Tile with Sensors for {K_COVERAGE}-Coverage")
    plt.savefig("spectre_with_sensors_adaptive_coverage.png")
    plt.show()

# Generate spectre tiles
tiles = generate_spectre_tiles(N_ITERATIONS)

# Place sensors adaptively for k-coverage
sensor_positions = place_sensors_adaptive(tiles, K_COVERAGE)

# Calculate and plot the coverage map
x_coords, y_coords, coverage_map = calculate_coverage(sensor_positions, SENSOR_RADIUS, GRID_RESOLUTION)
plot_coverage_map(x_coords, y_coords, coverage_map, K_COVERAGE)

# Plot the spectre tiles with sensor nodes
plot_spectre_tiles_with_sensors(tiles, sensor_positions)

# Calculate sensor area usage
sensor_area_usage = calculate_sensor_area_usage(coverage_map, SENSOR_RADIUS, GRID_RESOLUTION)
print(f"Sensor area usage: {sensor_area_usage:.2f}%")
