import dash
from dash import Dash, html, dcc
import flask
import os
# import config


# export PYTHONPATH=/Users/mariialomovskaia/PycharmProjects/EMBL/drug-modalities-distribution:$PYTHONPATH


# server = flask.Flask(__name__)

app = Dash(__name__, use_pages=True)
# app = Dash(__name__, use_pages=True, pages_folder=os.path.join(, "pages"))

# print(dash.page_container)
# print(dash.page_registry.values())

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
    app.run()
    # app.run(debug=True)
