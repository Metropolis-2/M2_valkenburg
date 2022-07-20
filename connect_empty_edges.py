# %%
import geopandas as gpd
import pandas as pd
import osmnx as ox
from shapely.geometry import  MultiLineString, mapping, shape
from rich import print

# read graphml with osmnx
G = ox.load_graphml('finalized_graph.graphml')
nodes, edges = ox.graph_to_gdfs(G)

# convert crs
edges = edges.to_crs(epsg=32633)
# read geodataframe from gpkg
gdf = gpd.read_file('simple_vienna.gpkg')

# convert to linestring
data = {idx: {'geometry': geom.geoms[0]} for idx, geom in enumerate(gdf.geometry)}

# convert data dictionary to geodataframe
df_single_lines = pd.DataFrame(data).T
gdf_single_lines = gpd.GeoDataFrame(df_single_lines, crs=gdf.crs)


# get some missing edges
edges_new = edges.loc[[(154,164,0),(324,326,0)]]

# add these edges to gdf single lines with pd.concat
gdf_single_lines = pd.concat([gdf_single_lines, edges_new])


# reset the index and only keep the geometry column
gdf_single_lines = gdf_single_lines.reset_index(drop=True)
gdf_single_lines = gdf_single_lines[['geometry']]

# export to geodataframe
gdf_single_lines.to_file('single_lines.gpkg', driver='GPKG')


# %%
