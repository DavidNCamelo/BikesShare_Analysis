'''
Created by David Camelo helped by ChatGPT February 2025

First steps on web data visualization with Plotly and Dash
'''
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from CleaningTrips import CleanData

# Load data
trips = pd.read_csv('trip_data.csv', parse_dates=['Start Date', 'End Date'])
stations = pd.read_csv('station_data.csv')

# Clean and transform data
trips = CleanData(trips).clean_data().replace_station().get_data()

# Merge station names
trips = trips.merge(stations[['Id', 'Name']], left_on='Start Station', right_on='Id', how='left')
trips.rename(columns={'Name': 'start_station_name'}, inplace=True)

trips = trips.merge(stations[['Id', 'Name']], left_on='End Station', right_on='Id', how='left')
trips.rename(columns={'Name': 'end_station_name'}, inplace=True)

# Extract year and month for filtering
trips['Year-Month'] = trips['Start Date'].dt.to_period('M')

# Generate dropdown options for stations
station_options = [{'label': s, 'value': s} for s in stations['Name'].dropna().unique()]
station_options.insert(0, {'label': 'All', 'value': 'All'})

# Generate date range options (Year-Month)
date_options = [{'label': str(d), 'value': str(d)} for d in sorted(trips['Year-Month'].unique())]
date_options.insert(0, {'label': 'All', 'value': 'All'})

# Initialize Dash app
app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1("Bike Trips Analysis", style={'textAlign': 'center'}),
    
    # Date filter (Year-Month)
    html.Label("Year-Month:", style={'fontSize': 18}),
    dcc.Dropdown(id='date-dropdown', options=date_options, value='All', clearable=False),

    # Start and End station filters
    html.Div([ 
        html.Div([ 
            html.Label("Start Station:", style={'fontSize': 18}),
            dcc.Dropdown(id='start-station-dropdown', options=station_options, value='All', clearable=False)
        ], style={'width': '48%'}),
        html.Div([ 
            html.Label("End Station:", style={'fontSize': 18}),
            dcc.Dropdown(id='end-station-dropdown', options=station_options, value='All', clearable=False)
        ], style={'width': '48%'})
    ], style={'display': 'flex', 'justify-content': 'space-between'}),

    # Graphs for trips by station with scrollable container
    html.Div([
        html.Div([
            dcc.Graph(id='graph-start', style={'height': '350px'})
        ], style={'width': '49%', 'overflowY': 'scroll'}),

        html.Div([
            dcc.Graph(id='graph-end', style={'height': '350px'})
        ], style={'width': '49%', 'overflowY': 'scroll'})
    ], style={'display': 'flex', 'justify-content': 'space-between'}),

    # Graphs for trips by hour
    html.Div([ 
        dcc.Graph(id='graph-start-hour', style={'display': 'inline-block', 'width': '49%'}),
        dcc.Graph(id='graph-end-hour', style={'display': 'inline-block', 'width': '49%'})
    ])
])

@app.callback(
    [Output('graph-start', 'figure'), Output('graph-end', 'figure'),
     Output('graph-start-hour', 'figure'), Output('graph-end-hour', 'figure')],
    [Input('date-dropdown', 'value'),
     Input('start-station-dropdown', 'value'),
     Input('end-station-dropdown', 'value')]
)
def update_graphs(selected_date, selected_start, selected_end):
    # Filter data based on selected date
    filtered_trips = trips if selected_date == 'All' else trips[trips['Year-Month'] == selected_date]

    # Filter start station
    if selected_start != 'All':
        filtered_trips = filtered_trips[filtered_trips['start_station_name'] == selected_start]

    # Filter end station (in reverse for "End Station" filter)
    if selected_end != 'All':
        filtered_trips = filtered_trips[filtered_trips['end_station_name'] == selected_end]

    # Count trips by start station for the "Started" graph
    start_counts = filtered_trips['start_station_name'].value_counts().reset_index()
    start_counts.columns = ['Station', 'Trips Started']
    start_counts = start_counts.sort_values(by='Trips Started', ascending=False)

    # Count trips by end station for the "Ended" graph
    end_counts = filtered_trips['end_station_name'].value_counts().reset_index()
    end_counts.columns = ['Station', 'Trips Ended']
    end_counts = end_counts.sort_values(by='Trips Ended', ascending=False)

    # Count trips by start hour for the "Started by Hour" graph (using Start Hour)
    start_hour_counts = filtered_trips['Start Hour'].value_counts().sort_index().reset_index()
    start_hour_counts.columns = ['Hour', 'Trips Started Per Hour']
    
    # Count trips by end hour for the "Ended by Hour" graph (using End Hour)
    end_hour_counts = filtered_trips['End Hour'].value_counts().sort_index().reset_index()
    end_hour_counts.columns = ['Hour', 'Trips Ended Per Hour']

    # Create horizontal bar charts for trips by station
    fig_start = px.bar(start_counts, y='Station', x='Trips Started', title="Trips Started by Station",
                       orientation='h', color_discrete_sequence=['#1f77b4'], category_orders={"Station": start_counts['Station'].tolist()})

    fig_end = px.bar(end_counts, y='Station', x='Trips Ended', title="Trips Ended by Station",
                     orientation='h', color_discrete_sequence=['#ff7f0e'], category_orders={"Station": end_counts['Station'].tolist()})

    # Adjust layout for scrollable container and bar alignment with increased space between bars and stations
    fig_start.update_layout(
        autosize=True,
        height=1000,  # Adjust height for scrolling
        yaxis=dict(
            fixedrange=True,
            showgrid=False,
            tickvals=start_counts['Station'],
            ticktext=start_counts['Station'],
            ticklen=45  # Increase the space between the bars and the station names
        ),
        showlegend=False,
        margin=dict(l=0, r=0, t=50, b=0),
        xaxis=dict(
            showgrid=True,
            showline=True,  # x-axis visible for alignment
        ),
        plot_bgcolor="white"
    )

    fig_end.update_layout(
        autosize=True,
        height=1000,  # Adjust height for scrolling
        yaxis=dict(
            fixedrange=True,
            showgrid=False,
            tickvals=end_counts['Station'],
            ticktext=end_counts['Station'],
            ticklen=45  # Increase the space between the bars and the station names
        ),
        showlegend=False,
        margin=dict(l=0, r=0, t=50, b=0),
        xaxis=dict(
            showgrid=True,
            showline=True,  # x-axis visible for alignment
        ),
        plot_bgcolor="white"
    )
    
    # Adjust layout for bar charts based on tooltips and hover interactions
    fig_start.update_traces(
        texttemplate="%{x:,.0f}",  # Format with comma separator
        textposition="outside",
        hovertemplate="<b>Station:</b> %{y}<br><b>Trips Started:</b> %{x:,.0f}<extra></extra>"
    )

    fig_end.update_traces(
        texttemplate="%{x:,.0f}",  # Format with comma separator
        textposition="outside",
        hovertemplate="<b>Station:</b> %{y}<br><b>Trips Ended:</b> %{x:,.0f}<extra></extra>"
    )

    fig_start.update_layout(
        xaxis=dict(tickformat=","),  # Maintain comma separator for x-axis
        hovermode="closest"
    )

    fig_end.update_layout(
        xaxis=dict(tickformat=","),  # Maintain comma separator for x-axis
        hovermode="closest"
    )

    # Create vertical bar charts for trips by hour
    fig_start_hour = px.bar(start_hour_counts, x='Hour', y='Trips Started Per Hour', title="Trips Started Per Hour",
                            color_discrete_sequence=['#1f77b4'])

    fig_end_hour = px.bar(end_hour_counts, x='Hour', y='Trips Ended Per Hour', title="Trips Ended Per Hour",
                          color_discrete_sequence=['#ff7f0e'])

        # Adjust layout for bar charts based on tooltips and hover interactions
    fig_start_hour.update_traces(
        texttemplate="%{y:,.0f}",  # Format with comma separator
        textposition="outside",
        hovertemplate="<b>Start hour:</b> %{x}<br><b>Trips Started:</b> %{y:,.0f}<extra></extra>"
    )

    fig_end_hour.update_traces(
        texttemplate="%{y:,.0f}",  # Format with comma separator
        textposition="outside",
        hovertemplate="<b>End hour:</b> %{x}<br><b>Trips Ended:</b> %{y:,.0f}<extra></extra>"
    )


    return fig_start, fig_end, fig_start_hour, fig_end_hour

if __name__ == '__main__':
    app.run_server(debug=True)
