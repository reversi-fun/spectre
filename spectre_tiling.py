import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as mplPolygon, Circle
from matplotlib.colors import ListedColormap
from shapely.geometry import Polygon
from spectre import buildSpectreBase, transPt, MetaTile, buildSupertiles, SPECTRE_POINTS

# Parameters
N_ITERATIONS = 1
GRID_RESOLUTION = 1  # Resolution of the coverage grid
SENSOR_RADIUS = 10  # Sensor radius in meters

def calculate_scaling_factor(tile_points, desired_radius):
    """Calculate the scaling factor to fit the tile within the desired sensor radius."""
    centroid = np.mean(tile_points, axis=0)
    longest_distance = max(np.linalg.norm(pt - centroid) for pt in tile_points)
    scaling_factor = desired_radius / longest_distance
    return scaling_factor

def scale_tile_points(tile_points, scaling_factor):
    """Scale the tile points using the scaling factor."""
    scaled_points = [scaling_factor * pt for pt in tile_points]
    return scaled_points

def apply_scaling_to_transformations(transformations, scaling_factor):
    """Apply scaling factor to the transformation matrices."""
    scaled_transformations = [transformation * scaling_factor for transformation in transformations]
    return scaled_transformations

def generate_spectre_tiles(n_iterations, scaling_factor):
    """Generate Spectre tiles for the given number of iterations and apply scaling."""
    tiles = buildSpectreBase()
    for _ in range(n_iterations):
        tiles = buildSupertiles(tiles)
    
    # Apply scaling to all transformations in the tiles
    for key in tiles:
        tile = tiles[key]
        if isinstance(tile, MetaTile):
            tile.transformations = apply_scaling_to_transformations(tile.transformations, scaling_factor)
    
    return tiles

def place_sensors_inscribed(tiles, scaling_factor):
    """Place sensors inscribed within each tile."""
    sensor_positions = []
    
    def add_sensor_points(transformation, label):
        nonlocal sensor_positions
        scaled_transformation = transformation * scaling_factor
        tile_points = [transPt(scaled_transformation, pt) for pt in SPECTRE_POINTS]
        centroid = np.mean(tile_points, axis=0)
        sensor_positions.append(centroid)
    
    tiles["Delta"].forEachTile(add_sensor_points)
    return sensor_positions

def calculate_coverage(sensor_positions, sensor_radius, grid_resolution):
    """Calculate the coverage map based on sensor positions and sensor radius."""
    x_coords = np.arange(-200, 200, grid_resolution)
    y_coords = np.arange(-200, 200, grid_resolution)
    coverage_map = np.zeros((len(x_coords), len(y_coords)))
    
    for sensor in sensor_positions:
        for i, x in enumerate(x_coords):
            for j, y in enumerate(y_coords):
                if np.linalg.norm(sensor - np.array([x, y])) <= sensor_radius:
                    coverage_map[i, j] += 1
    
    return x_coords, y_coords, coverage_map

def calculate_metrics(sensor_positions, coverage_map):
    """Calculate the sensor network metrics."""
    covered_area = np.sum(coverage_map > 0)
    sensor_density = len(sensor_positions) / covered_area
    
    overlap_sum = np.sum(coverage_map) - covered_area
    rate_of_overlap = overlap_sum / covered_area
    coverage_quality = 1 / rate_of_overlap if rate_of_overlap > 0 else float('inf')
    
    return sensor_density, rate_of_overlap, coverage_quality

def calculate_total_energy_consumption(sensor_positions):
    """Calculate the total energy consumption of the sensor network."""
    ENERGY_CONSUMPTION_RATE = 1  # Example value
    return len(sensor_positions) * ENERGY_CONSUMPTION_RATE

def calculate_rate_of_overlap(sensor_radius, tile_area):
    """Calculate the rate of overlap based on sensor radius and tile area."""
    circle_area = np.pi * sensor_radius**2
    rate_of_overlap = (circle_area - tile_area) / circle_area
    return rate_of_overlap

def calculate_spectre_area(scaled_points):
    """Calculate the area of the scaled Spectre tile."""
    polygon = Polygon(scaled_points)
    return polygon.area

def plot_coverage_map(x_coords, y_coords, coverage_map):
    """Plot the coverage map."""
    fig, ax = plt.subplots(figsize=(15, 15))
    cmap = ListedColormap(['white', 'lightblue', 'blue', 'darkblue', 'purple'])
    c = ax.pcolormesh(x_coords, y_coords, coverage_map.T, shading='auto', cmap=cmap)
    fig.colorbar(c, ax=ax, ticks=np.arange(0, np.max(coverage_map) + 1, 1))
    
    # Calculate the range of x and y coordinates
    x_range = max(x_coords) - min(x_coords)
    y_range = max(y_coords) - min(y_coords)
    
    # Set the aspect ratio to 'equal' and adjust the limits to center the plot
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlim(min(x_coords) - x_range * 0.1, max(x_coords) + x_range * 0.1)
    ax.set_ylim(min(y_coords) - y_range * 0.1, max(y_coords) + y_range * 0.1)
    
    plt.title("Coverage Map")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.tight_layout()  # Adjust the layout to prevent clipping
    plt.show()

def plot_spectre_tiles_with_sensors(tiles, sensor_positions, sensor_radius, scaling_factor):
    """Plot Spectre tiles with sensors inscribed."""
    fig, ax = plt.subplots(figsize=(15, 15))
    all_points = []

    def draw_tile(transformation, label):
        scaled_transformation = transformation * scaling_factor
        points = [transPt(scaled_transformation, pt) for pt in SPECTRE_POINTS]
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

# Generate spectre tiles
example_tile_points = [transPt(np.eye(3), pt) for pt in SPECTRE_POINTS]  # Using identity matrix for transformation
scaling_factor = calculate_scaling_factor(example_tile_points, SENSOR_RADIUS)
tiles = generate_spectre_tiles(N_ITERATIONS, scaling_factor)

# Place sensors inscribed within each tile
sensor_positions = place_sensors_inscribed(tiles, scaling_factor)

# Calculate and plot the coverage map
x_coords, y_coords, coverage_map = calculate_coverage(sensor_positions, SENSOR_RADIUS, GRID_RESOLUTION)
plot_coverage_map(x_coords, y_coords, coverage_map)

# Calculate metrics
sensor_density, rate_of_overlap, coverage_quality = calculate_metrics(sensor_positions, coverage_map)
total_energy_consumption = calculate_total_energy_consumption(sensor_positions)

# Calculate rate of overlap based on tile area
scaled_tile_points = scale_tile_points(example_tile_points, scaling_factor)
spectre_area = calculate_spectre_area(scaled_tile_points)
rate_of_overlap = calculate_rate_of_overlap(SENSOR_RADIUS, spectre_area)

# Print metrics
print(f"Sensor density: {sensor_density:.6f} sensors per unit area")
print(f"Rate of overlap: {rate_of_overlap:.6f}")
print(f"Coverage quality: {coverage_quality:.6f}")
print(f"Total energy consumption: {total_energy_consumption:.2f} units")
# Calculate and print additional metrics
print(f"Sensor radius: {SENSOR_RADIUS:.2f} units")
print(f"Number of sensors: {len(sensor_positions)}")
total_area = np.sum(coverage_map > 0) * GRID_RESOLUTION**2
print(f"Total covered area: {total_area:.2f} square units")
print(f"Estimated supertile area: {total_area:.2f} square units")

# Plot the spectre tiles with sensor nodes
plot_spectre_tiles_with_sensors(tiles, sensor_positions, SENSOR_RADIUS, scaling_factor)
