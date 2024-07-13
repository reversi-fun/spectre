# metrics_calculation.py

import numpy as np
from intruder_attack_simulation import simulate_intruder_attack
from network_generation import generate_aperiodic_network, generate_hexagonal_network, generate_triangular_network, generate_square_network
import random

# Parameters
SENSOR_RADIUS = 10
DETECTION_THRESHOLD = 0.1  # Threshold for considering a detection as positive

def calculate_detection_rate(network, intruder_path):
    detected_positions = []
    for position in intruder_path:
        detecting_sensors = [sensor for sensor in network if np.linalg.norm(np.array(sensor) - np.array(position)) <= SENSOR_RADIUS]
        if detecting_sensors:
            detected_positions.append(position)
    
    detection_rate = len(detected_positions) / len(intruder_path)
    return detection_rate

def calculate_false_positives_negatives(network, intruder_path, detection_radius=SENSOR_RADIUS):
    false_positives = 0
    false_negatives = 0
    for position in intruder_path:
        detecting_sensors = [sensor for sensor in network if np.linalg.norm(np.array(sensor) - np.array(position)) <= detection_radius]
        if detecting_sensors:
            if np.random.rand() > DETECTION_THRESHOLD:
                false_positives += 1
            else:
                false_negatives += 1
    
    return false_positives, false_negatives

def calculate_energy_consumption(network, intruder_path, energy_detection=0.1, energy_communication=0.05):
    total_energy_consumption = 0
    for position in intruder_path:
        detecting_sensors = [sensor for sensor in network if np.linalg.norm(np.array(sensor) - np.array(position)) <= SENSOR_RADIUS]
        total_energy_consumption += len(detecting_sensors) * energy_detection
        
        for sensor in detecting_sensors:
            communicating_sensors = [s for s in network if np.linalg.norm(np.array(s) - np.array(sensor)) <= 2 * SENSOR_RADIUS]
            total_energy_consumption += len(communicating_sensors) * energy_communication
            
    return total_energy_consumption

def calculate_node_failure_rates(network, intruder_path, failure_probability=0.01):
    node_failures = 0
    for position in intruder_path:
        detecting_sensors = [sensor for sensor in network if np.linalg.norm(np.array(sensor) - np.array(position)) <= SENSOR_RADIUS]
        for sensor in detecting_sensors:
            if np.random.rand() < failure_probability:
                node_failures += 1
    
    failure_rate = node_failures / len(network)
    return failure_rate

def main():
    random.seed()  # Ensure randomness in each simulation run

    num_sensors = 559  # Example value
    sensor_radius = SENSOR_RADIUS
    num_iterations = 3

    # Generate networks
    aperiodic_network = generate_aperiodic_network(sensor_radius, num_sensors, num_iterations)
    hexagonal_network = generate_hexagonal_network(num_sensors, sensor_radius)
    triangular_network = generate_triangular_network(num_sensors, sensor_radius)
    square_network = generate_square_network(num_sensors, sensor_radius)

    # Random initial position for intruder
    intruder_initial_position = (
        random.uniform(-200, 200), random.uniform(-200, 200)
    )

    aperiodic_center = np.mean(aperiodic_network, axis=0)
    hexagonal_center = np.mean(hexagonal_network, axis=0)
    triangular_center = np.mean(triangular_network, axis=0)
    square_center = np.mean(square_network, axis=0)

    aperiodic_base_station = tuple(aperiodic_center)
    hexagonal_base_station = tuple(hexagonal_center)
    triangular_base_station = tuple(triangular_center)
    square_base_station = tuple(square_center)

    # Simulate intruder attack and calculate metrics
    aperiodic_path, _ = simulate_intruder_attack(aperiodic_network, intruder_initial_position, aperiodic_base_station, 'aperiodic')
    hexagonal_path, _ = simulate_intruder_attack(hexagonal_network, intruder_initial_position, hexagonal_base_station, 'hexagonal')
    triangular_path, _ = simulate_intruder_attack(triangular_network, intruder_initial_position, triangular_base_station, 'triangular')
    square_path, _ = simulate_intruder_attack(square_network, intruder_initial_position, square_base_station, 'square')

    # Calculate metrics for each network topology
    metrics = {}

    metrics['Aperiodic'] = {
        'Detection Rate': calculate_detection_rate(aperiodic_network, aperiodic_path),
        'False Positives/Negatives': calculate_false_positives_negatives(aperiodic_network, aperiodic_path),
        'Energy Consumption': calculate_energy_consumption(aperiodic_network, aperiodic_path),
        'Node Failure Rate': calculate_node_failure_rates(aperiodic_network, aperiodic_path)
    }

    metrics['Hexagonal'] = {
        'Detection Rate': calculate_detection_rate(hexagonal_network, hexagonal_path),
        'False Positives/Negatives': calculate_false_positives_negatives(hexagonal_network, hexagonal_path),
        'Energy Consumption': calculate_energy_consumption(hexagonal_network, hexagonal_path),
        'Node Failure Rate': calculate_node_failure_rates(hexagonal_network, hexagonal_path)
    }

    metrics['Triangular'] = {
        'Detection Rate': calculate_detection_rate(triangular_network, triangular_path),
        'False Positives/Negatives': calculate_false_positives_negatives(triangular_network, triangular_path),
        'Energy Consumption': calculate_energy_consumption(triangular_network, triangular_path),
        'Node Failure Rate': calculate_node_failure_rates(triangular_network, triangular_path)
    }

    metrics['Square'] = {
        'Detection Rate': calculate_detection_rate(square_network, square_path),
        'False Positives/Negatives': calculate_false_positives_negatives(square_network, square_path),
        'Energy Consumption': calculate_energy_consumption(square_network, square_path),
        'Node Failure Rate': calculate_node_failure_rates(square_network, square_path)
    }

    # Print metrics
    for network_type, metric in metrics.items():
        print(f"\n{network_type} Network Metrics:")
        for key, value in metric.items():
            print(f"{key}: {value}")

if __name__ == "__main__":
    main()
