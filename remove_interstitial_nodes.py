# %%
import geopandas as gpd
import pandas as pd
import osmnx as ox
from shapely.geometry import  MultiLineString, mapping, shape
from rich import print
import momepy as mm


# read geodataframe from gpkg
gdf = gpd.read_file('unique_lines.gpkg')

# remove false nodes with mm
gdf = mm.remove_false_nodes(gdf)

gdf = gdf[['geometry']]
gdf = mm.remove_false_nodes(gdf)


# save to gpkg
gdf.to_file('simple_vienna_no_false_nodes.gpkg', driver='GPKG')
