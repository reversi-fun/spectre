# scalability_tests.py

import numpy as np
import matplotlib.pyplot as plt
import random
from network_generation import generate_aperiodic_network, generate_hexagonal_network, generate_triangular_network, generate_square_network
from intruder_attack_simulation import simulate_intruder_attack
from metrics_calculation import calculate_detection_rate, calculate_false_positives_negatives, calculate_energy_consumption, calculate_node_failure_rates

# Parameters
SENSOR_RADIUS = 10
NETWORK_SIZES = [9, 71, 559]  # Different sizes for scalability tests
NUM_ITERATIONS = 10  # Number of iterations for averaging results

def run_scalability_tests():
    results = {size: {network_type: [] for network_type in ['Aperiodic', 'Hexagonal', 'Triangular', 'Square']} for size in NETWORK_SIZES}

    for size in NETWORK_SIZES:
        for i in range(NUM_ITERATIONS):
            print(f"Running iteration {i+1}/{NUM_ITERATIONS} for network size {size}...")

            # Generate networks
            aperiodic_network = generate_aperiodic_network(SENSOR_RADIUS, size, 3)
            hexagonal_network = generate_hexagonal_network(size, SENSOR_RADIUS)
            triangular_network = generate_triangular_network(size, SENSOR_RADIUS)
            square_network = generate_square_network(size, SENSOR_RADIUS)

            # Base station positions (center of the network)
            aperiodic_base_station = tuple(np.mean(aperiodic_network, axis=0))
            hexagonal_base_station = tuple(np.mean(hexagonal_network, axis=0))
            triangular_base_station = tuple(np.mean(triangular_network, axis=0))
            square_base_station = tuple(np.mean(square_network, axis=0))

            # Random initial position for intruder
            intruder_initial_position = (
                random.uniform(-200, 200), random.uniform(-200, 200)
            )

            # Simulate intruder attacks
            for network, base_station, network_type in zip(
                [aperiodic_network, hexagonal_network, triangular_network, square_network],
                [aperiodic_base_station, hexagonal_base_station, triangular_base_station, square_base_station],
                ['Aperiodic', 'Hexagonal', 'Triangular', 'Square']
            ):
                path, time_steps = simulate_intruder_attack(network, intruder_initial_position, base_station, network_type)
                detection_rate = calculate_detection_rate(network, path)
                false_positives, false_negatives = calculate_false_positives_negatives(network, path)
                energy_consumption = calculate_energy_consumption(network, path)
                node_failure_rate = calculate_node_failure_rates(network, path)

                results[size][network_type].append({
                    'Time Steps': time_steps,
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

def aggregate_results(results):
    aggregated = {}
    for size in results:
        aggregated[size] = {}
        for network_type in results[size]:
            avg_time_steps = np.mean([r['Time Steps'] for r in results[size][network_type]])
            avg_detection_rate = np.mean([r['Detection Rate'] for r in results[size][network_type]])
            avg_false_positives = np.mean([r['False Positives'] for r in results[size][network_type]])
            avg_false_negatives = np.mean([r['False Negatives'] for r in results[size][network_type]])
            avg_energy_consumption = np.mean([r['Energy Consumption'] for r in results[size][network_type]])
            avg_node_failure_rate = np.mean([r['Node Failure Rate'] for r in results[size][network_type]])

            aggregated[size][network_type] = {
                'Time Steps': avg_time_steps,
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
