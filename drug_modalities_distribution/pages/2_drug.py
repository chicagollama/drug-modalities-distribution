import os
import sys

import dash
from dash import html, dcc
from discover_drug import get_info


# Get the current script's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory by going one level up
parent_dir = os.path.dirname(current_dir)

# Add the parent directory to sys.path
sys.path.append(parent_dir)


fig1, fig2 = get_info()
fig_height = '900px'

dash.register_page(__name__, order=2)

layout = html.Div([
    html.H3('Drug info'),
    html.Div([
        dcc.Graph(figure=fig1, responsive=True, style={'height': fig_height}),
    ]),
    html.Div([
        dcc.Graph(figure=fig2, responsive=True, style={'height': fig_height,
                                                       # 'width': '1200px'
                                                       }),
    ]),
])


