import numpy as np
from shapely.geometry import Polygon
from spectre import buildSpectreBase, transPt, get_spectre_points

def calculate_spectre_area(edge_a, edge_b):
    """
    Calculate the area of the spectre tile based on its vertices.
    """
    tile_points = [transPt(np.eye(3), pt) for pt in get_spectre_points(edge_a, edge_b)]
    spectre_polygon = Polygon(tile_points)
    return spectre_polygon.area

def calculate_rate_of_overlap(edge_a, edge_b, sensor_radius):
    """
    Calculate the rate of overlap for the spectre tile inscribed in a circular sensor range.
    """
    spectre_area = calculate_spectre_area(edge_a, edge_b)
    circle_area = np.pi * (sensor_radius ** 2)

    rate_of_overlap = (circle_area - spectre_area) / circle_area
    return rate_of_overlap

# Parameters
EDGE_A = 5.0
EDGE_B = 5.0
SENSOR_RADIUS = 12  # Use this radius as 'r' for the calculations

# Calculate the area of a Spectre tile
spectre_area = calculate_spectre_area(EDGE_A, EDGE_B)

# Calculate the rate of overlap
rate_of_overlap = calculate_rate_of_overlap(EDGE_A, EDGE_B, SENSOR_RADIUS)

print(f"Spectre area: {spectre_area:.2f}")
print(f"Sensor radius: {SENSOR_RADIUS}")
print(f"Rate of overlap: {rate_of_overlap:.2%}")
