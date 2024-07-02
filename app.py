import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Load the data
df = pd.read_excel('/Users/careyqiu/Desktop/YouGov_2024_general_election_MRP_2.xlsx', sheet_name='data-5sWjS (1)')

# Define a modern pastel color palette similar to "Chartr"
color_discrete_map = {
    'ConShare': '#8ecae6',  # Light Blue
    'LabShare': '#ffb703',  # Light Yellow
    'LibDemShare': '#fb8500',  # Light Orange
    'GreenShare': '#219ebc',  # Soft Green
    'ReformShare': '#adb5bd'  # Soft Grey
}

# Initialize Dash app
app = dash.Dash(__name__)

# Layout
app.layout = html.Div([
    html.H1("2024 UK Election - Projected Vote Shares", style={'text-align': 'center', 'color': '#023047', 'font-family': 'Arial'}),
    html.Label('Select Region:', style={'font-family': 'Arial', 'font-size': '16px'}),
    dcc.Dropdown(
        id='region-dropdown',
        options=[{'label': region, 'value': region} for region in df['region'].unique()],
        value=df['region'].unique().tolist(),  # Select all regions by default
        multi=True,
        className='dash-dropdown',
        style={'font-family': 'Arial', 'font-size': '14px'}
    ),
    html.Label('Select Constituency:', style={'font-family': 'Arial', 'font-size': '16px', 'margin-top': '10px'}),
    dcc.Dropdown(
        id='const-dropdown',
        multi=True,
        className='dash-dropdown',
        style={'font-family': 'Arial', 'font-size': '14px'}
    ),
    dcc.Graph(id='grouped-bar-chart', className='dash-graph', config={'displayModeBar': False})
], style={'padding': '20px', 'font-family': 'Arial', 'backgroundColor': '#f9f9f9'})

@app.callback(
    Output('const-dropdown', 'options'),
    [Input('region-dropdown', 'value')]
)
def set_constituency_options(selected_regions):
    filtered_df = df[df['region'].isin(selected_regions)]
    return [{'label': area, 'value': const} for area, const in zip(filtered_df['area'], filtered_df['const'])]

@app.callback(
    Output('const-dropdown', 'value'),
    [Input('const-dropdown', 'options')]
)
def set_constituency_value(available_options):
    return [option['value'] for option in available_options[:5]]  # Select first 5 constituencies by default

@app.callback(
    Output('grouped-bar-chart', 'figure'),
    [Input('const-dropdown', 'value')]
)
def update_grouped_bar_chart(selected_constituencies):
    filtered_df = df[df['const'].isin(selected_constituencies)]
    melted_df = filtered_df.melt(id_vars=['const', 'area'], 
                                 value_vars=['ConShare', 'LabShare', 'LibDemShare', 'GreenShare', 'ReformShare'],
                                 var_name='Party', value_name='Vote Share')
    
    # Highlight the winning party in each constituency
    filtered_df['Winner'] = filtered_df[['ConShare', 'LabShare', 'LibDemShare', 'GreenShare', 'ReformShare']].idxmax(axis=1)
    melted_df['Winner'] = melted_df.apply(lambda row: 'Yes' if row['Party'] == filtered_df[filtered_df['const'] == row['const']]['Winner'].values[0] else 'No', axis=1)
    
    fig = px.bar(melted_df, x='area', y='Vote Share', color='Party', 
                 title='Vote Shares by Constituency',
                 color_discrete_map=color_discrete_map,
                 labels={'area': 'Constituency', 'Vote Share': 'Vote Share (%)'},
                 barmode='group',
                 hover_data={'Vote Share': ':.2f', 'Winner': False})
    
    # Update layout for better readability and aesthetics
    fig.update_layout(
        title={'x':0.5, 'xanchor': 'center', 'font': {'size': 20, 'family': 'Arial', 'color': '#023047'}},
        font=dict(family='Arial', size=14, color='#023047'),
        plot_bgcolor='#f9f9f9',
        paper_bgcolor='#f9f9f9',
        hovermode='closest',
        xaxis_tickangle=-45,  # Rotate x-axis labels for better readability
        margin=dict(l=40, r=40, t=40, b=40),  # Add some margin for better layout
        legend_title_text='Party',
        legend=dict(font=dict(family='Arial', size=12, color='#023047'))
    )
    
    # Add annotations for the winning party
    for i, row in filtered_df.iterrows():
        winner = row['Winner']
        winner_vote_share = row[winner]
        winner_party = winner.replace('Share', '')
        fig.add_annotation(
            x=row['area'],
            y=winner_vote_share,
            text=f"{winner_party} Wins",
            showarrow=True,
            arrowhead=2,
            ax=-30,
            ay=-30,
            bgcolor="#fff",  # White background for annotation
            opacity=0.7
        )
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
