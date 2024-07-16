# File: results_visualization.py

import matplotlib.pyplot as plt

def visualize_results(all_averaged_metrics, attack_type):
    rounds = list(range(1, len(all_averaged_metrics[0]['detection_rate']) + 1))

    # Plot Detection Rate
    plt.figure(figsize=(10, 6))
    for metrics in all_averaged_metrics:
        plt.plot(rounds, metrics['detection_rate'], label=metrics['label'])
    plt.xlabel('Rounds')
    plt.ylabel('Detection Rate')
    plt.title(f'Comparison of Detection Rate ({attack_type.capitalize()})')
    plt.legend()
    plt.grid(True)
    plt.savefig(f'detection_rate_comparison_{attack_type}.png')
    plt.show()

    # Plot Energy Consumption
    plt.figure(figsize=(10, 6))
    for metrics in all_averaged_metrics:
        plt.plot(rounds, metrics['energy_consumption'], label=metrics['label'])
    plt.xlabel('Rounds')
    plt.ylabel('Energy Consumption (J)')
    plt.title(f'Comparison of Energy Consumption ({attack_type.capitalize()})')
    plt.legend()
    plt.grid(True)
    plt.savefig(f'energy_consumption_comparison_{attack_type}.png')
    plt.show()

    # Plot Node Failure Rate
    plt.figure(figsize=(10, 6))
    for metrics in all_averaged_metrics:
        plt.plot(rounds, metrics['node_failure_rate'], label=metrics['label'])
    plt.xlabel('Rounds')
    plt.ylabel('Node Failure Rate')
    plt.title(f'Comparison of Node Failure Rate ({attack_type.capitalize()})')
    plt.legend()
    plt.grid(True)
    plt.savefig(f'node_failure_rate_comparison_{attack_type}.png')
    plt.show()

def visualize_combined_results(all_averaged_metrics_list):
    # Combined plot for all attack types
    attack_types = ['selective_forwarding', 'dos']
    metrics_types = ['detection_rate', 'energy_consumption', 'node_failure_rate']
    metrics_titles = {
        'detection_rate': 'Detection Rate',
        'energy_consumption': 'Energy Consumption (J)',
        'node_failure_rate': 'Node Failure Rate'
    }

    for metrics_type in metrics_types:
        plt.figure(figsize=(10, 6))
        for all_averaged_metrics, attack_type in zip(all_averaged_metrics_list, attack_types):
            rounds = list(range(1, len(all_averaged_metrics[0][metrics_type]) + 1))
            for metrics in all_averaged_metrics:
                plt.plot(rounds, metrics[metrics_type], label=f"{metrics['label']} ({attack_type})")
        plt.xlabel('Rounds')
        plt.ylabel(metrics_titles[metrics_type])
        plt.title(f'Comparison of {metrics_titles[metrics_type]} for All Attack Types')
        plt.legend()
        plt.grid(True)
        plt.savefig(f'combined_{metrics_type}_comparison.png')
        plt.show()

def main():
    # Example usage of visualize_results function
    # all_averaged_metrics would be generated from the security_tests.py script
    all_averaged_metrics_list = [
        [
            {'label': 'Aperiodic', 'detection_rate': [0.9] * 100, 'energy_consumption': [100] * 100, 'node_failure_rate': [0.05] * 100},
            {'label': 'Hexagonal', 'detection_rate': [0.8] * 100, 'energy_consumption': [150] * 100, 'node_failure_rate': [0.1] * 100},
            {'label': 'Triangular', 'detection_rate': [0.85] * 100, 'energy_consumption': [130] * 100, 'node_failure_rate': [0.07] * 100},
            {'label': 'Square', 'detection_rate': [0.75] * 100, 'energy_consumption': [160] * 100, 'node_failure_rate': [0.12] * 100},
        ],
        [
            {'label': 'Aperiodic', 'detection_rate': [0.85] * 100, 'energy_consumption': [110] * 100, 'node_failure_rate': [0.06] * 100},
            {'label': 'Hexagonal', 'detection_rate': [0.78] * 100, 'energy_consumption': [155] * 100, 'node_failure_rate': [0.11] * 100},
            {'label': 'Triangular', 'detection_rate': [0.82] * 100, 'energy_consumption': [135] * 100, 'node_failure_rate': [0.08] * 100},
            {'label': 'Square', 'detection_rate': [0.72] * 100, 'energy_consumption': [165] * 100, 'node_failure_rate': [0.13] * 100},
        ]
    ]

    visualize_combined_results(all_averaged_metrics_list)

if __name__ == "__main__":
    main()
