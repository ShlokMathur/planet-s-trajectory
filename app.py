import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import math

# Data for planetary positions (simplified circular orbits)
planets = [
    {"name": "Mercury", "distance": 57.9, "color": "gray"},
    {"name": "Venus", "distance": 108.2, "color": "yellow"},
    {"name": "Earth", "distance": 149.6, "color": "blue"},
    {"name": "Mars", "distance": 227.9, "color": "red"},
    {"name": "Jupiter", "distance": 778.3, "color": "orange"},
    {"name": "Saturn", "distance": 1427.0, "color": "gold"},
    {"name": "Uranus", "distance": 2871.0, "color": "lightblue"},
    {"name": "Neptune", "distance": 4497.1, "color": "darkblue"},
]

# Generate positions for circular orbits
def generate_positions(planets):
    positions = []
    for i, planet in enumerate(planets):
        angle = i * (2 * math.pi / len(planets))  # Evenly spaced angles
        x = planet["distance"] * math.cos(angle)
        y = planet["distance"] * math.sin(angle)
        positions.append({"name": planet["name"], "x": x, "y": y, "color": planet["color"]})
    return positions

positions = generate_positions(planets)
df_planets = pd.DataFrame(positions)

# Initialize Dash app
app = dash.Dash(__name__)

# Layout
app.layout = html.Div([
    html.H1("Solar System Visualization", style={"textAlign": "center"}),
    dcc.Graph(
        id="solar-system-plot",
        style={"height": "80vh"},
    ),
])

# Callback to update the 2D plot
@app.callback(
    Output("solar-system-plot", "figure"),
    Input("solar-system-plot", "id")
)
def update_plot(_):
    # Create 2D scatter plot for planets and their orbits
    traces = []

    # Add orbits as circular lines
    for planet in planets:
        theta = [i * (2 * math.pi / 100) for i in range(101)]  # Create points for a circle
        x_orbit = [planet["distance"] * math.cos(t) for t in theta]
        y_orbit = [planet["distance"] * math.sin(t) for t in theta]
        orbit_trace = go.Scatter(
            x=x_orbit,
            y=y_orbit,
            mode="lines",
            line=dict(color="lightgray", dash="dot"),
            name=f"{planet['name']} Orbit",
        )
        traces.append(orbit_trace)

    # Add planets
    for _, row in df_planets.iterrows():
        planet_trace = go.Scatter(
            x=[row["x"]],
            y=[row["y"]],
            mode="markers+text",
            marker=dict(size=10, color=row["color"]),
            text=row["name"],
            textposition="top center",
        )
        traces.append(planet_trace)

    # Add the Sun at the origin
    sun_trace = go.Scatter(
        x=[0],
        y=[0],
        mode="markers+text",
        marker=dict(size=15, color="yellow"),
        text="Sun",
        textposition="top center",
    )
    traces.append(sun_trace)

    # Layout configuration
    layout = go.Layout(
        xaxis=dict(title="X (millions of km)", showgrid=False, zeroline=False),
        yaxis=dict(title="Y (millions of km)", showgrid=False, zeroline=False),
        margin=dict(l=0, r=0, b=0, t=0),
        showlegend=False,
        plot_bgcolor="black"
    )

    return go.Figure(data=traces, layout=layout)

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
