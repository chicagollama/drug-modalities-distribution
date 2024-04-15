import dash
from dash import html


dash.register_page(__name__, path='/', order=1)

layout = html.Div([
    html.H1('Home page'),
    html.Div('Home page'),
])



