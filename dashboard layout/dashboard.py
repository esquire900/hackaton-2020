go#!/usr/bin/env python
# coding: utf-8

# In[1]:


import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import geopandas as gpd
import numpy as np
import pandas as pd


# In[2]:


def format(x):
    if x > 1000000:
        return "€{:.1f}M".format(x / 1000000)
    else:
        return "€{:.1f}K".format(x / 1000)


# In[3]:


df_breda = pd.read_hdf("../data/dashboard-data.v01.hdf", key="key")
fp = "../data/shape/breda_buurten_4326.shp"
map_df = gpd.read_file(fp)
df_breda = gpd.GeoDataFrame(
    df_breda.merge(
        map_df[["BU_NAAM", "perc_groen", "geometry"]],
        left_index=True,
        right_on="BU_NAAM",
        how="outer",
    )
).round(1)
df_breda["premie_huidige_f"] = df_breda["premie_huidige"].apply(format)
df_breda["premie_nog_te_halen_f"] = df_breda["premie_nog_te_halen"].apply(format)
df_breda["id"] = df_breda.index
df_breda.head(2)

# In[4]:


df_breda["premie_huidige"].max()

# In[5]:


# percentage to evi
coefs = [44.0792625, 288.01533161]  # 1d fit for percentage to evi
ffit = np.poly1d(coefs)

# In[6]:


import plotly.express as px

fig = px.choropleth_mapbox(
    data_frame=df_breda,
    geojson=df_breda.geometry.__geo_interface__,
    locations="id",
    color="perc_groen",
    color_continuous_scale="Greens",
    range_color=(25, 100),
    mapbox_style="carto-positron",
    zoom=10,
    center=dict(lat=51.59, lon=4.78),
    opacity=0.5,
    hover_data=["BU_NAAM", "perc_groen"],
    labels=dict(BU_NAAM="Buurtnaam", perc_groen="% groen"),
)
fig.update_layout(margin={"r": 5, "t": 25, "l": 5, "b": 10})
fig.update_layout(
    autosize=False, width=850, height=400,
)
breda = fig

# In[7]:


app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
 app.title = 'Bladboard Breda'

# define styling

# the style arguments for the sidebar
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "55rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "60rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

CARD_STYLE_1 = {}

CARD_STYLE_2 = {}

# In[8]:


# card content temperatuur
card_content_temperatuur = [
    dbc.CardHeader(
        [
            dbc.Row(
                children=[
                    html.Img(src=app.get_asset_url("temperatuur.svg"), height="25px"),
                    html.H5("Hittestress", className="card-title"),
                    dbc.CardLink(
                        "[meer informatie]",
                        href="https://htmlpreview.github.io/?https://github.com/esquire900/hackaton-2020/blob/master/temperatuur/dashboard-export.html",
                        style={"position": "absolute", "right": "20px"},
                    ),
                ]
            )
        ],
        style={"height": "3rem"},
    ),
    dbc.CardBody(
        [
            html.P("Gemiddelde temperatuur afgelopen 20 jaar"),
            html.Div(id="value_temp_init"),
            html.Div(id="kaart_temperatuur", children=[]),
        ]
    ),
]

# card content biodiversiteit
card_content_biodiversiteit = [
    dbc.CardHeader(
        [
            dbc.Row(
                children=[
                    html.Img(src=app.get_asset_url("biodiversiteit.svg"), height="25px"),
                    html.H5("Fauna waarnemingen", className="card-title"),
                    dbc.CardLink(
                        "[meer informatie]",
                        href="https://htmlpreview.github.io/?https://github.com/esquire900/hackaton-2020/blob/master/waarnemingen/dashboard-export.html",
                        style={"position": "absolute", "right": "20px"},
                    ),
                ]
            ),
        ],
        style={"height": "3rem"},
    ),
    dbc.CardBody(
        [
            html.P("Gemiddeld aantal fauna waarnemingen per jaar"),
            html.Div(id="value_bio_init"),
            html.Div(id="kaart_biodiversiteit", children=[]),
        ]
    ),
]

# card content kosten
card_content_kosten = [
    dbc.CardHeader(
        [
            dbc.Row(
                children=[
                    html.Img(src=app.get_asset_url("kosten.svg"), height="25px"),
                    html.H5("Financieel voordeel", className="card-title"),
                    dbc.CardLink(
                        "[meer informatie]",
                        href="https://htmlpreview.github.io/?https://github.com/esquire900/hackaton-2020/blob/master/kosten/kosten-export.html",
                        style={"position": "absolute", "right": "20px"},
                    ),
                ]
            ),
        ],
        style={"height": "3rem"},
    ),
    dbc.CardBody(
        [
            html.Div("Geschat maatschappelijk financieel voordeel op basis van groen subsidie"),
            html.Div(id="value_kosten_init"),
            html.Div(id="kaart_kosten", children=[]),
        ]
    ),
]

# card content groen
card_content_groen = [
    dbc.CardBody(
        [
            html.P(
                "Het planten van groen heeft veel voordelen zoals o.a. verbetering van het leefklimaat (temperatuur), een betere waterhuishouding, ondersteuning van de biodiversiteit en verbetering van de luchtkwaliteit. Daarnaast heeft het ook positieve effecten op oa. gezondheid en welzijn, creëert het een sociale ontmoetingsruimte en biedt het meer ruimte voor beweging. Vergroenen, DOEN!"
            )
        ],
    ),
]

# In[9]:


# --------------------------------------------------------------------------------------------------------------------------
# define dashboard layout
sidebar = html.Div(
    [
        html.H3("Bladboard Breda", className="display-5"),
        html.Hr(),
        dcc.Markdown(
            "Selecteer jouw buurt en pas de slider aan om het effect te zien van vergroening.",
            className="lead",
        ),
        dcc.Dropdown(
            id="buurt_keuze",
            options=[{"label": i, "value": i} for i in df_breda.BU_NAAM.unique()],
            placeholder="Selecteer een buurt",
        ),
        dcc.Graph(id="mapbox_figure", figure=breda, style={"margin-top": "1rem"}),
        dbc.FormGroup(
            [
                dbc.Label("Hoe groen is jouw wijk?", html_for="slider",
                          style={'font-size': '24px', 'font-weight': "900"}),
                dcc.Markdown("Percentage groen (%)"),
                dcc.Slider(
                    id="slider",
                    min=10,
                    max=90,
                    step=1,
                    value=0,
                    tooltip={"style": {"color": "green"}},
                    marks={
                        10: {"label": "10%", "style": {"color": "black"}},
                        20: {"label": "20%", "style": {"color": "grey"}},
                        30: {"label": "30%", "style": {"color": "darkGrey"}},
                        40: {"label": "40%", "style": {"color": "silver"}},
                        50: {"label": "50%", "style": {"color": "lightGreen"}},
                        60: {"label": "60%", "style": {"color": "paleGreen"}},
                        70: {"label": "70%", "style": {"color": "springGreen"}},
                        80: {"label": "80%", "style": {"color": "forestGreen"}},
                        90: {"label": "90%", "style": {"color": "darkgreen"}},
                    },
                    included=False,
                ),
            ]
        ),
    ],
    style=SIDEBAR_STYLE,
)

# -------------------------------------------------------------------------------------------------------------------------#

content = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        card_content_groen,
                        color="success",
                        outline=True,
                        style=CARD_STYLE_2,
                    )
                ),
            ],
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        card_content_temperatuur,
                        color="dark",
                        outline=True,
                        style=CARD_STYLE_2,
                    )
                ),
            ],
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        card_content_biodiversiteit,
                        color="dark",
                        outline=True,
                        style=CARD_STYLE_2,
                    )
                ),
            ],
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        card_content_kosten,
                        color="dark",
                        outline=True,
                        style=CARD_STYLE_2,
                    )
                ),
            ],
            className="mb-4",
        ),
    ],
    style=CONTENT_STYLE,
)

app.layout = html.Div([sidebar, content])


# -------------------------------------------------------------------------------------------------------------------------


# In[10]:


# callback function for map locations & start values
@app.callback(
    [
        dash.dependencies.Output(
            component_id="mapbox_figure", component_property="figure"
        ),
        dash.dependencies.Output(component_id="slider", component_property="value"),
        dash.dependencies.Output(
            component_id="kaart_temperatuur", component_property="children"
        ),
        dash.dependencies.Output(
            component_id="kaart_biodiversiteit", component_property="children"
        ),

        dash.dependencies.Output(
            component_id="kaart_kosten", component_property="children"
        ),

        dash.dependencies.Output(
            component_id="value_temp_init", component_property="children",
        ),

        dash.dependencies.Output(
            component_id="value_bio_init", component_property="children",
        ),

        dash.dependencies.Output(
            component_id="value_kosten_init", component_property="children",
        ),
    ],
    [dash.dependencies.Input(component_id="buurt_keuze", component_property="value")],
)
def update_startvalues(buurtkeuze):
    m_figure = breda.update_layout(
        mapbox_layers=[
            {
                "sourcetype": "geojson",
                "source": df_breda[
                    df_breda.BU_NAAM == buurtkeuze
                    ].geometry.__geo_interface__,
                "type": "line",
                "color": "black",
            }
        ]
    )
    value_slider = df_breda.loc[df_breda.BU_NAAM == buurtkeuze, "perc_groen"].values[0]
    value_temperatuur = dbc.Progress(
        children=str(
            np.round(df_breda.loc[df_breda.BU_NAAM == buurtkeuze, "stemp"].values[0], 1)
        )
                 + "°C",
        value=df_breda.loc[df_breda.BU_NAAM == buurtkeuze, "stemp"].values[0],
        color="success",
        striped=True,
        max=30,
        id="progress_temperatuur",
        style={"height": "30px", "font-size": "20px"}
    )
    temp = df_breda.loc[df_breda.BU_NAAM == buurtkeuze, "stemp"].values[0]
    value_temp_init = html.Div("Huidige temperatuur: {}".format(temp), id="value_temp")

    value_biodiversiteit = dbc.Progress(
        children=str(
            int(
                df_breda.loc[
                    df_breda.BU_NAAM == buurtkeuze, "fauna_observaties"
                ].values[0]
            )
        )
                 + " waarnemingen",
        value=df_breda.loc[df_breda.BU_NAAM == buurtkeuze, "fauna_observaties"].values[
            0
        ],

        color="success",
        striped=True,
        id="progress_biodiversiteit",
        max=3000,
        style={"height": "30px", "font-size": "20px"}
    )

    n_waarnemingen = df_breda.loc[df_breda.BU_NAAM == buurtkeuze, "fauna_observaties"].values[0]

    value_bio_init = html.Div("Huidige waarnemingen: {}".format(n_waarnemingen), id="value_bio", )
    kosten = df_breda.loc[df_breda.BU_NAAM == buurtkeuze, "premie_huidige"].values[0]
    value_kosten = dbc.Progress(
        children=df_breda.loc[
            df_breda.BU_NAAM == buurtkeuze, "premie_huidige_f"
        ].values[0],
        value=kosten,
        color="success",
        striped=True,
        id="progress_kosten",
        max=1,
        style={"height": "30px", "font-size": "20px"}
    )
    value_kosten_init = html.Div(
        "Huidige waarde: €{} k".format(round(kosten / 1000),
                                       id="value_kosten"))

    return m_figure, value_slider, value_temperatuur, value_biodiversiteit, value_kosten, value_temp_init, value_bio_init, value_kosten_init


# In[11]:


# callback function update values according to slider
@app.callback(
    [
        dash.dependencies.Output(
            component_id="progress_temperatuur", component_property="value"
        ),
        dash.dependencies.Output(
            component_id="progress_temperatuur", component_property="children"
        ),
        dash.dependencies.Output(
            component_id="progress_biodiversiteit", component_property="value"
        ),
        dash.dependencies.Output(
            component_id="progress_biodiversiteit", component_property="children"
        ),
        dash.dependencies.Output(component_id='progress_kosten', component_property='value'),
        dash.dependencies.Output(component_id='progress_kosten', component_property='children'),

    ],
    [
        dash.dependencies.Input(component_id="slider", component_property="value"),
        dash.dependencies.Input(component_id="buurt_keuze", component_property="value"),
    ],
)
def update_effects(slider_value, buurtkeuze):
    buurt = df_breda[df_breda.BU_NAAM == buurtkeuze].iloc[0]  # pd.Series
    start_value_slider_evi = ffit(buurt.perc_groen)
    end_value_slider_evi = ffit(slider_value)
    slider_diff = end_value_slider_evi - start_value_slider_evi

    start_temp = buurt.stemp
    start_biodiversiteit = buurt.fauna_observaties
    start_kosten = buurt.premie_huidige

    effect_temp = start_temp + (slider_diff * -0.0012)
    effect_biodiversiteit = start_biodiversiteit + slider_diff * 0.679
    value_kosten = (slider_value) / 100
    string_kosten = "€ {}k".format(
        np.round(((slider_value) / 100) * (buurt.premie_nog_te_halen + buurt.premie_huidige) / 1000, 0)
    )

    value_temperatuur = np.round(effect_temp, 1)
    string_temperatuur = str(np.round(effect_temp, 1)) + "°C"
    value_biodiversiteit = int(effect_biodiversiteit)
    string_biodiversiteit = str(np.round(effect_biodiversiteit, 0)) + " waarnemingen"
    if value_biodiversiteit < 0:
        value_biodiversiteit = 0
        string_biodiversiteit = "0 waarnemingen"

    return (
        value_temperatuur,
        string_temperatuur,
        value_biodiversiteit,
        string_biodiversiteit,
        value_kosten,
        string_kosten
    )


# In[ ]:


# run app
if __name__ == "__main__":
    app.run_server(port=5009)
