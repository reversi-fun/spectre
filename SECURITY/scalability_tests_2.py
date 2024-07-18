# scalability_tests.py

import numpy as np
import matplotlib.pyplot as plt
import scienceplots
import random
from claude_clone_simulation import (
    generate_networks,
    simulate_clone_attack,
    plot_network_with_paths,
    has_reached_base_station,
)
from scipy.ndimage import uniform_filter1d

plt.style.use(['science', 'ieee'])
plt.rcParams.update({'figure.dpi': '100'})

# Parameters
SENSOR_RADIUS = 10
NETWORK_SIZES = [9, 71, 559]  # Different sizes for scalability tests
NUM_ITERATIONS = 1  # Number of iterations for averaging results
DETECTION_THRESHOLD = 0.1  # Threshold for considering a detection as positive

def run_scalability_tests():
    results = {size: {network_type: [] for network_type in ['Aperiodic', 'Hexagonal', 'Triangular', 'Square']} for size in NETWORK_SIZES}

    for size in NETWORK_SIZES:
        for i in range(NUM_ITERATIONS):
            print(f"Running iteration {i+1}/{NUM_ITERATIONS} for network size {size}...")

            # Generate networks
            networks = generate_networks(SENSOR_RADIUS, size)
            base_station_positions = {network_type: tuple(np.mean(network, axis=0)) for network_type, network in networks.items()}

            # Random initial position for intruder
            intruder_initial_position = (
                random.uniform(-200, 200), random.uniform(-200, 200)
            )

            # Simulate intruder attacks
            for network_type, network in networks.items():
                base_station = base_station_positions[network_type]
                path, intrusion_effort_metric = simulate_clone_attack(network, [intruder_initial_position], base_station)
                detection_rate = calculate_detection_rate(network, path)
                false_positives, false_negatives = calculate_false_positives_negatives(network, path)
                energy_consumption = calculate_energy_consumption(network, path)
                node_failure_rate = calculate_node_failure_rates(network, path)

                results[size][network_type].append({
                    'Intrusion Effort Metric': intrusion_effort_metric,
                    'Detection Rate': detection_rate,
                    'False Positives': false_positives,
                    'False Negatives': false_negatives,
                    'Energy Consumption': energy_consumption,
                    'Node Failure Rate': node_failure_rate
                })

    # Aggregate results
    aggregated_results = aggregate_results(results)

    # Plot results
    plot_scalability_results(aggregated_results)

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

def aggregate_results(results):
    aggregated = {}
    for size in results:
        aggregated[size] = {}
        for network_type in results[size]:
            avg_intrusion_effort_metric = np.mean([r['Intrusion Effort Metric'] for r in results[size][network_type]])
            avg_detection_rate = np.mean([r['Detection Rate'] for r in results[size][network_type]])
            avg_false_positives = np.mean([r['False Positives'] for r in results[size][network_type]])
            avg_false_negatives = np.mean([r['False Negatives'] for r in results[size][network_type]])
            avg_energy_consumption = np.mean([r['Energy Consumption'] for r in results[size][network_type]])
            avg_node_failure_rate = np.mean([r['Node Failure Rate'] for r in results[size][network_type]])

            aggregated[size][network_type] = {
                'Intrusion Effort Metric': avg_intrusion_effort_metric,
                'Detection Rate': avg_detection_rate,
                'False Positives': avg_false_positives,
                'False Negatives': avg_false_negatives,
                'Energy Consumption': avg_energy_consumption,
                'Node Failure Rate': avg_node_failure_rate
            }

    return aggregated

def plot_scalability_results(aggregated_results):
    sizes = list(aggregated_results.keys())
    metrics = list(aggregated_results[sizes[0]]['Aperiodic'].keys())

    fig, axes = plt.subplots(len(metrics), 1, figsize=(10, 15))

    for i, metric in enumerate(metrics):
        for network_type in ['Aperiodic', 'Hexagonal', 'Triangular', 'Square']:
            values = [aggregated_results[size][network_type][metric] for size in sizes]
            axes[i].plot(sizes, values, label=network_type)
        
        axes[i].set_xlabel('Network Size')
        axes[i].set_ylabel(metric)
        axes[i].set_title(f'{metric} vs Network Size')
        axes[i].legend()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_scalability_tests()
