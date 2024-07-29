# network_generation.py

import numpy as np
from securitymetricsaperiodic_hexagonal import generate_aperiodic_network, transPt, SPECTRE_POINTS

# Parameters
SENSOR_RADIUS = 10

def generate_hexagonal_network(num_sensors, sensor_radius):
    """Generate a hexagonal network of sensors."""
    sensor_positions = []
    hex_height = np.sqrt(3) * sensor_radius
    x_offset = 1.5 * sensor_radius
    num_rows = int(np.ceil(np.sqrt(num_sensors)))
    num_cols = int(np.ceil(num_sensors / num_rows))

    for x in range(num_cols):
        for y in range(num_rows):
            center_x = x * x_offset
            center_y = y * hex_height + (x % 2) * hex_height / 2
            sensor_positions.append((center_x, center_y))
            if len(sensor_positions) >= num_sensors:
                return np.array(sensor_positions)
    
    return np.array(sensor_positions)

def generate_triangular_network(num_sensors, sensor_radius):
    """Generate a triangular network of sensors."""
    sensor_positions = []
    row = 0
    col = 0
    y_offset = np.sqrt(3) * sensor_radius
    x_offset = 1.5 * sensor_radius
    while len(sensor_positions) < num_sensors:
        x = col * x_offset
        y = row * y_offset
        sensor_positions.append((x, y))
        col += 1
        if col * x_offset > np.sqrt(num_sensors) * x_offset:
            row += 1
            if row % 2 == 0:
                col = 0
            else:
                col = 0.5
    return np.array(sensor_positions)[:num_sensors]

def generate_square_network(num_sensors, sensor_radius):
    """Generate a square network of sensors."""
    sensor_positions = []
    side_length = int(np.ceil(np.sqrt(num_sensors)))
    x_offset = sensor_radius
    y_offset = sensor_radius
    for i in range(side_length):
        for j in range(side_length):
            sensor_positions.append((i * x_offset, j * y_offset))
            if len(sensor_positions) >= num_sensors:
                break
        if len(sensor_positions) >= num_sensors:
            break
    return np.array(sensor_positions)[:num_sensors]

def main():
    # Example usage
    num_sensors = 71
    sensor_radius = SENSOR_RADIUS
    
    aperiodic_network = generate_aperiodic_network(sensor_radius, num_sensors, 3)
    hexagonal_network = generate_hexagonal_network(num_sensors, sensor_radius)
    triangular_network = generate_triangular_network(num_sensors, sensor_radius)
    square_network = generate_square_network(num_sensors, sensor_radius)

    print("Aperiodic Network:", aperiodic_network[:5])  # Print first 5 for brevity
    print("Hexagonal Network:", hexagonal_network[:5])
    print("Triangular Network:", triangular_network[:5])
    print("Square Network:", square_network[:5])

if __name__ == "__main__":
    main()
