import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go

# Load data
planet_info = pd.read_csv('modified_planets.csv')
coordinates = pd.read_csv('planetary_coordinates_2025_01_16.csv')

# Scaling factor for visualization
SCALING_FACTOR = 5  # Increase to space out planets more

# Functions for planet position calculations
def calculate_angle(revolution_days, velocity, perimeter, time_difference):
    distance_travelled = velocity * time_difference
    angle_moved = (distance_travelled / perimeter) * 360
    return angle_moved

def get_new_coordinates(user_date_str):
    user_date = datetime.strptime(user_date_str, "%Y-%m-%d")
    date_16jan2025 = datetime(2025, 1, 16)
    time_difference = (user_date - date_16jan2025).days
    new_coordinates = []

    for _, planet_row in planet_info.iterrows():
        planet = planet_row['Planet']
        revolution_days = planet_row['Orbital Period (days)']
        velocity = planet_row['Orbital Velocity (km/s)'] * 86400
        perimeter = planet_row['Perimeter (10^6)(km)'] * 1e6
        inclination = np.radians(planet_row['Orbital Inclination (degrees)'])

        initial_coords = coordinates[coordinates['Planet'] == planet].iloc[0]
        x, y, z = initial_coords['X (AU)'], initial_coords['Y (AU)'], initial_coords['Z (AU)']

        angle_moved = calculate_angle(revolution_days, velocity, perimeter, time_difference)
        angle_radians = np.radians(angle_moved)

        new_x = x * np.cos(angle_radians) - y * np.sin(angle_radians)
        new_y = x * np.sin(angle_radians) + y * np.cos(angle_radians)
        new_z = z * np.cos(inclination)

        # Scale the positions for better visibility
        new_coordinates.append({
            'Planet': planet,
            'New_X (AU)': new_x * SCALING_FACTOR,
            'New_Y (AU)': new_y * SCALING_FACTOR,
            'New_Z (AU)': new_z * SCALING_FACTOR
        })

    return pd.DataFrame(new_coordinates)

# Initialize the Dash app
app = dash.Dash(__name__)

# Layout
app.layout = html.Div([
    html.H1("Solar System Viewer", style={'textAlign': 'center', 'color': '#FFD700'}),
    html.Div([
        html.Label("Enter Date (YYYY-MM-DD):", style={'color': 'white'}),
        dcc.Input(id='user_date', type='text', placeholder="YYYY-MM-DD", style={'marginRight': '10px'}),
        html.Button("Calculate", id='calculate_button', n_clicks=0, style={'backgroundColor': '#1E90FF', 'color': 'white'}),
    ], style={'textAlign': 'center', 'marginBottom': '20px'}),
    html.Div(id='status_output', style={'textAlign': 'center', 'color': 'red', 'marginBottom': '20px'}),
    dcc.Graph(id='solar_system_plot', style={'height': '80vh', 'width': '100%'})
])

# Callback for updates
@app.callback(
    [Output('status_output', 'children'), Output('solar_system_plot', 'figure')],
    [Input('calculate_button', 'n_clicks')],
    [State('user_date', 'value')]
)
def update_solar_system(n_clicks, user_date_str):
    if n_clicks > 0:
        if not user_date_str:
            return "Please enter a valid date.", go.Figure()

        try:
            new_coords = get_new_coordinates(user_date_str)
            fig = go.Figure()

            # Add the Sun at the center
            fig.add_trace(go.Scatter(
                x=[0], y=[0], mode='markers',
                marker=dict(size=40, color='yellow'),
                name='Sun'
            ))

            # Add each planet's current position with improved markers
            for _, row in new_coords.iterrows():
                fig.add_trace(go.Scatter(
                    x=[row['New_X (AU)']],
                    y=[row['New_Y (AU)']],
                    mode='markers+text',
                    marker=dict(size=15),
                    name=row['Planet'],
                    text=row['Planet'],
                    textposition='top center'
                ))

            # Add orbit lines for each planet
            for _, planet_row in coordinates.iterrows():
                orbit_x = [planet_row['X (AU)'] * np.cos(t) - planet_row['Y (AU)'] * np.sin(t) for t in np.linspace(0, 2*np.pi, 100)]
                orbit_y = [planet_row['X (AU)'] * np.sin(t) + planet_row['Y (AU)'] * np.cos(t) for t in np.linspace(0, 2*np.pi, 100)]
                fig.add_trace(go.Scatter(
                    x=[x * SCALING_FACTOR for x in orbit_x],
                    y=[y * SCALING_FACTOR for y in orbit_y],
                    mode='lines',
                    line=dict(dash='dot', width=1, color='lightgray'),
                    showlegend=False
                ))

            # Update layout for better visualization
            fig.update_layout(
                title="Solar System Visualization",
                xaxis=dict(title="X (AU)", range=[-100, 100], zeroline=False),
                yaxis=dict(title="Y (AU)", range=[-100, 100], zeroline=False),
                paper_bgcolor="#1A202C",
                plot_bgcolor="#2D3748",
                font=dict(color="white"),
                showlegend=True
            )

            return "Coordinates updated successfully!", fig
        except Exception as e:
            return f"Error: {str(e)}", go.Figure()

    return "Enter a date to calculate.", go.Figure()

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
