# energy_consumption_simulation.py

import numpy as np
import matplotlib.pyplot as plt
from network_generation import generate_aperiodic_network, generate_hexagonal_network, generate_triangular_network, generate_square_network
from intruder_attack_simulation import simulate_intruder_attack
import random

# Parameters
SENSOR_RADIUS = 10
HOP_DISTANCE = SENSOR_RADIUS

def calculate_energy_consumption(path, energy_per_hop):
    return len(path) * energy_per_hop

def run_energy_simulation(num_iterations=100, energy_per_hop=1.0):
    random.seed()  # Ensure randomness in each simulation run

    global SENSOR_RADIUS
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

    network_types = ['Aperiodic', 'Hexagonal', 'Triangular', 'Square']
    networks = [aperiodic_network, hexagonal_network, triangular_network, square_network]
    base_stations = [aperiodic_base_station, hexagonal_base_station, triangular_base_station, square_base_station]
    
    results = {network_type: [] for network_type in network_types}
    
    for i in range(num_iterations):
        for network_type, network, base_station in zip(network_types, networks, base_stations):
            intruder_initial_position = (random.uniform(-200, 200), random.uniform(-200, 200))
            path, _ = simulate_intruder_attack(network, intruder_initial_position, base_station)
            energy_consumption = calculate_energy_consumption(path, energy_per_hop)
            results[network_type].append(energy_consumption)
        print(f"Iteration {i + 1} completed.")

    # Calculate average energy consumption
    avg_energy_consumption = {network_type: np.mean(results[network_type]) for network_type in network_types}

    # Plot results
    plot_results(avg_energy_consumption)

def plot_results(avg_energy_consumption):
    fig, ax = plt.subplots()
    network_types = list(avg_energy_consumption.keys())
    avg_energy = list(avg_energy_consumption.values())
    
    ax.bar(network_types, avg_energy, color=['red', 'green', 'blue', 'purple'])
    
    ax.set_xlabel('Network Topology')
    ax.set_ylabel('Average Energy Consumption')
    ax.set_title('Average Energy Consumption for Different Network Topologies')
    
    plt.show()

if __name__ == "__main__":
    run_energy_simulation()
