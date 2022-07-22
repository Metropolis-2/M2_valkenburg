# %%
import geopandas as gpd
import osmnx as ox
import momepy as mm

gdf = gpd.read_file('gis_data/cute_vienna/valk_graph_simplified.gpkg')

# %%
G = mm.gdf_to_nx(gdf)

points, lines = mm.nx_to_gdf(G)

# set the key of lines as (u, v, key)
lines['u'] = lines['node_start']
lines['v'] = lines['node_end']
lines['key'] = 0
lines = lines.set_index(['u', 'v', 'key'])


# convert to epsg:4326
points = points.to_crs(epsg=4326)
lines = lines.to_crs(epsg=4326)

# give points an x,y column
points['x'] = points['geometry'].apply(lambda x: x.x)
points['y'] = points['geometry'].apply(lambda x: x.y)

# convert to osmnx graph
G = ox.graph_from_gdfs(points, lines)

# add lengths
G = ox.distance.add_edge_lengths(G)

# save graphml
ox.save_graphml(G, 'gis_data/cute_vienna/valk_graph.graphml')

# save gpkg
ox.save_graph_geopackage(G, 'gis_data/cute_vienna/valk_graph.gpkg')




# %%
