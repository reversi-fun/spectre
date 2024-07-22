import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from spectre import buildSpectreBase, transPt, buildSupertiles, SPECTRE_POINTS
import scienceplots

plt.style.use(['science', 'ieee'])
plt.rcParams.update({'figure.dpi': 300})

# Parameters
MAX_ITERATIONS = 4
DEFAULT_SENSOR_RADIUS = 10  # Default sensor radius

def calculate_sensor_radius(tile_points):
    longest_distance = max(np.linalg.norm(pt - np.mean(tile_points, axis=0)) for pt in tile_points)
    return longest_distance

def generate_spectre_tiles(n_iterations):
    tiles = buildSpectreBase()
    for _ in range(n_iterations):
        tiles = buildSupertiles(tiles)
    return tiles

def place_sensors_inscribed(tiles, scaling_factor):
    sensor_positions = []
    
    def add_sensor_points(transformation, label):
        nonlocal sensor_positions
        scaled_transformation = transformation @ np.diag([scaling_factor, scaling_factor, 1])
        tile_points = [transPt(scaled_transformation, pt) for pt in SPECTRE_POINTS]
        centroid = np.mean(tile_points, axis=0)
        sensor_positions.append(centroid)
    
    tiles["Delta"].forEachTile(add_sensor_points)
    return sensor_positions

def calculate_coverage(sensor_positions, sensor_radius):
    x_min = min(sensor[0] for sensor in sensor_positions) - sensor_radius
    x_max = max(sensor[0] for sensor in sensor_positions) + sensor_radius
    y_min = min(sensor[1] for sensor in sensor_positions) - sensor_radius
    y_max = max(sensor[1] for sensor in sensor_positions) + sensor_radius
    
    grid_resolution = sensor_radius / 10
    x_coords = np.arange(x_min, x_max, grid_resolution)
    y_coords = np.arange(y_min, y_max, grid_resolution)
    coverage_map = np.zeros((len(x_coords), len(y_coords)))
    
    for sensor in sensor_positions:
        for i, x in enumerate(x_coords):
            for j, y in enumerate(y_coords):
                if np.linalg.norm(sensor - np.array([x, y])) <= sensor_radius:
                    coverage_map[i, j] += 1
    
    return coverage_map

def calculate_metrics(sensor_positions, coverage_map, sensor_radius):
    covered_area = np.sum(coverage_map > 0) * (sensor_radius / 10)**2
    sensor_density = len(sensor_positions) / covered_area if covered_area > 0 else float('inf')
    return sensor_density

def calculate_rate_of_overlap(tile_area, circle_area):
    rate_of_overlap = (circle_area - tile_area) / circle_area
    coverage_quality = 1 / rate_of_overlap if rate_of_overlap > 0 else float('inf')
    return rate_of_overlap, coverage_quality

def calculate_spectre_area():
    polygon = Polygon(SPECTRE_POINTS)
    return polygon.area

def calculate_total_energy_consumption(sensor_positions):
    ENERGY_CONSUMPTION_RATE = 1
    return len(sensor_positions) * ENERGY_CONSUMPTION_RATE

# Prepare to collect data
iterations = range(1, MAX_ITERATIONS + 1)
sensor_densities = []
supertile_areas = []

example_tile_points = [transPt(np.eye(3), pt) for pt in SPECTRE_POINTS]
DEFAULT_SENSOR_RADIUS = calculate_sensor_radius(example_tile_points)

# Calculate scaling factor based on the sensor radius
scaling_factor = 1  # Using default sensor radius for scaling factor

# Calculate metrics for each iteration
for n_iter in iterations:
    tiles = generate_spectre_tiles(n_iter)
    sensor_positions = place_sensors_inscribed(tiles, scaling_factor)
    coverage_map = calculate_coverage(sensor_positions, DEFAULT_SENSOR_RADIUS)
    sensor_density = calculate_metrics(sensor_positions, coverage_map, DEFAULT_SENSOR_RADIUS)
    sensor_densities.append(sensor_density)
    supertile_areas.append(np.sum(coverage_map > 0) * (DEFAULT_SENSOR_RADIUS / 10)**2)

# Plot sensor density vs. iterations
with plt.style.context(['science', 'ieee']):
    fig, ax = plt.subplots()
    ax.plot(iterations, sensor_densities, marker='o', label='Sensor Density')
    ax.set_xlabel('Number of Iterations')
    ax.set_ylabel('Sensor Density (sensors per unit area)')
    ax.legend(title='Metrics')
    ax.autoscale(tight=True)
    plt.title('Sensor Density vs. Number of Iterations')
    plt.savefig('sensor_density_vs_iterations.png', dpi=300)
    plt.show()
