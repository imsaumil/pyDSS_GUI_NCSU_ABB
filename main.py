# Importing required libraries
import dash
from dash import html
import dash_bootstrap_components as dbc
import base64
import os

font_awesome = (
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"
)


# Defining file path
file_path = os.path.dirname(os.path.abspath(__file__))

logo_img = os.path.join(file_path, 'assets', 'sponsor_logo.png')
logo_base64 = base64.b64encode(open(logo_img, 'rb').read()).decode('ascii')

# Starting up the dash app
app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.SPACELAB,
                                                                font_awesome])

# Setting up the navigation bar for multi-page application
navigation_bar = dbc.Nav(
    [
        dbc.NavLink(
            [
                html.Div(page["name"], className="ms-2"),
            ],
            href=page["path"],
            active="exact",
        )
        for page in dash.page_registry.values()
    ],
    vertical=False,
    pills=True,
)

# Defining the app layout
app.layout = dbc.Container([
    html.A(
        dbc.Row([
            dbc.Col(html.H1(children="DISTRIBUTION SYSTEM PROTECTION SIMULATOR",
                            style={'text-align': 'center', 'color': 'navy',
                                   'fontWeight': 'bold', 'fontSize': 35,
                                   'margin-left': '20%'}
                            ), width=10),

            dbc.Col(html.Img(src='data:image/png;base64,{}'.format(logo_base64),
                             style={'align': 'right', 'margin-left': '30%',
                                    'margin-top': '3%'}), width=1),

        ], style={'height': 'auto', 'width': 'auto', 'align-items': 'center', 'text-align': 'left'})
    ),

    dbc.Row([
        dbc.Col([
            navigation_bar
        ], style={'margin-left': '0.5%'})
    ]),

    html.Hr(),

    dbc.Row([
        dbc.Col([
            dash.page_container
        ])
    ]),

], fluid=True)

if __name__ == "__main__":
    app.run(debug=False, port=8070, threaded=True)
