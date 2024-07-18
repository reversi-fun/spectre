import numpy as np
import matplotlib.pyplot as plt
import scienceplots
import random
import pandas as pd
from network_generation import generate_aperiodic_network, generate_hexagonal_network, generate_triangular_network, generate_square_network
from scipy.ndimage import uniform_filter1d

plt.style.use(['science', 'ieee'])
plt.rcParams.update({'figure.dpi': '150'})

# Parameters
SENSOR_RADIUS = 10
COMMUNICATION_RANGE = SENSOR_RADIUS * 2
CLONE_PERCENTAGE = 0.01
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

def get_cloned_positions(base_station, num_clones, distance, angle):
    angle_rad = np.deg2rad(angle)
    x_offset = distance * np.cos(angle_rad)
    y_offset = distance * np.sin(angle_rad)
    clone_positions = []
    center_x = base_station[0] + x_offset
    center_y = base_station[1] + y_offset

    for _ in range(num_clones):
        x_variation = random.uniform(-SENSOR_RADIUS, SENSOR_RADIUS)
        y_variation = random.uniform(-SENSOR_RADIUS, SENSOR_RADIUS)
        clone_positions.append((center_x + x_variation, center_y + y_variation))

    return clone_positions

def simulate_clone_attack(network, clone_positions, base_station_position):
    detections = 0
    paths = []
    time_steps = 0
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
                next_position, step_time, pattern_found = smart_random_walk(network, clone_position, visited_nodes)
                if next_position is None:
                    break
                if np.linalg.norm(np.array(next_position) - np.array(clone_position)) > COMMUNICATION_RANGE:
                    break
                clone_position = next_position
                compromised_nodes.add(tuple(clone_position))
                path.append(clone_position)
                time_steps += step_time
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
    
    return detections, paths, time_steps, total_hops, detected_clones, len(compromised_nodes)

def smart_random_walk(network, intruder_position, visited_nodes):
    distances = np.linalg.norm(np.array(network) - np.array(intruder_position), axis=1)
    sorted_indices = np.argsort(distances)
    for idx in sorted_indices:
        nearest_node = network[idx]
        if tuple(nearest_node) not in visited_nodes and np.linalg.norm(nearest_node - intruder_position) <= COMMUNICATION_RANGE:
            step_time = calculate_time_step(nearest_node, intruder_position, network)
            pattern_found = detect_pattern(nearest_node, network)
            return nearest_node, step_time, pattern_found
    return None, 0, False

def calculate_time_step(nearest_node, current_node, network):
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

def plot_network_with_paths(network, paths, clone_positions, detected_clones, base_station_position, title):
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
    plt.show()
    plt.close()  # Close the figure to free up memory

def run_simulation(num_sensors=559, num_iterations=1, num_rounds=10):
    sensor_radius = SENSOR_RADIUS
    networks = generate_networks(sensor_radius, num_sensors)
    results = {network_type: {'detections': 0, 'paths': [], 'time_steps': [], 'total_hops': [], 'base_station_reached': 0, 'detected_clones': set(), 'compromised_nodes': 0} for network_type in networks.keys()}
    
    for round_idx in range(num_rounds):
        print(f"Round {round_idx + 1}")
        round_seed = round_idx  # Use round index as the seed for consistency
        random.seed(round_seed)  # Set the random seed for reproducibility
        base_station_position = tuple(np.mean(networks['Aperiodic'], axis=0))
        distance = random.uniform(10, 50)  # Example distance range
        angle = random.uniform(0, 360)  # Random angle for each round
        
        clone_positions_per_network = {network_type: get_cloned_positions(base_station_position, int(num_sensors * CLONE_PERCENTAGE), distance, angle) for network_type, network in networks.items()}
        
        for network_type, network in networks.items():
            print(f"Processing {network_type} network...")  # Add this line for debugging
            clone_positions = clone_positions_per_network[network_type]
            for iteration in range(num_iterations):
                detections, paths, time_steps, total_hops, detected_clones, compromised_nodes = simulate_clone_attack(network, clone_positions, base_station_position)
                results[network_type]['detections'] += detections
                results[network_type]['paths'].extend(paths)
                results[network_type]['time_steps'].append(time_steps)
                results[network_type]['total_hops'].append(total_hops)
                results[network_type]['detected_clones'].update(detected_clones)
                results[network_type]['compromised_nodes'] += compromised_nodes
                if paths and has_reached_base_station(paths[-1][-1], base_station_position):
                    results[network_type]['base_station_reached'] += 1
            
            plot_network_with_paths(network, results[network_type]['paths'], clone_positions, results[network_type]['detected_clones'], base_station_position, f'{network_type} Network')
            plt.close()  # Close the figure to free up memory
    
    for network_type in results.keys():
        print(f"{network_type} Network: {results[network_type]['detections']} detections, {results[network_type]['base_station_reached']} base stations reached out of {num_iterations * num_rounds} total rounds")
        print(f"Average time steps: {np.mean(results[network_type]['time_steps'])}")
        print(f"Average total hops: {np.mean(results[network_type]['total_hops'])}")
        print(f"Total detected cloned nodes: {len(results[network_type]['detected_clones'])}")
        print(f"Total compromised nodes: {results[network_type]['compromised_nodes'] / (num_iterations * num_rounds)}")
        print(f"Base station reached percentage: {(results[network_type]['base_station_reached'] / (num_iterations * num_rounds)) * 100}%")
    
    plot_metrics(results, num_rounds)

def plot_metrics(results, num_rounds):
    metrics = ['Time Steps', 'Total Hops']
    data = []
    
    for network_type, network_results in results.items():
        time_steps = uniform_filter1d(network_results['time_steps'], size=50)
        total_hops = uniform_filter1d(network_results['total_hops'], size=50)
        data.extend([
            {'Round': i, 'Network Type': network_type, 'Metric': 'Time Steps', 'Value': time_steps[i]} for i in range(num_rounds)
        ])
        data.extend([
            {'Round': i, 'Network Type': network_type, 'Metric': 'Total Hops', 'Value': total_hops[i]} for i in range(num_rounds)
        ])
    
    df = pd.DataFrame(data)
    
    markers = ['o', '^', 's', 'd']
    for metric in metrics:
        plt.figure(figsize=(12, 6))
        subset = df[df['Metric'] == metric]
        for idx, network_type in enumerate(results.keys()):
            network_subset = subset[subset['Network Type'] == network_type]
            plt.plot(network_subset['Round'], network_subset['Value'], marker=markers[idx], label=network_type)
        plt.title(f'{metric} for Each Topology Over {num_rounds} Rounds', fontsize=16, fontweight='bold')
        plt.xlabel('Rounds', fontsize=14)
        plt.ylabel(metric, fontsize=14)
        plt.legend(title='Network Type', title_fontsize='12', fontsize='10', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    run_simulation(num_iterations=1, num_rounds=10)
