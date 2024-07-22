import numpy as np
import matplotlib.pyplot as plt
import scienceplots
import random
import pandas as pd
from network_generation import generate_aperiodic_network, generate_hexagonal_network, generate_triangular_network, generate_square_network

plt.style.use(['science', 'ieee', 'high-vis'])
plt.rcParams.update({'figure.dpi': 600})

# Parameters
SENSOR_RADIUS = 10
COMMUNICATION_RANGE = SENSOR_RADIUS * 2
CLONE_PERCENTAGE = 0.05
DETECTION_THRESHOLD = 0.1  # Probability threshold for detecting a cloned node

def generate_networks(sensor_radius, num_sensors):
    aperiodic_network = generate_aperiodic_network(sensor_radius, num_sensors, 3)
    hexagonal_network = generate_hexagonal_network(num_sensors, sensor_radius)
    triangular_network = generate_triangular_network(num_sensors, sensor_radius)
    square_network = generate_square_network(num_sensors, sensor_radius)
    return {
        'Aperiodic': aperiodic_network,
        'Hexagonal': hexagonal_network,
        'Triangular': triangular_network,
        'Square': square_network
    }

def get_cloned_positions(network, seed, clone_percentage):
    random.seed(seed)
    num_clones = int(len(network) * clone_percentage)
    clone_indices = np.random.choice(len(network), num_clones, replace=False)
    return [tuple(network[idx]) for idx in clone_indices]

def simulate_clone_attack(network, clone_positions, base_station_position):
    detections = 0
    paths = []
    total_intrusion_effort = 0
    total_hops = 0
    detected_clones = set()
    compromised_nodes = set(clone_positions)
    active_clones = set(clone_positions)

    while active_clones:
        new_active_clones = set()
        for clone_position in active_clones:
            if tuple(clone_position) in detected_clones or has_reached_base_station(clone_position, base_station_position):
                continue
            
            path = [clone_position]
            visited_nodes = set()
            while not has_reached_base_station(clone_position, base_station_position):
                visited_nodes.add(tuple(clone_position))
                next_position, effort_of_intrusion, pattern_found = smart_random_walk(network, clone_position, visited_nodes)
                if next_position is None:
                    break
                if np.linalg.norm(np.array(next_position) - np.array(clone_position)) > COMMUNICATION_RANGE:
                    break
                clone_position = next_position
                compromised_nodes.add(tuple(clone_position))
                path.append(clone_position)
                total_intrusion_effort += effort_of_intrusion
                total_hops += 1
                if random.random() < DETECTION_THRESHOLD:
                    detected_clones.add(tuple(clone_position))
                    detections += 1
                    break
                if has_reached_base_station(clone_position, base_station_position):
                    break
            paths.append(path)
            if not has_reached_base_station(clone_position, base_station_position) and tuple(clone_position) not in detected_clones:
                new_active_clones.add(tuple(clone_position))
        
        active_clones = new_active_clones
    
    return detections, paths, total_intrusion_effort, total_hops, detected_clones, len(compromised_nodes)

def smart_random_walk(network, intruder_position, visited_nodes):
    distances = np.linalg.norm(np.array(network) - np.array(intruder_position), axis=1)
    sorted_indices = np.argsort(distances)
    for idx in sorted_indices:
        nearest_node = network[idx]
        if tuple(nearest_node) not in visited_nodes and np.linalg.norm(nearest_node - intruder_position) <= COMMUNICATION_RANGE:
            effort_of_intrusion = calculate_intrusion_effort(nearest_node, intruder_position, network)
            pattern_found = detect_pattern(nearest_node, network)
            return nearest_node, effort_of_intrusion, pattern_found
    return None, 0, False

def calculate_intrusion_effort(nearest_node, current_node, network):
    distance = np.linalg.norm(np.array(nearest_node) - np.array(current_node))
    unique_angles, unique_distances = get_unique_angles_distances(current_node, network)
    complexity_factor = len(unique_angles) + len(unique_distances)
    return distance / SENSOR_RADIUS * complexity_factor

def get_unique_angles_distances(current_node, network):
    current_node = np.array(current_node)
    unique_angles = set()
    unique_distances = set()
    
    for node in network:
        node = np.array(node)
        vector = node - current_node
        distance = np.linalg.norm(vector)
        unique_distances.add(distance)
        
        angle = np.degrees(np.arctan2(vector[1], vector[0]))
        if angle < 0:
            angle += 360
        unique_angles.add(angle)
    
    return unique_angles, unique_distances

def detect_pattern(current_node, network):
    unique_angles, unique_distances = get_unique_angles_distances(current_node, network)
    
    max_angles = 6
    max_distances = 2
    
    return len(unique_angles) <= max_angles and len(unique_distances) <= max_distances

def has_reached_base_station(position, base_station_position):
    return np.linalg.norm(np.array(position) - np.array(base_station_position)) <= SENSOR_RADIUS

def run_simulation(num_sensors=71, num_iterations=1, num_rounds=20, save_fig=True):
    sensor_radius = SENSOR_RADIUS
    networks = generate_networks(sensor_radius, num_sensors)
    results = {network_type: {'detections': [], 'total_intrusion_effort': [], 'total_hops': [], 'base_station_reached': [], 'compromised_nodes': []} for network_type in networks.keys()}
    
    for round_idx in range(num_rounds):
        print(f"Round {round_idx + 1}")
        round_seed = round_idx  # Use round index as the seed for consistency
        clone_positions_per_network = {network_type: get_cloned_positions(network, round_seed, CLONE_PERCENTAGE) for network_type, network in networks.items()}
        
        for network_type, network in networks.items():
            clone_positions = clone_positions_per_network[network_type]
            detections, paths, total_intrusion_effort, total_hops, detected_clones, compromised_nodes = simulate_clone_attack(network, clone_positions, tuple(np.mean(network, axis=0)))
            results[network_type]['detections'].append(detections)
            results[network_type]['total_intrusion_effort'].append(total_intrusion_effort)
            results[network_type]['total_hops'].append(total_hops)
            results[network_type]['compromised_nodes'].append(compromised_nodes)
            results[network_type]['base_station_reached'].append(1 if has_reached_base_station(paths[-1][-1], tuple(np.mean(network, axis=0))) else 0)
    
    plot_metrics(results, num_rounds, num_sensors, save_fig)

def plot_metrics(results, num_rounds, num_sensors, save_fig=False):
    metrics = ['Total Intrusion Effort', 'Total Hops', 'Base Station Reached %', 'Compromised Nodes', 'Detections']
    colors = ['tab:red', 'tab:blue', 'tab:green', 'tab:orange', 'tab:purple']
    network_types = list(results.keys())
    
    # Plot each metric as a line plot with box plots for rounds
    for metric, color in zip(metrics, colors):
        plt.figure(figsize=(10, 6))
        
        for idx, network_type in enumerate(network_types):
            metric_data = results[network_type][metric.lower().replace(" ", "_")]
            plt.plot(range(1, num_rounds + 1), metric_data, label=network_type, marker='o', linestyle='-', color=colors[idx])
        
        plt.title(f'{metric} vs. Number of Rounds', fontsize=16, fontweight='bold')
        plt.xlabel('Number of Rounds', fontsize=14)
        plt.ylabel(metric, fontsize=14)
        plt.legend(title='Network Type', fontsize=12)
        plt.grid(True)
        
        if save_fig:
            plt.savefig(f'figures/{metric.replace(" ", "_")}_vs_Number_of_Rounds.png', dpi=600)
        plt.show()
        
        # Box plot for the rounds
        plt.figure(figsize=(10, 6))
        boxplot_data = [results[network_type][metric.lower().replace(" ", "_")] for network_type in network_types]
        positions = np.arange(1, num_rounds + 1)
        
        bplot = plt.boxplot(boxplot_data, positions=positions, widths=0.6, patch_artist=True)
        
        for patch, color in zip(bplot['boxes'], colors):
            patch.set_facecolor(color)
        
        plt.title(f'{metric} Distribution Across Rounds', fontsize=16, fontweight='bold')
        plt.xlabel('Number of Rounds', fontsize=14)
        plt.ylabel(metric, fontsize=14)
        plt.grid(True)
        
        if save_fig:
            plt.savefig(f'figures/{metric.replace(" ", "_")}_Distribution_Across_Rounds.png', dpi=600)
        plt.show()
        
if __name__ == "__main__":
    run_simulation(num_iterations=1, num_rounds=20, save_fig=True)
