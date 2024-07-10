from spectre import buildSpectreTiles, get_color_array, SPECTRE_POINTS, Mystic_SPECTRE_POINTS, Edge_a, Edge_b, N_ITERATIONS, print_trot_inv_prof
from time import time
import matplotlib.pyplot as plt
import numpy as np

# Parameters
SENSOR_RADIUS = 10  # Example value for sensor radius

def calculate_sensor_radius(tile_points):
    """Calculate the sensor radius to inscribe the spectre monotile within a circle."""
    longest_distance = max(np.linalg.norm(pt - np.mean(tile_points, axis=0)) for pt in tile_points)
    return longest_distance

def place_sensors_inscribed(tile_transformation, label):
    global sensor_positions
    tile_points = (SPECTRE_POINTS if label != "Gamma2" else Mystic_SPECTRE_POINTS).dot(tile_transformation[:, :2].T) + tile_transformation[:, 2]
    centroid = np.mean(tile_points, axis=0)
    sensor_positions.append(centroid)

start = time()
spectreTiles = buildSpectreTiles(N_ITERATIONS, Edge_a, Edge_b)
time1 = time() - start

print(f"supertiling loop took {round(time1, 4)} seconds")

start = time()
plt.figure(figsize=(8, 8))
plt.axis('equal')

sensor_counts = []
num_tiles = 0
sensor_positions = []

def plotVertices(tile_transformation, label):
    global num_tiles, sensor_positions
    num_tiles += 1
    vertices = (SPECTRE_POINTS if label != "Gamma2" else Mystic_SPECTRE_POINTS).dot(tile_transformation[:, :2].T) + tile_transformation[:, 2]
    color_array = get_color_array(tile_transformation, label)
    plt.fill(vertices[:, 0], vertices[:, 1], facecolor=color_array)
    plt.plot(vertices[:, 0], vertices[:, 1], color='gray', linewidth=0.2)
    place_sensors_inscribed(tile_transformation, label)

spectreTiles["Delta"].forEachTile(plotVertices)
time2 = time() - start
print(f"matplotlib.pyplot: tile recursion loop took {round(time2, 4)} seconds, generated {num_tiles} tiles")
print_trot_inv_prof()

sensor_counts.append(len(sensor_positions))
print(f"Number of sensors: {sensor_counts[-1]}")

start = time()
saveFileName = f"spectre_tile{Edge_a:.1f}-{Edge_b:.1f}_{N_ITERATIONS}-{num_tiles}pts.svg"
print("matplotlib.pyplot: file save to " + saveFileName)
plt.savefig(saveFileName)
time3 = time() - start
print(f"matplotlib.pyplot SVG drawing took {round(time3, 4)} seconds")
print(f"matplotlib.pyplot total processing time {round(time1 + time2 + time3, 4)} seconds, {round(1000000 * (time1 + time2 + time3) / num_tiles, 4)} μs/tile")

plt.show()

# Print the total number of sensors
print(f"Total number of sensors for iteration {N_ITERATIONS}: {sensor_counts[-1]}")
