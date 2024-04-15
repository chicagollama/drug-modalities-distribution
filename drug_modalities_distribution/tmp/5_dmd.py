import os
import sys

import dash
from dash import html, dcc
from merged2plot import DMD


# Get the current script's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory by going one level up
parent_dir = os.path.dirname(current_dir)

# Add the parent directory to sys.path
sys.path.append(parent_dir)


# Get figures
dmd = DMD()

dmd.df_info()
fig1 = dmd.common_locations()
fig2, fig3, fig4, fig5 = dmd.clusters()
fig6, fig7 = dmd.mlp()
fig8, fig81 = dmd.reduce_locations()
fig9 = dmd.average_cluster()
figs10 = dmd.average_cluster_vs_modality()
figs11 = dmd.average_cluster_vs_cluster()
adc = dmd.adc_check()

fig_height = '900px'

dash.register_page(__name__)
# dash.register_page(__name__, order=5, path='/dmd/')

layout = html.Div([
    html.H3('DMD info'),
    html.Div([
        dcc.Graph(figure=fig1, responsive=True, style={'height': fig_height}), ]),
    html.P("Some text", style={"width": "40%"}),
    html.Div([
        dcc.Graph(figure=fig2, responsive=True, style={'height': fig_height}), ]),
    html.Div([
        dcc.Graph(figure=fig3, responsive=True, style={'height': fig_height}), ]),
    html.Div([
        dcc.Graph(figure=fig4, responsive=True, style={'height': fig_height}), ]),
    html.Div([
        dcc.Graph(figure=fig5, responsive=True, style={'height': fig_height}), ]),
    html.Div([
        dcc.Graph(figure=fig6, responsive=True, style={'height': fig_height}), ]),
    html.Div([
        dcc.Graph(figure=fig7, responsive=True, style={'height': fig_height}), ]),
    html.Div([
        dcc.Graph(figure=fig8, responsive=True, style={'height': fig_height}), ]),
    html.Div([
        dcc.Graph(figure=fig81, responsive=True, style={'height': fig_height}), ]),
    html.Div([
        dcc.Graph(figure=fig9, responsive=True, style={'height': fig_height}), ]),
    html.Div([
        dcc.Graph(figure=figs10[0], responsive=True, style={'height': fig_height}), ]),
    html.Div([
        dcc.Graph(figure=figs10[1], responsive=True, style={'height': fig_height}), ]),
    html.Div([
        dcc.Graph(figure=figs10[2], responsive=True, style={'height': fig_height}), ]),
    html.Div([
        dcc.Graph(figure=figs11[0], responsive=True, style={'height': fig_height}), ]),
    html.Div([
        dcc.Graph(figure=figs11[1], responsive=True, style={'height': fig_height}), ]),
    html.Div([
        dcc.Graph(figure=figs11[2], responsive=True, style={'height': fig_height}), ]),
    html.Div([
        dcc.Graph(figure=figs11[3], responsive=True, style={'height': fig_height}), ]),
    html.H3('Check for ADC'),
    html.P(adc),
])


