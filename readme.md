# Generate a simplified vienna

The first step of this repo was to create a simplified geometry of Vienna with less streets inside qgis.

1) Manually deleted some streets in QGIS and save them in **gis_data/simplified_vienna/simple_vienna.gpkg**
2) Observe for some missing edges and manually connect them with ```connect_empty_edges.py``` and save in **gis_data/simplified_vienna/single_lines.gpkg**
3) Inside QGIS run algorithm to ensure that ```single_lines.gpkg``` is split at all intersections and save in **gis_data/simplified_vienna/unique_lines.gpkg**
4) Run ```remove_interstitital_nodes.py``` to merge degree-one edges and save as **gis_data/simplified_vienna/simple_vienna_no_false_nodes.gpkg**
5) TODO: remove edges with degree one nodes
6) ```simple_vienna_no_false_nodes``` is now ready to be translated, scaled, and rotated.

# Project geometry

Projection can happen with any prepared geometry. This can either by with the original M2 edge data ```finalized_graph``` or with ```simple_vienna_no_false_nodes``` and any other geometry. The requirements are that the edges must be supplied as in the section above.

The steps to project the geometry are

1) Choose a reference point in the center of vienna (total airspace centroid).
2) Choose a scaling reference length. This is the radius of total airspace.
3) Run ```project_geom.py``` on prepared geometry and other references to move things to Valkenburg.
4) Run ```create_osmnx_graph.py``` on projected geometry so that it is possible to run path planning on it.

# Create a sceario
With the last step it is now a classic graph so we can create a BlueSky scenario.