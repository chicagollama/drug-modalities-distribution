import dash
from dash import Dash, html, dcc


app = Dash(__name__, use_pages=True, pages_folder="tmp")

app.layout = html.Div([
    html.H1('Info'),
    html.Div([
        html.Div(
            dcc.Link(f"{page['name']}", href=page["relative_path"])
        ) for page in dash.page_registry.values()
    ]),
    dash.page_container
])


if __name__ == '__main__':
    app.run(port=8051)
    app.run()
