import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

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
    
    # Create state mapping (simplified - using state code as identifier)
    df['state_name'] = df['state'].astype(str)
    
    # Filter out rows with missing crime data (target variable)
    df = df.dropna(subset=['ViolentCrimesPerPop'])
    
    return df

# Load data
df = load_data()

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("US Communities Crime Rate Visualization", 
                   className="text-center mb-4"),
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
                               [{'label': f"State {state}", 'value': state} 
                                for state in sorted(df['state'].unique())],
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
    
], fluid=True)

@callback(
    [Output('crime-scatter-plot', 'figure'),
     Output('crime-histogram', 'figure'),
     Output('state-boxplot', 'figure'),
     Output('correlation-heatmap', 'figure')],
    [Input('state-dropdown', 'value'),
     Input('crime-range-slider', 'value')]
)
def update_plots(selected_state, crime_range):
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
        color='state',
        size='medIncome',
        hover_data=['communityname', 'pctUrban', 'PctPopUnderPov'],
        title='Crime Rate vs Population (sized by median income)',
        labels={
            'population': 'Population (normalized)',
            'ViolentCrimesPerPop': 'Violent Crimes Per Capita',
            'medIncome': 'Median Income'
        }
    )
    scatter_fig.update_layout(height=500)
    
    # 2. Histogram of crime rates
    hist_fig = px.histogram(
        filtered_df,
        x='ViolentCrimesPerPop',
        nbins=30,
        title='Distribution of Crime Rates',
        labels={'ViolentCrimesPerPop': 'Violent Crimes Per Capita', 'count': 'Number of Communities'}
    )
    hist_fig.update_layout(height=400)
    
    # 3. Box plot by state (top 10 states with most communities)
    state_counts = filtered_df['state'].value_counts().head(10)
    top_states_df = filtered_df[filtered_df['state'].isin(state_counts.index)]
    
    box_fig = px.box(
        top_states_df,
        x='state',
        y='ViolentCrimesPerPop',
        title='Crime Rate Distribution by State (Top 10 States)',
        labels={'state': 'State Code', 'ViolentCrimesPerPop': 'Violent Crimes Per Capita'}
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)