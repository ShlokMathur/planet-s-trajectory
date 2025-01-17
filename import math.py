import math
import pandas as pd
from datetime import datetime

# Constants
AU = 149597870.7  # Astronomical unit in kilometers

# Orbital parameters for the planets (source: NASA)
# Units: semi-major axis (AU), eccentricity, inclination (degrees),
# longitude of ascending node (degrees), argument of perihelion (degrees), orbital period (years)
planets = [
    {"name": "Mercury", "a": 0.387, "e": 0.206, "i": 7.0, "\u03a9": 48.33, "\u03c9": 29.12, "P": 0.241},
    {"name": "Venus", "a": 0.723, "e": 0.007, "i": 3.39, "\u03a9": 76.68, "\u03c9": 54.88, "P": 0.615},
    {"name": "Earth", "a": 1.000, "e": 0.017, "i": 0.00, "\u03a9": 0.00, "\u03c9": 102.94, "P": 1.000},
    {"name": "Mars", "a": 1.524, "e": 0.093, "i": 1.85, "\u03a9": 49.56, "\u03c9": 286.50, "P": 1.881},
    {"name": "Jupiter", "a": 5.203, "e": 0.049, "i": 1.31, "\u03a9": 100.56, "\u03c9": 273.87, "P": 11.862},
    {"name": "Saturn", "a": 9.537, "e": 0.056, "i": 2.49, "\u03a9": 113.72, "\u03c9": 339.39, "P": 29.457},
    {"name": "Uranus", "a": 19.191, "e": 0.047, "i": 0.77, "\u03a9": 74.00, "\u03c9": 96.99, "P": 84.020},
    {"name": "Neptune", "a": 30.069, "e": 0.009, "i": 1.77, "\u03a9": 131.79, "\u03c9": 265.64, "P": 164.8},
    {"name": "Pluto", "a": 39.482, "e": 0.249, "i": 17.16, "\u03a9": 110.30, "\u03c9": 113.77, "P": 248.0}
]

# Reference date
reference_date = datetime(2022, 1, 1)

# Get user input for the current date
current_date_input = input("Enter the current date (YYYY-MM-DD): ")
current_date = datetime.strptime(current_date_input, "%Y-%m-%d")
days_since_reference = (current_date - reference_date).days

# Compute positions for all planets
results = []
for planet in planets:
    # Orbital parameters
    a = planet["a"] * AU  # Semi-major axis in km
    e = planet["e"]
    i = math.radians(planet["i"])  # Inclination in radians
    Ω = math.radians(planet["\u03a9"])  # Longitude of ascending node in radians
    ω = math.radians(planet["\u03c9"])  # Argument of perihelion in radians
    P = planet["P"] * 365.25  # Orbital period in days

    # Mean anomaly
    mean_motion = 2 * math.pi / P  # Mean motion in radians per day
    mean_anomaly = mean_motion * days_since_reference

    # True anomaly (approximation for small eccentricity)
    true_anomaly = mean_anomaly + 2 * e * math.sin(mean_anomaly)

    # Distance from the Sun
    distance = a * (1 - e**2) / (1 + e * math.cos(true_anomaly))

    # Position in orbital plane
    x_orbital = distance * math.cos(true_anomaly)
    y_orbital = distance * math.sin(true_anomaly)

    # Transform to ecliptic coordinates
    x_ecliptic = (
        x_orbital * (math.cos(ω) * math.cos(Ω) - math.sin(ω) * math.sin(Ω) * math.cos(i))
        - y_orbital * (math.sin(ω) * math.cos(Ω) + math.cos(ω) * math.sin(Ω) * math.cos(i))
    )
    y_ecliptic = (
        x_orbital * (math.cos(ω) * math.sin(Ω) + math.sin(ω) * math.cos(Ω) * math.cos(i))
        + y_orbital * (math.cos(ω) * math.cos(Ω) * math.cos(i) - math.sin(ω) * math.sin(Ω))
    )
    z_ecliptic = (
        x_orbital * math.sin(ω) * math.sin(i)
        + y_orbital * math.cos(ω) * math.sin(i)
    )

    # Append results
    results.append({
        "Planet": planet["name"],
        "x (km)": x_ecliptic,
        "y (km)": y_ecliptic,
        "z (km)": z_ecliptic
    })

# Create a DataFrame to display the results
df_results = pd.DataFrame(results)
print(df_results)
