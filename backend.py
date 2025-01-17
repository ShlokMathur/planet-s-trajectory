import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import os

# Load data
planet_info = pd.read_csv(r'C:\Users\Shlok Mathur\Desktop\practice_codes\modified_planets.csv')
coordinates = pd.read_csv(r'C:\Users\Shlok Mathur\Desktop\practice_codes\planetary_coordinates_2025_01_16.csv')

# Your existing functions here...
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

# Layout for the app
app.layout = html.Div([
    html.H1("Planetary Coordinates Calculator"),
    
    # Date input field
    html.Div([
        html.Label("Enter the date (YYYY-MM-DD):"),
        dcc.Input(id='user_date', type='text', placeholder="YYYY-MM-DD", style={'margin': '10px'})
    ]),
    
    # Button to calculate the new coordinates
    html.Div([
        html.Button("Calculate New Coordinates", id='calculate_button', n_clicks=0)
    ]),
    
    # Output area to display the status
    html.Div([
        html.Div(id='status_output')
    ]),

    # 3D Graph to display planetary coordinates
    dcc.Graph(id='3d_plot')
])

# Callback to update the output based on user input
@app.callback(
    [Output('status_output', 'children'),
     Output('3d_plot', 'figure')],
    [Input('calculate_button', 'n_clicks')],
    [Input('user_date', 'value')]
)
def update_coordinates(n_clicks, user_date_str):
    if n_clicks > 0 and user_date_str:
        try:
            new_coords = get_new_coordinates(user_date_str)
            output_filename = r"C:\Users\Shlok Mathur\Desktop\practice_codes\planet_coordinates_new.csv"
            new_coords.to_csv(output_filename, index=False)
            
            # Create a 3D plot using Plotly
            fig = px.scatter_3d(new_coords, x='New_X (AU)', y='New_Y (AU)', z='New_Z (AU)', color='Planet',
                                title="Planetary Positions in 3D", labels={"New_X (AU)": "X (AU)", "New_Y (AU)": "Y (AU)", "New_Z (AU)": "Z (AU)"})
            fig.update_layout(scene=dict(xaxis_title='X (AU)', yaxis_title='Y (AU)', zaxis_title='Z (AU)'))
            
            return f"New coordinates have been saved to: {output_filename}", fig
        except Exception as e:
            return f"An error occurred: {str(e)}", {}
    return "Enter a valid date and click 'Calculate New Coordinates'", {}

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
