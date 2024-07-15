import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as mplPolygon, Circle
from matplotlib.colors import ListedColormap
from spectre import buildSpectreBase, transPt, buildSupertiles, SPECTRE_POINTS

# Parameters
GRID_RESOLUTION = 1
ENERGY_CONSUMPTION_RATE = 1
MAX_ITERATIONS = 100  # Increase for a more thorough optimization
DUTY_CYCLE = 0.5  # Example duty cycle: 50% on, 50% off

def calculate_sensor_radius(tile_points):
    longest_distance = max(np.linalg.norm(pt - np.mean(tile_points, axis=0)) for pt in tile_points)
    return longest_distance

def generate_spectre_tiles():
    tiles = buildSpectreBase()
    iterations = 0
    sensor_counts = []
    
    while iterations < MAX_ITERATIONS:
        tiles = buildSupertiles(tiles)
        sensor_positions = place_sensors_inscribed(tiles)
        sensor_counts.append(len(sensor_positions))
        iterations += 1
        print(f"Iteration {iterations} completed. Number of sensors: {len(sensor_positions)}")
    
    return tiles, sensor_counts

def place_sensors_inscribed(tiles):
    sensor_positions = []
    
    def add_sensor_points(transformation, label):
        nonlocal sensor_positions
        tile_points = [transPt(transformation, pt) for pt in SPECTRE_POINTS]
        centroid = np.mean(tile_points, axis=0)
        sensor_positions.append((centroid[0], centroid[1], calculate_sensor_radius(tile_points)))
    
    tiles["Delta"].forEachTile(add_sensor_points)
    return sensor_positions

def calculate_coverage(sensor_positions, sensor_radius, grid_resolution):
    x_coords = np.arange(0, int(np.max(sensor_positions[:,0])) + grid_resolution, grid_resolution)
    y_coords = np.arange(0, int(np.max(sensor_positions[:,1])) + grid_resolution, grid_resolution)
    coverage_map = np.zeros((len(x_coords), len(y_coords)))

    for sensor in sensor_positions:
        for i, x in enumerate(x_coords):
            for j, y in enumerate(y_coords):
                if np.linalg.norm(sensor[:2] - np.array([x, y])) <= sensor_radius:
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

def calculate_total_energy_consumption(sensor_positions, duty_cycle):
    return len(sensor_positions) * ENERGY_CONSUMPTION_RATE * duty_cycle

def plot_coverage_map(x_coords, y_coords, coverage_map):
    fig, ax = plt.subplots(figsize=(15, 15))
    cmap = ListedColormap(['white', 'lightblue', 'blue', 'darkblue', 'purple'])
    c = ax.pcolormesh(x_coords, y_coords, coverage_map.T, shading='auto', cmap=cmap)
    fig.colorbar(c, ax=ax, ticks=np.arange(0, np.max(coverage_map) + 1, 1))
    ax.set_aspect('equal', adjustable='box')
    plt.title("Coverage Map")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.show()

def plot_spectre_tiles_with_sensors(tiles, sensor_positions, sensor_radius):
    fig, ax = plt.subplots(figsize=(15, 15))
    all_points = []

    def draw_tile(transformation, label):
        points = [transPt(transformation, pt) for pt in SPECTRE_POINTS]
        all_points.extend(points)
        polygon = mplPolygon(points, closed=True, fill=None, edgecolor='b')
        ax.add_patch(polygon)

    tiles["Delta"].forEachTile(draw_tile)

    for sensor_pos in sensor_positions:
        circle = Circle(sensor_pos[:2], sensor_pos[2], color='r', fill=False, linestyle='dotted')
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

# Generate spectre tiles and count sensors per iteration
tiles, sensor_counts = generate_spectre_tiles()

# Place sensors inscribed within each tile
sensor_positions = place_sensors_inscribed(tiles)
sensor_positions = np.array(sensor_positions)

# Calculate sensor radius
example_tile_points = [transPt(np.eye(3), pt) for pt in SPECTRE_POINTS]
SENSOR_RADIUS = calculate_sensor_radius(example_tile_points)

# Calculate and plot the coverage map
x_coords, y_coords, coverage_map = calculate_coverage(sensor_positions, SENSOR_RADIUS, GRID_RESOLUTION)
plot_coverage_map(x_coords, y_coords, coverage_map)

# Calculate metrics
sensor_density, rate_of_overlap, coverage_quality = calculate_metrics(sensor_positions, coverage_map)
total_energy_consumption = calculate_total_energy_consumption(sensor_positions, DUTY_CYCLE)

# Print metrics
print(f"Sensor density: {sensor_density:.6f} sensors per unit area")
print(f"Rate of overlap: {rate_of_overlap:.6f}")
print(f"Coverage quality: {coverage_quality:.6f}")
print(f"Total energy consumption: {total_energy_consumption:.2f} units")
print(f"Number of iterations: {MAX_ITERATIONS}")
print(f"Sensors per iteration: {sensor_counts}")

# Plot the spectre tiles with sensor nodes
plot_spectre_tiles_with_sensors(tiles, sensor_positions, SENSOR_RADIUS)

### Fitness-Based DPSA Optimization with Duty Cycling ###

class FitnessBasedDPSA:
    def __init__(self, sensor_positions, pop_size, max_iter, duty_cycle):
        self.sensor_positions = sensor_positions
        self.pop_size = pop_size
        self.max_iter = max_iter
        self.duty_cycle = duty_cycle
        self.dim = sensor_positions.shape[0] * 2  # Each sensor has x and y coordinates

        # PSO Parameters
        self.w = 0.7
        self.c1 = 1.5
        self.c2 = 1.5

        # DE Parameters
        self.F = 0.8
        self.CR = 0.9

        # Initialize particle positions and velocities
        self.X = np.array([sensor[:2] for sensor in self.sensor_positions] * pop_size).reshape(pop_size, -1)
        self.V = np.zeros((self.pop_size, self.dim))
        self.pbest = self.X.copy()
        self.sensor_states = np.ones((self.pop_size, len(sensor_positions)), dtype=bool)
        self.pbest_fitness = np.array([self.fitness(p, self.sensor_states[i]) for i, p in enumerate(self.pbest)])
        self.gbest = self.pbest[np.argmin(self.pbest_fitness)]
        self.gbest_fitness = np.min(self.pbest_fitness)

    def coverage(self, positions, states):
        # Calculate the total covered area by the sensors
        covered_points = set()
        for i in range(0, len(positions), 2):
            if states[i // 2]:  # Only consider sensors that are turned on
                x, y = int(positions[i]), int(positions[i + 1])
                radius = int(SENSOR_RADIUS)  # Cast radius to int
                for dx in range(-radius, radius + 1):
                    for dy in range(-radius, radius + 1):
                        if dx**2 + dy**2 <= radius**2:
                            covered_points.add((x + dx, y + dy))
        return len(covered_points)

    def fitness(self, positions, states):
        # The fitness is a combination of coverage and energy consumption
        coverage_area = self.coverage(positions, states)
        energy_consumption = np.sum(states) * ENERGY_CONSUMPTION_RATE * self.duty_cycle
        return -coverage_area + energy_consumption

    def optimize(self):
        fitness_scores = []  # List to store fitness scores over iterations
        for iteration in range(self.max_iter):
            for i in range(self.pop_size):
                # PSO Update for Poor Fitness
                r1, r2 = np.random.rand(self.dim), np.random.rand(self.dim)
                pbest_diff = self.pbest[i] - self.X[i]
                gbest_diff = self.gbest - self.X[i]
                self.V[i] = self.w * self.V[i] + self.c1 * r1 * pbest_diff + self.c2 * r2 * gbest_diff
                pso_position = self.X[i] + self.V[i]

                # DE Mutation and Crossover for Good Fitness
                idxs = [idx for idx in range(self.pop_size) if idx != i]
                a, b, c = self.X[np.random.choice(idxs, 3, replace=False)]
                mutant = np.clip(a + self.F * (b - c), 0, None)

                cross_points = np.random.rand(self.dim) < self.CR
                de_position = np.where(cross_points, mutant, self.X[i])

                # Fitness-Based Hybrid Update
                if self.pbest_fitness[i] > np.median(self.pbest_fitness):
                    # Poor fitness - use PSO update
                    hybrid_position = pso_position
                else:
                    # Good fitness - use DE update
                    hybrid_position = de_position

                # Determine sensor states based on fitness
                states = self.sensor_states[i].copy()
                for j in range(len(states)):
                    if np.random.rand() > self.duty_cycle:
                        states[j] = False  # Turn off the sensor

                # Evaluate fitness
                fitness = self.fitness(hybrid_position, states)

                # Update personal best
                if fitness < self.pbest_fitness[i]:
                    self.pbest[i] = hybrid_position
                    self.pbest_fitness[i] = fitness
                    self.sensor_states[i] = states

                # Update global best
                if fitness < self.gbest_fitness:
                    self.gbest = hybrid_position
                    self.gbest_fitness = fitness

                # Update particle position
                self.X[i] = hybrid_position

            # Adaptive Mechanisms
            self.w *= 0.99
            self.F = 0.5 + 0.3 * np.sin(np.pi * iteration / self.max_iter)
            self.CR = 0.9 - 0.5 * np.cos(np.pi * iteration / self.max_iter)

            # Collect fitness score for current iteration
            fitness_scores.append(-self.gbest_fitness)  # Append negative because we want to maximize fitness

        return self.gbest, -self.gbest_fitness, fitness_scores

# Example usage
pop_size = 100
max_iter = 10
duty_cycle = DUTY_CYCLE

optimizer = FitnessBasedDPSA(sensor_positions, pop_size, max_iter, duty_cycle)
best_solution, best_coverage, fitness_scores = optimizer.optimize()

# Plot fitness scores over iterations
plt.figure(figsize=(10, 6))
plt.plot(range(1, max_iter + 1), fitness_scores, marker='o', linestyle='-', color='b', label='Fitness Score')
plt.title('Fitness of Sensor Network Over Iterations')
plt.xlabel('Iteration')
plt.ylabel('Fitness Score')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

print(f"Best solution: {best_solution}\nBest coverage: {best_coverage}")
