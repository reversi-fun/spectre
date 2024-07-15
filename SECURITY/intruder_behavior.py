# intruder_behavior.py

import numpy as np
import random
from network_generation import generate_aperiodic_network, generate_hexagonal_network, generate_triangular_network, generate_square_network
from intruder_attack_simulation import has_reached_base_station, smart_random_walk, calculate_time_step, get_unique_angles_distances
import matplotlib.pyplot as plt

# Parameters
SENSOR_RADIUS = 10
HOP_DISTANCE = SENSOR_RADIUS

def simulate_smart_intruder(network, intruder_position, base_station_position, network_type):
    path = [intruder_position]
    time_steps = 0
    visited_nodes = set()
    is_aperiodic = network_type == 'aperiodic'

    while not has_reached_base_station(intruder_position, base_station_position):
        visited_nodes.add(tuple(intruder_position))
        intruder_position, step_time, _ = smart_random_walk(network, intruder_position, visited_nodes, is_aperiodic)
        path.append(intruder_position)
        time_steps += step_time

        if time_steps > len(network) * 10:  # Prevent infinite loop
            break

    return path, time_steps

def simulate_greedy_intruder(network, intruder_position, base_station_position):
    path = [intruder_position]
    time_steps = 0

    while not has_reached_base_station(intruder_position, base_station_position):
        distances = np.linalg.norm(np.array(network) - np.array(base_station_position), axis=1)
        nearest_node_index = np.argmin(distances)
        intruder_position = network[nearest_node_index]
        path.append(intruder_position)
        time_steps += 1

        if time_steps > len(network) * 10:  # Prevent infinite loop
            break

    return path, time_steps

def simulate_collaborative_intruders(network, intruder_positions, base_station_position):
    paths = [ [position] for position in intruder_positions ]
    time_steps = 0
    visited_nodes = set(tuple(pos) for pos in intruder_positions)

    while not any(has_reached_base_station(pos, base_station_position) for pos in intruder_positions):
        for i, intruder_position in enumerate(intruder_positions):
            intruder_position, _, _ = smart_random_walk(network, intruder_position, visited_nodes, is_aperiodic=False)
            paths[i].append(intruder_position)
            visited_nodes.add(tuple(intruder_position))

        time_steps += 1

        if time_steps > len(network) * 10:  # Prevent infinite loop
            break

    return paths, time_steps

def run_intruder_behavior_experiment(num_iterations=10):
    random.seed()

    num_sensors = 559  # Example value
    sensor_radius = SENSOR_RADIUS

    # Generate networks
    aperiodic_network = generate_aperiodic_network(sensor_radius, num_sensors, 3)
    hexagonal_network = generate_hexagonal_network(num_sensors, sensor_radius)
    triangular_network = generate_triangular_network(num_sensors, sensor_radius)
    square_network = generate_square_network(num_sensors, sensor_radius)

    # Base station positions (center of the network)
    aperiodic_base_station = tuple(np.mean(aperiodic_network, axis=0))
    hexagonal_base_station = tuple(np.mean(hexagonal_network, axis=0))
    triangular_base_station = tuple(np.mean(triangular_network, axis=0))
    square_base_station = tuple(np.mean(square_network, axis=0))

    intruder_initial_position = (random.uniform(-200, 200), random.uniform(-200, 200))
    intruder_positions = [intruder_initial_position for _ in range(3)]  # Three collaborative intruders

    network_types = ['Aperiodic', 'Hexagonal', 'Triangular', 'Square']
    networks = [aperiodic_network, hexagonal_network, triangular_network, square_network]
    base_stations = [aperiodic_base_station, hexagonal_base_station, triangular_base_station, square_base_station]

    results = {strategy: {network_type: [] for network_type in network_types} for strategy in ['Smart', 'Greedy', 'Collaborative']}

    for i in range(num_iterations):
        print(f"Starting iteration {i + 1}")

        for network, base_station, network_type in zip(networks, base_stations, network_types):
            print(f"Simulating for {network_type} network")

            # Smart intruder
            path, time_steps = simulate_smart_intruder(network, intruder_initial_position, base_station, network_type)
            results['Smart'][network_type].append(time_steps)

            # Greedy intruder
            path, time_steps = simulate_greedy_intruder(network, intruder_initial_position, base_station)
            results['Greedy'][network_type].append(time_steps)

            # Collaborative intruders
            paths, time_steps = simulate_collaborative_intruders(network, intruder_positions, base_station)
            results['Collaborative'][network_type].append(time_steps)

    # Calculate average time steps
    avg_results = {strategy: {network_type: np.mean(results[strategy][network_type]) for network_type in network_types} for strategy in results}

    plot_intruder_behavior_results(avg_results)

def plot_intruder_behavior_results(results):
    strategies = list(results.keys())
    network_types = list(results['Smart'].keys())

    fig, ax = plt.subplots(figsize=(10, 7))

    for strategy in strategies:
        avg_time_steps = [results[strategy][network_type] for network_type in network_types]
        ax.plot(network_types, avg_time_steps, label=strategy, marker='o')

    ax.set_xlabel('Network Topology')
    ax.set_ylabel('Average Time Steps')
    ax.set_title('Average Time Steps for Different Intruder Strategies')
    ax.legend()
    plt.show()

if __name__ == "__main__":
    run_intruder_behavior_experiment(num_iterations=100)
