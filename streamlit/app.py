import streamlit as st
import pandas as pd
import geopandas as gpd
import numpy as np

# percentage to evi
coefs = [44.0792625, 288.01533161] # 1d fit for percentage to evi
ffit = np.poly1d(coefs)

# read shapefile
gdf = gpd.read_file('data/gdf.geojson')
gdf.perc_groen = gdf.perc_groen.astype(int)

# titles and header
st.title('Groen, groener, groenst!')
st.subheader('Groen in de Breda')
st.markdown('Het planten van bomen, vaste planten, bloembollen en andere vormen van groen heeft veel\nvoordelen zoals o.a. verbetering van het leefklimaat (temperatuur), een betere\nwaterhuishouding, ondersteuning van de biodiversiteit en verbetering van de \nluchtkwaliteit, en daarnaast ook positieve effecten heeft op gezondheid en welzijn, en \neen sociale ontmoetingsruimte creëert en ruimte voor beweging biedt.')
st.sidebar.title('Pas het groen in jouw buurt aan!')

# buurt selector
buurt = st.sidebar.selectbox('selecteer buurt', options=gdf.BU_NAAM)
buurt_data = gdf[gdf.BU_NAAM == buurt]

# green slider
green = st.sidebar.slider('verander het percentage groen', 10, 90, value=int(buurt_data.iloc[0].loc['perc_groen']))
temp = pd.DataFrame([ffit(green) * -0.0012 + 3], index=['Temperatuur'])
biod = pd.DataFrame([green / 20], index=['# Biodiversiteit'])
st.sidebar.header('en zie wat er gebeurt... \n\n')

# map
from streamlit_folium import folium_static
import folium

# center on mean of gdf
m = folium.Map(location=[51.59, 4.77], zoom_start=12)
# add choropleths
choropleth = folium.Choropleth(gdf, data=gdf, 
                    key_on='feature.properties.BU_NAAM',
                    columns=['BU_NAAM', 'perc_groen'], 
                    bins=[10,20,30,40,50,60,70,80,90],
                    fill_color='YlGn',
                    fill_opacity=0.7,
                    line_opacity=0.2,
                    legend_name='% groen',
                    highlight=True).add_to(m)
choropleth.geojson.add_child(
    folium.features.GeoJsonTooltip(['BU_NAAM', 'perc_groen'], aliases=['buurtnaam:', 'percentage groen:'])
)


# call to render Folium map in Streamlit
folium_static(m)
st.markdown('/* huidig percentage groen per wijk op basis van [Groenkaart RIVM](https://data.overheid.nl/dataset/6607-groenkaart-van-nederland)')

def hbar(df, xaxistitle, range_x, color):
    import plotly.express as px
    margindict = dict(l=0, r=0, t=0, b=0)
    height = 100
    fig = px.bar(df, orientation="h", range_x=range_x, color_discrete_sequence=[color])
    fig.update_layout(margin=margindict, height=height, width=300, xaxis=dict(title=xaxistitle, showgrid=False), yaxis=dict(visible=False, showgrid=False), plot_bgcolor='white', paper_bgcolor='white', showlegend=False) 
    return st.sidebar.plotly_chart(fig)


st.sidebar.markdown('verschil in [temperatuur](https://htmlpreview.github.io/?https://github.com/thomas-wsbd/streamlit-hackaton-2020/blob/master/html/dashboard-export-temp.html)')
hbar(temp, 'Temperatuur \u00b0C', range_x=[-2,2], color='darksalmon')
st.sidebar.markdown('[biodiversiteit](https://htmlpreview.github.io/?https://github.com/thomas-wsbd/streamlit-hackaton-2020/blob/master/html/dashboard-export-obs.html) op schaal; 1 (vrijwel geen) tot 5 (groot)')
hbar(biod, 'Biodiversiteit (1-5)', range_x=[1, 5], color='navy')