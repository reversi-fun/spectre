import numpy as np
from matplotlib.patches import Polygon
from shapely.geometry import Polygon as ShapelyPolygon
from spectre import buildSpectreBase, transPt, SPECTRE_POINTS

def calculate_spectre_area():
    # Extract the vertices of the Spectre tile
    tile_points = [transPt(np.eye(3), pt) for pt in SPECTRE_POINTS]
    tile_points_2d = np.array(tile_points)[:, :2]

    # Create a polygon and calculate its area
    polygon = ShapelyPolygon(tile_points_2d)
    spectre_area = polygon.area
    
    return spectre_area

def calculate_rate_of_overlap(spectre_area, sensor_radius):
    circle_area = np.pi * sensor_radius**2
    rate_of_overlap = 1 - (spectre_area / circle_area)
    return rate_of_overlap

# Parameters
SENSOR_RADIUS = 10  # Adjust based on the actual sensing range required

# Calculate the area of a Spectre tile
spectre_area = calculate_spectre_area()

# Calculate the rate of overlap
rate_of_overlap = calculate_rate_of_overlap(spectre_area, SENSOR_RADIUS)

print(f"Spectre area: {spectre_area:.2f}")
print(f"Sensor radius: {SENSOR_RADIUS}")
print(f"Rate of overlap: {rate_of_overlap:.2%}")
