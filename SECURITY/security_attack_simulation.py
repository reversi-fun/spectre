# File: security_attack_simulation.py

import numpy as np
import random
from network_generation import generate_aperiodic_network, generate_hexagonal_network, generate_triangular_network, generate_square_network
from intruder_attack_simulation import has_reached_base_station, calculate_time_step, get_unique_angles_distances
import matplotlib.pyplot as plt

# Parameters
SENSOR_RADIUS = 10
HOP_DISTANCE = SENSOR_RADIUS

def simulate_blackhole_attack(network, intruder_position, base_station_position):
    path = [intruder_position]
    time_steps = 0

    while not has_reached_base_station(intruder_position, base_station_position):
        time_steps += 1
        if np.random.rand() < 0.5:  # 50% chance to drop the packet
            continue
        distances = np.linalg.norm(np.array(network) - np.array(intruder_position), axis=1)
        nearest_node_index = np.argmin(distances)
        intruder_position = network[nearest_node_index]
        path.append(intruder_position)
        
        if time_steps > len(network) * 10:  # Prevent infinite loop
            break

    return path, time_steps

def simulate_sybil_attack(network, intruder_position, base_station_position):
    path = [intruder_position]
    time_steps = 0
    identities = [intruder_position] + [network[random.randint(0, len(network) - 1)] for _ in range(2)]  # Three Sybil identities

    while not has_reached_base_station(intruder_position, base_station_position):
        time_steps += 1
        intruder_position = identities[random.randint(0, len(identities) - 1)]
        path.append(intruder_position)
        
        if time_steps > len(network) * 10:  # Prevent infinite loop
            break

    return path, time_steps

def simulate_selective_forwarding_attack(network, intruder_position, base_station_position):
    path = [intruder_position]
    time_steps = 0
    visited_nodes = set()

    while not has_reached_base_station(intruder_position, base_station_position):
        visited_nodes.add(tuple(intruder_position))
        distances = np.linalg.norm(np.array(network) - np.array(intruder_position), axis=1)
        nearest_node_index = np.argmin(distances)
        next_position = network[nearest_node_index]
        
        if tuple(next_position) not in visited_nodes:
            if np.random.rand() < 0.5:  # 50% chance to drop the packet
                continue
        
        intruder_position = next_position
        path.append(intruder_position)
        time_steps += 1

        if time_steps > len(network) * 10:  # Prevent infinite loop
            break

    return path, time_steps

def run_security_attack_simulations(num_iterations=10):
    random.seed()

    num_sensors = 559
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

    network_types = ['Aperiodic', 'Hexagonal', 'Triangular', 'Square']
    networks = [aperiodic_network, hexagonal_network, triangular_network, square_network]
    base_stations = [aperiodic_base_station, hexagonal_base_station, triangular_base_station, square_base_station]

    results = {attack: {network_type: [] for network_type in network_types} for attack in ['Blackhole', 'Sybil', 'Selective Forwarding']}

    for i in range(num_iterations):
        print(f"Starting iteration {i + 1}")

        for network, base_station, network_type in zip(networks, base_stations, network_types):
            print(f"Simulating for {network_type} network")

            # Blackhole attack
            path, time_steps = simulate_blackhole_attack(network, (random.uniform(-200, 200), random.uniform(-200, 200)), base_station)
            results['Blackhole'][network_type].append(time_steps)

            # Sybil attack
            path, time_steps = simulate_sybil_attack(network, (random.uniform(-200, 200), random.uniform(-200, 200)), base_station)
            results['Sybil'][network_type].append(time_steps)

            # Selective forwarding attack
            path, time_steps = simulate_selective_forwarding_attack(network, (random.uniform(-200, 200), random.uniform(-200, 200)), base_station)
            results['Selective Forwarding'][network_type].append(time_steps)

    # Calculate average time steps
    avg_results = {attack: {network_type: np.mean(results[attack][network_type]) for network_type in network_types} for attack in results}

    plot_attack_simulation_results(results, num_iterations)

def plot_attack_simulation_results(results, num_iterations):
    attacks = list(results.keys())
    network_types = list(results['Blackhole'].keys())

    fig, axs = plt.subplots(1, len(attacks), figsize=(20, 5), sharey=True)

    for ax, attack in zip(axs, attacks):
        for network_type in network_types:
            ax.plot(range(1, num_iterations + 1), results[attack][network_type], label=f'{network_type} Network')
        ax.set_xlabel('Rounds')
        ax.set_title(f'{attack} Attack')
        ax.legend()

    axs[0].set_ylabel('Time Steps')
    plt.suptitle('Time Steps for Different Security Attacks Over Multiple Rounds')
    plt.show()

if __name__ == "__main__":
    run_security_attack_simulations(num_iterations=10)
