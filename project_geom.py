import geopandas as gpd
import os

# folder to save the data
gis_dir = 'gis_data/'
valken_dir = 'side_vienna'

# vienna center in epsg:3857
x_center = 1821437
y_center = 6141036

# valkenburg
x_val = 491319
y_val = 6830620

# scale
scale_factor =  0.05/8

# rotation
rotation = 0


# offset
offset = (x_val - x_center , y_val - y_center)

################### STREETS

# read gdf
gdf = gpd.read_file('gis_data/simplified_vienna/simple_vienna_no_false_nodes.gpkg')

# convert to epsg:3857
gdf = gdf.to_crs(epsg=3857)

scaled_gdf = gdf.scale(xfact=scale_factor, yfact=scale_factor, zfact=1.0, origin=(x_center, y_center))

# translate to valkenburg
trans_gdf = scaled_gdf.translate(*offset)

# rotate the gdf
rota_gdf = trans_gdf.rotate(angle=rotation)

# save as gpkg
rota_gdf.to_file(os.path.join(gis_dir, valken_dir, 'valk_streets.gpkg'), driver='GPKG')


################### GEOFENCES

# read gdf
gdf = gpd.read_file('gis_data/simplified_vienna/geofences.gpkg', driver='GPKG')

# convert to epsg:3857
gdf = gdf.to_crs(epsg=3857)

scaled_gdf = gdf.scale(xfact=scale_factor, yfact=scale_factor, zfact=1.0, origin=(x_center, y_center))

# translate to valkenburg
trans_gdf = scaled_gdf.translate(*offset)

# rotate the gdf
rota_gdf = trans_gdf.rotate(angle=rotation)

# save as gpkg
rota_gdf.to_file(os.path.join(gis_dir, valken_dir, 'valk_geofences.gpkg'), driver='GPKG')


###################AIRSPACE

# read gdf
gdf = gpd.read_file('gis_data/total_airspace.gpkg')

# convert to epsg:3857
gdf = gdf.to_crs(epsg=3857)

scaled_gdf = gdf.scale(xfact=scale_factor, yfact=scale_factor, zfact=1.0, origin=(x_center, y_center))

# translate to valkenburg
trans_gdf = scaled_gdf.translate(*offset)

# rotate the gdf
rota_gdf = trans_gdf.rotate(angle=rotation)

# save as gpkg
rota_gdf.to_file(os.path.join(gis_dir, valken_dir, 'valk_airspace.gpkg'), driver='GPKG')
