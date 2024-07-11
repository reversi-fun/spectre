import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as mplPolygon, Circle
from matplotlib.colors import ListedColormap
from shapely.geometry import Polygon
from spectre import buildSpectreBase, transPt, buildSupertiles, SPECTRE_POINTS, Edge_a, Edge_b
from spectre_tiling import calculate_sensor_radius, calculate_coverage, calculate_metrics, calculate_total_energy_consumption, plot_coverage_map, plot_spectre_tiles_with_sensors

# Parameters
GRID_RESOLUTION = 1  # Resolution of the coverage grid
ENERGY_CONSUMPTION_RATE = 1  # Example value for energy consumption per sensor
K_COVERAGE = 2  # Desired k-coverage level

def generate_hierarchical_spectre_tiles(k_coverage):
    tiles_layers = []
    sensor_positions_layers = []
    scale_factor = 1.0
    
    for k in range(k_coverage):
        # Generate tiles with decreasing scale
        scale_factor *= 0.7  # You can adjust this factor to control the scaling between layers
        tiles = buildSpectreBase()
        tiles = buildSupertiles(tiles)  # Generate one level of supertiles
        
        # Scale the tiles
        def scale_transformation(transformation, _):
            scaled_transform = transformation.copy()
            scaled_transform[:2, 2] *= scale_factor
            return scaled_transform
        
        for tile in tiles.values():
            tile.forEachTile(scale_transformation)
        
        tiles_layers.append(tiles)
        
        # Place sensors for this layer
        sensor_positions = place_sensors_inscribed(tiles)
        sensor_positions_layers.append(sensor_positions)
    
    return tiles_layers, sensor_positions_layers

def place_sensors_inscribed(tiles):
    sensor_positions = []
    
    def add_sensor_points(transformation, label):
        nonlocal sensor_positions
        tile_points = [transPt(transformation, pt) for pt in SPECTRE_POINTS]
        centroid = np.mean(tile_points, axis=0)
        sensor_positions.append(centroid)
    
    tiles["Delta"].forEachTile(add_sensor_points)
    return np.array(sensor_positions)

def calculate_hierarchical_coverage(sensor_positions_layers, sensor_radius, grid_resolution):
    all_sensors = np.vstack(sensor_positions_layers)
    x_coords = np.arange(0, np.max(all_sensors[:,0]) + grid_resolution, grid_resolution)
    y_coords = np.arange(0, np.max(all_sensors[:,1]) + grid_resolution, grid_resolution)
    coverage_map = np.zeros((len(x_coords), len(y_coords)))

    for sensor_positions in sensor_positions_layers:
        for sensor in sensor_positions:
            for i, x in enumerate(x_coords):
                for j, y in enumerate(y_coords):
                    if np.linalg.norm(sensor - np.array([x, y])) <= sensor_radius:
                        coverage_map[i, j] += 1

    return x_coords, y_coords, coverage_map

def plot_hierarchical_spectre_tiles_with_sensors(tiles_layers, sensor_positions_layers, sensor_radius):
    fig, ax = plt.subplots(figsize=(15, 15))
    all_points = []

    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']  # Add more colors if needed

    for layer, (tiles, sensor_positions) in enumerate(zip(tiles_layers, sensor_positions_layers)):
        color = colors[layer % len(colors)]
        
        def draw_tile(transformation, label):
            points = [transPt(transformation, pt) for pt in SPECTRE_POINTS]
            all_points.extend(points)
            polygon = mplPolygon(points, closed=True, fill=None, edgecolor=color, alpha=0.5)
            ax.add_patch(polygon)

        tiles["Delta"].forEachTile(draw_tile)

        for sensor_pos in sensor_positions:
            circle = Circle(sensor_pos, sensor_radius, color=color, fill=False, linestyle='dotted', alpha=0.5)
            ax.add_patch(circle)
            ax.plot(sensor_pos[0], sensor_pos[1], 'o', color=color, markersize=2, alpha=0.5)

    if all_points:
        all_points = np.array(all_points)
        x_min, x_max = all_points[:, 0].min(), all_points[:, 0].max()
        y_min, y_max = all_points[:, 1].min(), all_points[:, 1].max()
        x_center, y_center = (x_min + x_max) / 2, (y_min + y_max) / 2
        plot_width, plot_height = x_max - x_min + 20, y_max - y_min + 20

        ax.set_xlim(x_center - plot_width / 2, x_center + plot_width / 2)
        ax.set_ylim(y_center - plot_height / 2, y_center + plot_height / 2)

    ax.set_aspect('equal', adjustable='box')
    plt.grid(True)
    plt.title(f"Hierarchical Spectre Tiling with {K_COVERAGE}-Coverage")
    plt.savefig(f"hierarchical_spectre_tiling_{K_COVERAGE}_coverage.png")
    plt.show()

# Generate hierarchical spectre tiles and sensor positions
tiles_layers, sensor_positions_layers = generate_hierarchical_spectre_tiles(K_COVERAGE)

# Calculate sensor radius (using the base tile size)
example_tile_points = [transPt(np.eye(3), pt) for pt in SPECTRE_POINTS]
SENSOR_RADIUS = calculate_sensor_radius(example_tile_points)

# Calculate and plot the coverage map
x_coords, y_coords, coverage_map = calculate_hierarchical_coverage(sensor_positions_layers, SENSOR_RADIUS, GRID_RESOLUTION)
plot_coverage_map(x_coords, y_coords, coverage_map)

# Calculate metrics
all_sensors = np.vstack(sensor_positions_layers)
sensor_density, rate_of_overlap, coverage_quality = calculate_metrics(all_sensors, coverage_map)
total_energy_consumption = calculate_total_energy_consumption(all_sensors)

# Print metrics
print(f"Desired k-coverage: {K_COVERAGE}")
print(f"Sensor density: {sensor_density:.6f} sensors per unit area")
print(f"Rate of overlap: {rate_of_overlap:.6f}")
print(f"Coverage quality: {coverage_quality:.6f}")
print(f"Total energy consumption: {total_energy_consumption:.2f} units")
print(f"Total number of sensors: {len(all_sensors)}")
print(f"Sensors per layer: {[len(layer) for layer in sensor_positions_layers]}")

# Plot the hierarchical spectre tiles with sensor nodes
plot_hierarchical_spectre_tiles_with_sensors(tiles_layers, sensor_positions_layers, SENSOR_RADIUS)