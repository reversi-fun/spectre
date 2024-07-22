import numpy as np
import matplotlib.pyplot as plt
from network_generation import generate_hexagonal_network, generate_triangular_network, generate_square_network, SENSOR_RADIUS

def plot_network(sensor_positions, title):
    x, y = zip(*sensor_positions)
    plt.figure(figsize=(6, 6))
    plt.scatter(x, y)
    plt.title(title)
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.grid(True)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()

num_sensors = 559
sensor_radius = SENSOR_RADIUS

# Generate networks
hexagonal_network = generate_hexagonal_network(num_sensors, sensor_radius)
triangular_network = generate_triangular_network(num_sensors, sensor_radius)
square_network = generate_square_network(num_sensors, sensor_radius)

# Plot networks
plot_network(hexagonal_network, 'Hexagonal Network')
plot_network(triangular_network, 'Triangular Network')
plot_network(square_network, 'Square Network')
