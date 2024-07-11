import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as mplPolygon, Circle
from matplotlib.colors import ListedColormap
from spectre import buildSpectreBase, transPt, buildSupertiles, SPECTRE_POINTS, Edge_a, Edge_b

# Parameters
GRID_RESOLUTION = 1  # Resolution of the coverage grid
ENERGY_CONSUMPTION_RATE = 1  # Example value for energy consumption per sensor
K_COVERAGE = 3  # Desired k-coverage level

def generate_hierarchical_spectre_tiles(k_coverage):
    tiles_layers = []
    sensor_positions_layers = []
    scale_factor = 1.0
    
    for k in range(k_coverage):
        # Generate tiles with decreasing scale
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
        
        # Reduce scale for the next layer
        scale_factor *= 0.8
    
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

def calculate_sensor_radius(tile_points):
    # Calculate the maximum distance from the centroid to any vertex
    centroid = np.mean(tile_points, axis=0)
    distances = [np.linalg.norm(point - centroid) for point in tile_points]
    return max(distances)

def calculate_hierarchical_coverage(sensor_positions_layers, sensor_radius, grid_resolution):
    all_sensors = np.vstack(sensor_positions_layers)
    x_min, x_max = np.min(all_sensors[:,0]), np.max(all_sensors[:,0])
    y_min, y_max = np.min(all_sensors[:,1]), np.max(all_sensors[:,1])
    
    x_coords = np.arange(x_min, x_max + grid_resolution, grid_resolution)
    y_coords = np.arange(y_min, y_max + grid_resolution, grid_resolution)
    coverage_map = np.zeros((len(y_coords), len(x_coords)), dtype=int)

    for sensor_positions in sensor_positions_layers:
        for sensor in sensor_positions:
            x_indices = np.where(np.abs(x_coords - sensor[0]) <= sensor_radius)[0]
            y_indices = np.where(np.abs(y_coords - sensor[1]) <= sensor_radius)[0]
            for i in y_indices:
                for j in x_indices:
                    if np.linalg.norm(sensor - np.array([x_coords[j], y_coords[i]])) <= sensor_radius:
                        coverage_map[i, j] += 1

    return x_coords, y_coords, coverage_map

def plot_coverage_map(x_coords, y_coords, coverage_map):
    plt.figure(figsize=(12, 10))
    plt.imshow(coverage_map, extent=[x_coords.min(), x_coords.max(), y_coords.min(), y_coords.max()], 
               origin='lower', cmap='viridis', interpolation='nearest')
    plt.colorbar(label='Coverage Level')
    plt.title(f'Coverage Map (Desired k-coverage: {K_COVERAGE})')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.savefig(f"coverage_map_{K_COVERAGE}_coverage.png")
    plt.close()

def plot_hierarchical_spectre_tiles_with_sensors(tiles_layers, sensor_positions_layers, sensor_radius):
    fig, ax = plt.subplots(figsize=(15, 15))
    colors = plt.cm.rainbow(np.linspace(0, 1, len(tiles_layers)))

    for layer, (tiles, sensor_positions, color) in enumerate(zip(tiles_layers, sensor_positions_layers, colors)):
        def draw_tile(transformation, label):
            points = [transPt(transformation, pt) for pt in SPECTRE_POINTS]
            polygon = mplPolygon(points, closed=True, fill=None, edgecolor=color, alpha=0.5)
            ax.add_patch(polygon)

        tiles["Delta"].forEachTile(draw_tile)

        for sensor_pos in sensor_positions:
            circle = Circle(sensor_pos, sensor_radius, color=color, fill=False, linestyle='dotted', alpha=0.5)
            ax.add_patch(circle)
            ax.plot(sensor_pos[0], sensor_pos[1], 'o', color=color, markersize=2, alpha=0.5)

    ax.set_aspect('equal', adjustable='box')
    plt.grid(True)
    plt.title(f"Hierarchical Spectre Tiling with {K_COVERAGE}-Coverage")
    plt.savefig(f"hierarchical_spectre_tiling_{K_COVERAGE}_coverage.png")
    plt.close()

def calculate_metrics(sensor_positions, coverage_map):
    total_area = coverage_map.size
    covered_area = np.sum(coverage_map > 0)
    k_covered_area = np.sum(coverage_map >= K_COVERAGE)
    
    sensor_density = len(sensor_positions) / total_area
    coverage_ratio = covered_area / total_area
    k_coverage_ratio = k_covered_area / total_area
    
    return sensor_density, coverage_ratio, k_coverage_ratio

def main(k_coverage=3, n_iterations=3):
    print(f"Generating hierarchical Spectre tiles for {k_coverage}-coverage with {n_iterations} iterations")
    
    # Generate hierarchical spectre tiles and sensor positions
    tiles_layers, sensor_positions_layers = generate_hierarchical_spectre_tiles(k_coverage, n_iterations)

    # Print number of sensors for each iteration
    for i, layer in enumerate(sensor_positions_layers):
        print(f"Iteration {i+1}: {len(layer)} sensors")

    # Calculate sensor radius (using the base tile size)
    example_tile_points = [transPt(np.eye(3), pt) for pt in SPECTRE_POINTS]
    SENSOR_RADIUS = calculate_sensor_radius(example_tile_points)

    # Calculate and plot the coverage map
    x_coords, y_coords, coverage_map = calculate_hierarchical_coverage(sensor_positions_layers, SENSOR_RADIUS, GRID_RESOLUTION)
    
    plt.figure(figsize=(12, 10))
    plt.imshow(coverage_map, extent=[x_coords.min(), x_coords.max(), y_coords.min(), y_coords.max()], 
               origin='lower', cmap='viridis', interpolation='nearest')
    plt.colorbar(label='Coverage Level')
    plt.title(f'Coverage Map (Desired k-coverage: {k_coverage})')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.show()

    # Plot the hierarchical spectre tiles with sensor nodes
    plt.figure(figsize=(15, 15))
    ax = plt.gca()
    colors = plt.cm.rainbow(np.linspace(0, 1, len(tiles_layers)))

    for layer, (tiles, sensor_positions, color) in enumerate(zip(tiles_layers, sensor_positions_layers, colors)):
        def draw_tile(transformation, label):
            points = [transPt(transformation, pt) for pt in SPECTRE_POINTS]
            polygon = mplPolygon(points, closed=True, fill=None, edgecolor=color, alpha=0.5)
            ax.add_patch(polygon)

        tiles["Delta"].forEachTile(draw_tile)

        for sensor_pos in sensor_positions:
            circle = Circle(sensor_pos, SENSOR_RADIUS, color=color, fill=False, linestyle='dotted', alpha=0.5)
            ax.add_patch(circle)
            ax.plot(sensor_pos[0], sensor_pos[1], 'o', color=color, markersize=2, alpha=0.5)

    ax.set_aspect('equal', adjustable='box')
    plt.grid(True)
    plt.title(f"Hierarchical Spectre Tiling with {k_coverage}-Coverage")
    plt.show()

    # Calculate metrics
    all_sensors = np.vstack(sensor_positions_layers)
    sensor_density, coverage_ratio, k_coverage_ratio = calculate_metrics(all_sensors, coverage_map)

    # Print metrics
    print(f"Desired k-coverage: {k_coverage}")
    print(f"Number of iterations: {n_iterations}")
    print(f"Sensor density: {sensor_density:.6f} sensors per unit area")
    print(f"Coverage ratio: {coverage_ratio:.6f}")
    print(f"{k_coverage}-coverage ratio: {k_coverage_ratio:.6f}")
    print(f"Total number of sensors: {len(all_sensors)}")
    print(f"Sensors per layer: {[len(layer) for layer in sensor_positions_layers]}")

if __name__ == "__main__":
    main(k_coverage=3, n_iterations=3)  # You can change these parameters as needed