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

# Functions
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

        new_coordinates.append({
            'Planet': planet,
            'New_X (AU)': new_x,
            'New_Y (AU)': new_y,
            'New_Z (AU)': new_z
        })

    new_coords_df = pd.DataFrame(new_coordinates)
    return new_coords_df

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "3D CSS Solar System Viewer"

# Layout with integrated UI
app.layout = html.Div([
    html.Div(id="navbar", children=[
        html.A("Data", id="toggle-data", href="#data", className="icon-data"),
        html.H1("3D CSS Solar System"),
        html.A("Controls", id="toggle-controls", href="#controls", className="icon-controls"),
    ]),

    html.Div(id="data", children=[
        html.A("Sun", className="sun", title="sun", href="#sunspeed"),
        html.A("Mercury", className="mercury", title="mercury", href="#mercuryspeed"),
        html.A("Venus", className="venus", title="venus", href="#venusspeed"),
        html.A("Earth", className="earth", title="earth", href="#earthspeed"),
        html.A("Mars", className="mars", title="mars", href="#marsspeed"),
        html.A("Jupiter", className="jupiter", title="jupiter", href="#jupiterspeed"),
        html.A("Saturn", className="saturn", title="saturn", href="#saturnspeed"),
        html.A("Uranus", className="uranus", title="uranus", href="#uranusspeed"),
        html.A("Neptune", className="neptune", title="neptune", href="#neptunespeed"),
    ]),

    html.Div(id="controls", children=[
        html.Label("Enter the date (YYYY-MM-DD):", style={'fontWeight': 'bold', 'marginRight': '10px'}),
        dcc.Input(id='user_date', type='text', placeholder="YYYY-MM-DD", style={'marginRight': '10px', 'padding': '5px'}),
        html.Button("Calculate", id='calculate_button', n_clicks=0, style={'padding': '5px 10px', 'backgroundColor': '#4CAF50', 'color': 'white', 'border': 'none'}),
    ]),

    html.Div(id='status_output', style={'textAlign': 'center', 'color': 'red', 'marginBottom': '20px'}),

    html.Div(id="universe", children=[
        dcc.Graph(id='solar_system_plot', style={'height': '80vh', 'width': '100%'}),
    ]),

    html.Script(src="//ajax.googleapis.com/ajax/libs/jquery/1.8.1/jquery.min.js"),
    html.Script(src="js/prefixfree.min.js"),
    html.Script(src="js/scripts.min.js"),
])

# Callback for updating the solar system plot
@app.callback(
    [Output('status_output', 'children'),
     Output('solar_system_plot', 'figure')],
    [Input('calculate_button', 'n_clicks')],
    [State('user_date', 'value')]
)
def update_solar_system(n_clicks, user_date_str):
    if n_clicks > 0:
        if not user_date_str:
            return "Please enter a valid date in YYYY-MM-DD format.", go.Figure()

        try:
            new_coords = get_new_coordinates(user_date_str)

            # Create a solar system plot
            fig = go.Figure()

            # Add the Sun at the center
            fig.add_trace(go.Scatter(
                x=[0], y=[0], mode='markers+text',
                marker=dict(size=30, color='yellow'),
                name='Sun',
                text='Sun',
                textposition='bottom center'
            ))

            # Add each planet's current position
            for _, row in new_coords.iterrows():
                fig.add_trace(go.Scatter(
                    x=[row['New_X (AU)']],
                    y=[row['New_Y (AU)']],
                    mode='markers+text',
                    marker=dict(size=10, symbol='circle'),
                    name=row['Planet'],
                    text=row['Planet'],
                    textposition='top center'
                ))

            # Update layout for visualization
            fig.update_layout(
                title="Solar System Visualization",
                xaxis=dict(title="X (AU)", range=[-35, 35], zeroline=False),
                yaxis=dict(title="Y (AU)", range=[-35, 35], zeroline=False),
                paper_bgcolor="#000",
                plot_bgcolor="#111",
                font=dict(color="white"),
                showlegend=True
            )

            return "Coordinates successfully updated!", fig
        except Exception as e:
            return f"An error occurred: {str(e)}", go.Figure()
    return "Enter a date and click 'Calculate'.", go.Figure()

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
