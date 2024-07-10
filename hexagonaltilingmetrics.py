import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon, Circle
from matplotlib.colors import ListedColormap

# Parameters
GRID_RESOLUTION = 1  # Resolution of the coverage grid
HEX_SENSOR_RADIUS = 10  # This will be updated based on the Spectre radius

def generate_hexagonal_grid(sensor_radius, grid_size):
    hex_height = np.sqrt(3) * sensor_radius
    sensor_positions = []
    for x in range(-grid_size, grid_size + 1):
        for y in range(-grid_size, grid_size + 1):
            center_x = x * 1.5 * sensor_radius
            center_y = y * hex_height + (x % 2) * hex_height / 2
            sensor_positions.append((center_x, center_y))
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

def calculate_metrics(sensor_positions, coverage_map):
    total_area = coverage_map.size
    covered_area = np.sum(coverage_map > 0)
    sensor_density = len(sensor_positions) / total_area
    
    overlap_sum = np.sum(coverage_map) - covered_area
    rate_of_overlap = overlap_sum / total_area
    coverage_quality = 1 / rate_of_overlap if rate_of_overlap > 0 else float('inf')
    
    return sensor_density, rate_of_overlap, coverage_quality

def calculate_total_energy_consumption(sensor_positions):
    ENERGY_CONSUMPTION_RATE = 1  # Example value
    return len(sensor_positions) * ENERGY_CONSUMPTION_RATE

def plot_coverage_map(x_coords, y_coords, coverage_map):
    fig, ax = plt.subplots(figsize=(15, 15))
    cmap = ListedColormap(['white', 'lightblue', 'blue', 'darkblue', 'purple'])
    c = ax.pcolormesh(x_coords, y_coords, coverage_map.T, shading='auto', cmap=cmap)
    fig.colorbar(c, ax=ax, ticks=np.arange(0, np.max(coverage_map) + 1, 1))
    ax.set_aspect('equal', adjustable='box')
    plt.title("Coverage Map for Hexagonal Tiling")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.show()

def plot_hexagonal_grid_with_sensors(sensor_positions, sensor_radius):
    fig, ax = plt.subplots(figsize=(15, 15))
    for sensor_pos in sensor_positions:
        hexagon = RegularPolygon(sensor_pos, numVertices=6, radius=sensor_radius / np.sqrt(3), orientation=np.radians(30), edgecolor='b', fill=None)
        ax.add_patch(hexagon)
        circle = Circle(sensor_pos, sensor_radius, color='r', fill=False, linestyle='dotted')
        ax.add_patch(circle)
        ax.plot(sensor_pos[0], sensor_pos[1], 'ko', markersize=2)
    
    ax.set_aspect('equal', adjustable='box')
    plt.grid(True)
    plt.title("Hexagonal Grid with Sensors")
    plt.savefig("hexagonal_grid_with_sensors.png")
    plt.show()

# Generate hexagonal grid with the same sensor radius as the Spectre tiles
sensor_positions = generate_hexagonal_grid(HEX_SENSOR_RADIUS, grid_size=15)

# Calculate and plot the coverage map
x_coords, y_coords, coverage_map = calculate_coverage(sensor_positions, HEX_SENSOR_RADIUS, GRID_RESOLUTION)
plot_coverage_map(x_coords, y_coords, coverage_map)

# Calculate metrics
sensor_density, rate_of_overlap, coverage_quality = calculate_metrics(sensor_positions, coverage_map)
total_energy_consumption = calculate_total_energy_consumption(sensor_positions)

# Print metrics
print(f"Sensor density: {sensor_density:.6f} sensors per unit area")
print(f"Rate of overlap: {rate_of_overlap:.6f}")
print(f"Coverage quality: {coverage_quality:.6f}")
print(f"Total energy consumption: {total_energy_consumption:.2f} units")

# Plot the hexagonal grid with sensor nodes
plot_hexagonal_grid_with_sensors(sensor_positions, HEX_SENSOR_RADIUS)
