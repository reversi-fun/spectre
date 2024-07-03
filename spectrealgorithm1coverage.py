import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle
from spectre import buildSpectreBase, transPt, MetaTile, buildSupertiles, SPECTRE_POINTS

# Parameters
N_ITERATIONS = 3
SENSOR_RADIUS = 5  # Adjusted radius for better coverage

def generate_spectre_tiles():
    shapes = buildSpectreBase()
    for _ in range(N_ITERATIONS):
        shapes = buildSupertiles(shapes)
    return shapes

def place_sensors(shapes):
    sensor_positions = []
    for meta_tile_name, meta_tile in shapes.items():
        if isinstance(meta_tile, MetaTile):
            for tile, transformation in zip(meta_tile.tiles, meta_tile.transformations):
                # Add sensors at vertices
                for pt in tile.quad:
                    sensor_positions.append(transPt(transformation, pt).xy)
                # Add sensors at midpoints of edges
                for i in range(len(tile.quad)):
                    pt1 = transPt(transformation, tile.quad[i])
                    pt2 = transPt(transformation, tile.quad[(i + 1) % len(tile.quad)])
                    midpoint = [(pt1.x + pt2.x) / 2, (pt1.y + pt2.y) / 2]
                    sensor_positions.append(midpoint)
        else:
            print(f"Unexpected type: {type(meta_tile)}")
    return sensor_positions

def plot_spectre_tiles_with_sensors(shapes, sensor_positions):
    fig, ax = plt.subplots(figsize=(10, 10))
    for meta_tile_name, meta_tile in shapes.items():
        if isinstance(meta_tile, MetaTile):
            for tile, transformation in zip(meta_tile.tiles, meta_tile.transformations):
                points = [transPt(transformation, pt).xy for pt in tile.quad]
                polygon = Polygon(points, closed=True, fill=None, edgecolor='b')
                ax.add_patch(polygon)

    for sensor_pos in sensor_positions:
        circle = Circle(sensor_pos, SENSOR_RADIUS, color='r', fill=False, linestyle='dotted')
        ax.add_patch(circle)
        ax.plot(sensor_pos[0], sensor_pos[1], 'ko')  # Sensor node as black dot

    ax.set_xlim(-100, 100)
    ax.set_ylim(-100, 100)
    ax.set_aspect('equal', adjustable='box')
    plt.grid(True)
    plt.title("Spectre Tile with Sensors for 1-Coverage")
    plt.savefig("spectre_with_sensors_1_coverage_corrected.png")
    plt.show()

# Generate spectre tiles
shapes = generate_spectre_tiles()

# Place sensors at strategic points
sensor_positions = place_sensors(shapes)

# Plot the spectre tiles with sensor nodes
plot_spectre_tiles_with_sensors(shapes, sensor_positions)
