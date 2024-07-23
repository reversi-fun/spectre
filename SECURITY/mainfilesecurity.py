import numpy as np
import matplotlib.pyplot as plt
import scienceplots
import random
import pandas as pd
from network_generation import generate_aperiodic_network, generate_hexagonal_network, generate_triangular_network, generate_square_network

plt.style.use(['science', 'ieee', 'high-vis'])
plt.rcParams.update({'figure.dpi': '300'})

# Parameters
SENSOR_RADIUS = 10
COMMUNICATION_RANGE = SENSOR_RADIUS * 2
CLONE_PERCENTAGE = 0.1
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

def plot_network_with_paths(network, paths, clone_positions, detected_clones, base_station_position, title, save_fig=False):
    fig, ax = plt.subplots(figsize=(10, 8))
    network = np.array(network)
    
    # Plot sensors and their ranges
    for node in network:
        sensor_circle = plt.Circle(node, SENSOR_RADIUS, color='blue', alpha=0.2)
        ax.add_artist(sensor_circle)
        plt.plot(node[0], node[1], 'bo', markersize=2, label='Uncompromised Nodes' if 'Uncompromised Nodes' not in plt.gca().get_legend_handles_labels()[1] else "")
    
    # Plot base station
    plt.plot(base_station_position[0], base_station_position[1], 'go', markersize=10, label='Base Station')
    
    # Plot cloned nodes
    for pos in clone_positions:
        plt.plot(pos[0], pos[1], 'ro', markersize=5, label='Cloned Nodes' if 'Cloned Nodes' not in plt.gca().get_legend_handles_labels()[1] else "")
    
    # Plot detected cloned nodes
    for pos in detected_clones:
        plt.plot(pos[0], pos[1], 'yo', markersize=5, label='Detected Cloned Nodes' if 'Detected Cloned Nodes' not in plt.gca().get_legend_handles_labels()[1] else "")
    
    # Plot paths
    for path in paths:
        path = np.array(path)
        plt.plot(path[:, 0], path[:, 1], 'r-', linewidth=1, alpha=0.5)

    plt.title(title, fontsize=16, fontweight='bold')
    plt.xlabel('Width', fontsize=14)
    plt.ylabel('Height', fontsize=14)
    plt.legend(fontsize=10, loc='center left', bbox_to_anchor=(1, 0.5))
    plt.tight_layout()

    if save_fig:
        plt.savefig(f'figures/{title}.png', dpi=300)

    plt.show()

def run_simulation(num_sensors=71, num_iterations=1, num_rounds=10000, save_fig=False):
    sensor_radius = SENSOR_RADIUS
    networks = generate_networks(sensor_radius, num_sensors)
    results = {network_type: {'detections': 0, 'paths': [], 'total_intrusion_effort': 0, 'total_hops': 0, 'base_station_reached': 0, 'detected_clones': set(), 'compromised_nodes': 0} for network_type in networks.keys()}
    
    for round_idx in range(num_rounds):
        print(f"Round {round_idx + 1}")
        round_seed = round_idx  # Use round index as the seed for consistency
        clone_positions_per_network = {network_type: get_cloned_positions(network, round_seed, CLONE_PERCENTAGE) for network_type, network in networks.items()}
        
        for network_type, network in networks.items():
            clone_positions = clone_positions_per_network[network_type]
            for iteration in range(num_iterations):
                detections, paths, total_intrusion_effort, total_hops, detected_clones, compromised_nodes = simulate_clone_attack(network, clone_positions, tuple(np.mean(network, axis=0)))
                results[network_type]['detections'] += detections
                results[network_type]['paths'].extend(paths)
                results[network_type]['total_intrusion_effort'] += total_intrusion_effort
                results[network_type]['total_hops'] += total_hops
                results[network_type]['detected_clones'].update(detected_clones)
                results[network_type]['compromised_nodes'] += compromised_nodes
                if has_reached_base_station(paths[-1][-1], tuple(np.mean(network, axis=0))):
                    results[network_type]['base_station_reached'] += 1
            if round_idx == 0 and iteration == 0:
                plot_network_with_paths(network, results[network_type]['paths'], clone_positions, results[network_type]['detected_clones'], tuple(np.mean(network, axis=0)), f'{network_type} Network - {num_sensors} Sensors', save_fig)
    
    for network_type in results.keys():
        print(f"{network_type} Network: {results[network_type]['detections']} detections, {results[network_type]['base_station_reached']} base stations reached out of {num_iterations * num_rounds} total rounds")
        print(f"Average total intrusion effort: {results[network_type]['total_intrusion_effort'] / (num_iterations * num_rounds)}")
        print(f"Average total hops: {results[network_type]['total_hops'] / (num_iterations * num_rounds)}")
        print(f"Average total detected cloned nodes: {len(results[network_type]['detected_clones'])} / {num_iterations * num_rounds}")
        print(f"Average total compromised nodes: {results[network_type]['compromised_nodes'] / (num_iterations * num_rounds)}")
        print(f"Base station reached percentage: {(results[network_type]['base_station_reached'] / (num_iterations * num_rounds)) * 100}%")
    
    plot_metrics(results, num_rounds, num_sensors, save_fig)

def plot_metrics(results, num_rounds, num_sensors, save_fig=False):
    metrics = ['Average Intrusion Effort', 'Average Hops', 'Base Station Reached Percentage', 'Average Compromised Nodes', 'Average Detections']
    data = []

    for network_type, network_results in results.items():
        data.append({'Network Type': network_type, 'Metric': 'Average Intrusion Effort', 'Value': network_results['total_intrusion_effort'] / num_rounds})
        data.append({'Network Type': network_type, 'Metric': 'Average Hops', 'Value': network_results['total_hops'] / num_rounds})
        data.append({'Network Type': network_type, 'Metric': 'Base Station Reached Percentage', 'Value': (network_results['base_station_reached'] / num_rounds) * 100})
        data.append({'Network Type': network_type, 'Metric': 'Average Compromised Nodes', 'Value': network_results['compromised_nodes'] / num_rounds})
        data.append({'Network Type': network_type, 'Metric': 'Average Detections', 'Value': network_results['detections'] / num_rounds})
    
    df = pd.DataFrame(data)

    colors = ['tab:red', 'tab:blue', 'tab:green', 'tab:orange', 'tab:purple']
    
    for metric, color in zip(metrics, colors):
        plt.figure(figsize=(10, 4))
        subset = df[df['Metric'] == metric]
        plt.plot(subset['Network Type'], subset['Value'], marker='o', linestyle='-', color=color, label=metric)
        plt.title(f'{metric} for Each Topology Over {num_rounds} Rounds: {int(CLONE_PERCENTAGE*100)}\% Clones, {num_sensors} Sensors', fontsize=16, fontweight='bold')
        plt.xlabel('Network Topology', fontsize=14)
        plt.ylabel(metric, fontsize=14)
        plt.tight_layout()
        if save_fig:
            plt.savefig(f'figures/{metric}_for_Each_Topology_Over_{num_rounds}_Rounds_Clone_Percentage_{int(CLONE_PERCENTAGE*100)}_Sensors_{num_sensors}.png', dpi=300)
        plt.show()

if __name__ == "__main__":
    run_simulation(num_iterations=1, num_rounds=10000, save_fig=True)
