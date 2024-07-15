# energy_analysis.py

import numpy as np
import random
import matplotlib.pyplot as plt
from network_generation import generate_aperiodic_network, generate_hexagonal_network, generate_triangular_network, generate_square_network
from intruder_attack_simulation import simulate_intruder_attack

# Parameters
SENSOR_RADIUS = 10
ENERGY_DETECTION = 0.1  # Energy cost for detection
ENERGY_COMMUNICATION = 0.05  # Energy cost for communication

def calculate_network_energy_usage(network, intruder_path):
    total_energy_consumption = 0
    for position in intruder_path:
        detecting_sensors = [sensor for sensor in network if np.linalg.norm(np.array(sensor) - np.array(position)) <= SENSOR_RADIUS]
        total_energy_consumption += len(detecting_sensors) * ENERGY_DETECTION
        
        for sensor in detecting_sensors:
            communicating_sensors = [s for s in network if np.linalg.norm(np.array(s) - np.array(sensor)) <= 2 * SENSOR_RADIUS]
            total_energy_consumption += len(communicating_sensors) * ENERGY_COMMUNICATION
            
    return total_energy_consumption

def simulate_network_energy_tradeoffs(network, intruder_position, base_station_position, network_type):
    path, _ = simulate_intruder_attack(network, intruder_position, base_station_position, network_type)
    energy_usage = calculate_network_energy_usage(network, path)
    return energy_usage

def plot_energy_efficiency(results):
    fig, ax = plt.subplots()
    network_types = list(results.keys())
    energy_usages = list(results.values())
    
    ax.bar(network_types, energy_usages, color=['red', 'green', 'blue', 'purple'])
    
    ax.set_xlabel('Network Topology')
    ax.set_ylabel('Total Energy Usage')
    ax.set_title('Energy Efficiency for Different Network Topologies')
    
    plt.show()

def main():
    random.seed()  # Ensure randomness in each simulation run

    num_sensors = 559  # Example value
    sensor_radius = SENSOR_RADIUS
    num_iterations = 4

    # Generate networks
    aperiodic_network = generate_aperiodic_network(sensor_radius, num_sensors, num_iterations)
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
    
    results = {network_type: 0 for network_type in network_types}

    for i in range(num_iterations):
        for network_type, network, base_station in zip(network_types, networks, base_stations):
            intruder_initial_position = (random.uniform(-200, 200), random.uniform(-200, 200))
            energy_usage = simulate_network_energy_tradeoffs(network, intruder_initial_position, base_station, network_type)
            results[network_type] += energy_usage
        print(f"Iteration {i + 1} completed.")

    # Average energy usage
    avg_energy_usages = {network_type: results[network_type] / num_iterations for network_type in network_types}

    # Plot results
    plot_energy_efficiency(avg_energy_usages)

if __name__ == "__main__":
    main()
