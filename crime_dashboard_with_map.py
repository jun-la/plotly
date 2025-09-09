import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

# State FIPS code mapping (partial - for the states that have data)
STATE_FIPS_MAPPING = {
    1: 'AL', 2: 'AK', 4: 'AZ', 5: 'AR', 6: 'CA', 8: 'CO', 9: 'CT', 10: 'DE', 
    11: 'DC', 12: 'FL', 13: 'GA', 15: 'HI', 16: 'ID', 17: 'IL', 18: 'IN', 
    19: 'IA', 20: 'KS', 21: 'KY', 22: 'LA', 23: 'ME', 24: 'MD', 25: 'MA', 
    26: 'MI', 27: 'MN', 28: 'MS', 29: 'MO', 30: 'MT', 31: 'NE', 32: 'NV', 
    33: 'NH', 34: 'NJ', 35: 'NM', 36: 'NY', 37: 'NC', 38: 'ND', 39: 'OH', 
    40: 'OK', 41: 'OR', 42: 'PA', 44: 'RI', 45: 'SC', 46: 'SD', 47: 'TN', 
    48: 'TX', 49: 'UT', 50: 'VT', 51: 'VA', 53: 'WA', 54: 'WV', 55: 'WI', 56: 'WY'
}

def load_data():
    """Load and preprocess the UCI Communities and Crime dataset"""
    
    # Column names based on the .names file
    column_names = [
        'state', 'county', 'community', 'communityname', 'fold', 
        'population', 'householdsize', 'racepctblack', 'racePctWhite', 'racePctAsian',
        'racePctHisp', 'agePct12t21', 'agePct12t29', 'agePct16t24', 'agePct65up',
        'numbUrban', 'pctUrban', 'medIncome', 'pctWWage', 'pctWFarmSelf',
        'pctWInvInc', 'pctWSocSec', 'pctWPubAsst', 'pctWRetire', 'medFamInc',
        'perCapInc', 'whitePerCap', 'blackPerCap', 'indianPerCap', 'AsianPerCap',
        'OtherPerCap', 'HispPerCap', 'NumUnderPov', 'PctPopUnderPov', 'PctLess9thGrade',
        'PctNotHSGrad', 'PctBSorMore', 'PctUnemployed', 'PctEmploy', 'PctEmplManu',
        'PctEmplProfServ', 'PctOccupManu', 'PctOccupMgmtProf', 'MalePctDivorce', 'MalePctNevMarr',
        'FemalePctDiv', 'TotalPctDiv', 'PersPerFam', 'PctFam2Par', 'PctKids2Par',
        'PctYoungKids2Par', 'PctTeen2Par', 'PctWorkMomYoungKids', 'PctWorkMom', 'NumIlleg',
        'PctIlleg', 'NumImmig', 'PctImmigRecent', 'PctImmigRec5', 'PctImmigRec8',
        'PctImmigRec10', 'PctRecentImmig', 'PctRecImmig5', 'PctRecImmig8', 'PctRecImmig10',
        'PctSpeakEnglOnly', 'PctNotSpeakEnglWell', 'PctLargHouseFam', 'PctLargHouseOccup', 'PersPerOccupHous',
        'PersPerOwnOccHous', 'PersPerRentOccHous', 'PctPersOwnOccup', 'PctPersDenseHous', 'PctHousLess3BR',
        'MedNumBR', 'HousVacant', 'PctHousOccup', 'PctHousOwnOcc', 'PctVacantBoarded',
        'PctVacMore6Mos', 'MedYrHousBuilt', 'PctHousNoPhone', 'PctWOFullPlumb', 'OwnOccLowQuart',
        'OwnOccMedVal', 'OwnOccHiQuart', 'RentLowQ', 'RentMedian', 'RentHighQ',
        'MedRent', 'MedRentPctHousInc', 'MedOwnCostPctInc', 'MedOwnCostPctIncNoMtg', 'NumInShelters',
        'NumStreet', 'PctForeignBorn', 'PctBornSameState', 'PctSameHouse85', 'PctSameCity85',
        'PctSameState85', 'LemasSwornFT', 'LemasSwFTPerPop', 'LemasSwFTFieldOps', 'LemasSwFTFieldPerPop',
        'LemasTotalReq', 'LemasTotReqPerPop', 'PolicReqPerOffic', 'PolicPerPop', 'RacialMatchCommPol',
        'PctPolicWhite', 'PctPolicBlack', 'PctPolicHisp', 'PctPolicAsian', 'PctPolicMinor',
        'OfficAssgnDrugUnits', 'NumKindsDrugsSeiz', 'PolicAveOTWorked', 'LandArea', 'PopDens',
        'PctUsePubTrans', 'PolicCars', 'PolicOperBudg', 'LemasPctPolicOnPatr', 'LemasGangUnitDeploy',
        'LemasPctOfficDrugUn', 'PolicBudgPerPop', 'ViolentCrimesPerPop'
    ]
    
    # Load the data
    df = pd.read_csv('communities_crime.data', names=column_names, na_values='?')
    
    # Clean community names
    df['communityname'] = df['communityname'].fillna('Unknown')
    
    # Map state codes to abbreviations
    df['state_abbr'] = df['state'].map(STATE_FIPS_MAPPING)
    
    # Filter out rows with missing crime data (target variable)
    df = df.dropna(subset=['ViolentCrimesPerPop'])
    
    return df

def create_state_summary(df):
    """Create state-level aggregated data"""
    state_summary = df.groupby(['state', 'state_abbr']).agg({
        'ViolentCrimesPerPop': ['mean', 'median', 'std', 'count'],
        'population': 'sum',
        'medIncome': 'mean',
        'PctPopUnderPov': 'mean',
        'pctUrban': 'mean'
    }).round(4)
    
    # Flatten column names
    state_summary.columns = [
        'crime_rate_mean', 'crime_rate_median', 'crime_rate_std', 'num_communities',
        'total_population', 'avg_income', 'avg_poverty_rate', 'avg_urban_pct'
    ]
    
    state_summary = state_summary.reset_index()
    return state_summary

# Load data
df = load_data()
state_summary = create_state_summary(df)

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the layout with multiple pages
app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    
    # Navigation bar
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Overview", href="/", id="overview-link")),
            dbc.NavItem(dbc.NavLink("US Map", href="/map", id="map-link")),
        ],
        brand="US Crime Rate Dashboard",
        brand_href="/",
        color="primary",
        dark=True,
        className="mb-4"
    ),
    
    # Page content
    html.Div(id='page-content')
])

# Overview page layout
overview_layout = [
    dbc.Row([
        dbc.Col([
            html.H2("Crime Rate Analysis Overview", className="text-center mb-4"),
            html.P("Exploring crime rates across US communities using UCI dataset",
                   className="text-center text-muted mb-4")
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Filters", className="card-title"),
                    html.Label("State:"),
                    dcc.Dropdown(
                        id='state-dropdown',
                        options=[{'label': 'All States', 'value': 'all'}] + 
                               [{'label': f"{row.state_abbr} (State {row.state})", 'value': row.state} 
                                for _, row in state_summary.iterrows() if pd.notna(row.state_abbr)],
                        value='all',
                        className="mb-3"
                    ),
                    html.Label("Crime Rate Range:"),
                    dcc.RangeSlider(
                        id='crime-range-slider',
                        min=df['ViolentCrimesPerPop'].min(),
                        max=df['ViolentCrimesPerPop'].max(),
                        value=[df['ViolentCrimesPerPop'].min(), df['ViolentCrimesPerPop'].max()],
                        marks={
                            df['ViolentCrimesPerPop'].min(): f"{df['ViolentCrimesPerPop'].min():.2f}",
                            df['ViolentCrimesPerPop'].max(): f"{df['ViolentCrimesPerPop'].max():.2f}"
                        },
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ])
            ])
        ], width=3),
        
        dbc.Col([
            dcc.Graph(id='crime-scatter-plot')
        ], width=9)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='crime-histogram')
        ], width=6),
        dbc.Col([
            dcc.Graph(id='state-boxplot')
        ], width=6)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='correlation-heatmap')
        ], width=12)
    ])
]

# US Map page layout
map_layout = [
    dbc.Row([
        dbc.Col([
            html.H2("US Crime Rate Map", className="text-center mb-4"),
            html.P("State-level crime rates visualized on US map",
                   className="text-center text-muted mb-4")
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Map Options", className="card-title"),
                    html.Label("Metric to Display:"),
                    dcc.Dropdown(
                        id='map-metric-dropdown',
                        options=[
                            {'label': 'Average Crime Rate', 'value': 'crime_rate_mean'},
                            {'label': 'Median Crime Rate', 'value': 'crime_rate_median'},
                            {'label': 'Number of Communities', 'value': 'num_communities'}
                        ],
                        value='crime_rate_mean',
                        className="mb-3"
                    ),
                    html.Label("Color Scale:"),
                    dcc.Dropdown(
                        id='color-scale-dropdown',
                        options=[
                            {'label': 'Reds', 'value': 'Reds'},
                            {'label': 'Blues', 'value': 'Blues'},
                            {'label': 'Viridis', 'value': 'Viridis'},
                            {'label': 'Plasma', 'value': 'Plasma'}
                        ],
                        value='Reds',
                        className="mb-3"
                    )
                ])
            ])
        ], width=3),
        
        dbc.Col([
            dcc.Graph(id='us-map', style={'height': '600px'})
        ], width=9)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='state-ranking-bar')
        ], width=12)
    ])
]

@callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/map':
        return map_layout
    else:
        return overview_layout

# Overview page callbacks
@callback(
    [Output('crime-scatter-plot', 'figure'),
     Output('crime-histogram', 'figure'),
     Output('state-boxplot', 'figure'),
     Output('correlation-heatmap', 'figure')],
    [Input('state-dropdown', 'value'),
     Input('crime-range-slider', 'value')]
)
def update_overview_plots(selected_state, crime_range):
    # Filter data based on selections
    filtered_df = df.copy()
    
    if selected_state != 'all':
        filtered_df = filtered_df[filtered_df['state'] == int(selected_state)]
    
    filtered_df = filtered_df[
        (filtered_df['ViolentCrimesPerPop'] >= crime_range[0]) &
        (filtered_df['ViolentCrimesPerPop'] <= crime_range[1])
    ]
    
    # 1. Scatter plot: Population vs Crime Rate
    scatter_fig = px.scatter(
        filtered_df,
        x='population',
        y='ViolentCrimesPerPop',
        color='state_abbr',
        size='medIncome',
        hover_data=['communityname', 'pctUrban', 'PctPopUnderPov'],
        title='Crime Rate vs Population (sized by median income)',
        labels={
            'population': 'Population (normalized)',
            'ViolentCrimesPerPop': 'Violent Crimes Per Capita',
            'state_abbr': 'State'
        }
    )
    scatter_fig.update_layout(height=500)
    
    # 2. Histogram of crime rates
    hist_fig = px.histogram(
        filtered_df,
        x='ViolentCrimesPerPop',
        nbins=30,
        title='Distribution of Crime Rates',
        labels={'ViolentCrimesPerPop': 'Violent Crimes Per Capita'}
    )
    hist_fig.update_layout(height=400)
    
    # 3. Box plot by state (top 10 states with most communities)
    state_counts = filtered_df['state_abbr'].value_counts().head(10)
    top_states_df = filtered_df[filtered_df['state_abbr'].isin(state_counts.index)]
    
    box_fig = px.box(
        top_states_df,
        x='state_abbr',
        y='ViolentCrimesPerPop',
        title='Crime Rate Distribution by State (Top 10 States)',
        labels={'state_abbr': 'State', 'ViolentCrimesPerPop': 'Violent Crimes Per Capita'}
    )
    box_fig.update_layout(height=400)
    
    # 4. Correlation heatmap of key socioeconomic factors
    corr_columns = [
        'ViolentCrimesPerPop', 'medIncome', 'PctPopUnderPov', 'PctUnemployed',
        'pctUrban', 'population', 'racepctblack', 'racePctWhite', 'PctBSorMore'
    ]
    corr_data = filtered_df[corr_columns].corr()
    
    heatmap_fig = px.imshow(
        corr_data.values,
        x=corr_data.columns,
        y=corr_data.columns,
        color_continuous_scale='RdBu_r',
        title='Correlation Matrix: Crime Rate vs Socioeconomic Factors',
        text_auto=True
    )
    heatmap_fig.update_layout(height=500)
    
    return scatter_fig, hist_fig, box_fig, heatmap_fig

# Map page callbacks
@callback(
    [Output('us-map', 'figure'),
     Output('state-ranking-bar', 'figure')],
    [Input('map-metric-dropdown', 'value'),
     Input('color-scale-dropdown', 'value')]
)
def update_map_plots(selected_metric, color_scale):
    # Create choropleth map
    map_fig = px.choropleth(
        state_summary.dropna(subset=['state_abbr']),
        locations='state_abbr',
        color=selected_metric,
        locationmode='USA-states',
        color_continuous_scale=color_scale,
        scope='usa',
        title=f'US States by {selected_metric.replace("_", " ").title()}',
        hover_data={
            'crime_rate_mean': ':.4f',
            'num_communities': True,
            'avg_income': ':.4f',
            'avg_poverty_rate': ':.4f'
        },
        labels={
            'crime_rate_mean': 'Avg Crime Rate',
            'crime_rate_median': 'Median Crime Rate',
            'num_communities': 'Communities',
            'state_abbr': 'State'
        }
    )
    map_fig.update_layout(height=600)
    
    # Create ranking bar chart
    top_states = state_summary.dropna(subset=['state_abbr']).nlargest(15, selected_metric)
    
    bar_fig = px.bar(
        top_states,
        x='state_abbr',
        y=selected_metric,
        title=f'Top 15 States by {selected_metric.replace("_", " ").title()}',
        labels={
            'state_abbr': 'State',
            selected_metric: selected_metric.replace("_", " ").title()
        },
        color=selected_metric,
        color_continuous_scale=color_scale
    )
    bar_fig.update_layout(height=400)
    
    return map_fig, bar_fig

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)