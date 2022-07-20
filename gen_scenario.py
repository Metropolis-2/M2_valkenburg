"""
Code contains functions that are used to generate a path only
through constrained airspace. It also gives information
about turn speeds, bools, coordinates based on angles.

There are two important functions in this file:
    1. get_lat_lon_from_osm_route()
    2. get_turn_arrays()

The other functions are helper and test functions for the two important functions.

Code written by: Andres Morfin Veytia
Project: Metropolis 2
"""
from os import path
import osmnx as ox
import geopandas as gpd
import numpy as np
from shapely.geometry import LineString



def main():
    """
    Main function for the module.
    """
    from os import path
    from matplotlib import pyplot as plt

    # import common elements graph
    graph_path = path.join(
        path.dirname(__file__),
        'gis_data',
        'cute_vienna',
        "valk_graph.graphml",
    )
    G = ox.load_graphml(graph_path)

    # convert to undirected graph
    G_undirected = ox.get_undirected(G)

    orig = 37
    dest = 28
    route = ox.shortest_path(G_undirected, orig, dest)

    # get lat and lon from route and turninfo
    lats, lons, _ = get_lat_lon_from_osm_route(G_undirected, route)
    turn_bool, *_ = get_turn_arrays(lats, lons)

    # get initial bearing
    qdr = qdrdist(lats[0], lons[0], lats[1], lons[1])
    
    acidx = '3'

    # generate the scenario text and path
    scenario_lines, scenario_path = create_scenario_text(
        acidx, lats, lons, turn_bool
    )

    with open(scenario_path, "w") as f:
        for line in scenario_lines:
            f.write(f"{line}\n")


def get_lat_lon_from_osm_route(G, route):
    """
    Get lat and lon from an osmnx route (list of nodes) and nx.MultGraph.
    The function returns two numpy arrays with the lat and lon of route.
    Also return a GeoDataFrame with the lat and lon of the route as a
    linestring.

    Parameters
    ----------
    G : nx.MultiGraph
        Graph to get lat and lon from. Graph should be built
        with osmnx.get_undirected.

    route : list
        List of nodes to build edge and to get lat lon from

    Returns
    -------
    lat : numpy.ndarray
        Array with latitudes of route

    lon : numpy.ndarray
        Array with longitudes of route

    route_gdf : geopandas.GeoDataFrame
        GeoDataFrame with lat and lon of route as a linestring.
    """
    # add first node to route
    lons = np.array(G.nodes[route[0]]["x"])
    lats = np.array(G.nodes[route[0]]["y"])

    # loop through the rest for loop only adds from second point of edge
    for u, v in zip(route[:-1], route[1:]):
        # if there are parallel edges, select the shortest in length
        data = list(G.get_edge_data(u, v).values())[0]

        # extract coords from linestring
        xs, ys = data["geometry"].xy

        # Check if geometry of edge is in correct order
        if G.nodes[u]["x"] != data["geometry"].coords[0][0]:

            # flip if in wrong order
            xs = xs[::-1]
            ys = ys[::-1]

        # only add from the second point of linestring
        lons = np.append(lons, xs[1:])
        lats = np.append(lats, ys[1:])

    # make a linestring from the coords
    linestring = LineString(zip(lons, lats))

    # make into a gdf
    line_gdf = gpd.GeoDataFrame(geometry=[linestring], crs="epsg:4326")

    return lats, lons, line_gdf


def get_turn_arrays(lats, lons, cutoff_angle=25):
    """
    Get turn arrays from latitude and longitude arrays.
    The function returns three arrays with the turn boolean, turn speed and turn coordinates.

    Turn speed depends on the turn angle.

        - Speed set to 0 for no turns.
        - Speed is 10 knots for angles between 25 and 100 degrees.
        - Speed is 5 knots for angles between 100 and 150 degrees.
        - Speed is 2 knots for angles larger than 150 degrees.

    Parameters
    ----------
    lat : numpy.ndarray
        Array with latitudes of route

    lon : numpy.ndarray
        Array with longitudes of route

    cutoff_angle : int
        Cutoff angle for turning. Default is 25.

    Returns
    -------
    turn_bool : numpy.ndarray
        Array with boolean values for turns.

    turn_speed : numpy.ndarray
        Array with turn speed. If no turn, speed is 0.

    turn_coords : numpy.ndarray
        Array with turn coordinates. If no turn then it has (-9999.9, -9999.9)

    """

    # Define empty arrays that are same size as lat and lon
    turn_speed = np.zeros(len(lats))
    turn_bool = np.array([False] * len(lats), dtype=np.bool8)
    turn_coords = np.array([(-9999.9, -9999.9)] * len(lats), dtype="f,f")

    # Initialize variables for the loop
    lat_prev = lats[0]
    lon_prev = lons[0]

    # loop thru the points to calculate turn angles
    for i in range(1, len(lats) - 1):
        # reset some values for the loop
        lat_cur = lats[i]
        lon_cur = lons[i]
        lat_next = lats[i + 1]
        lon_next = lons[i + 1]

        # calculate angle between points
        d1 = qdrdist(lat_prev, lon_prev, lat_cur, lon_cur)
        d2 = qdrdist(lat_cur, lon_cur, lat_next, lon_next)

        # fix angles that are larger than 180 degrees
        angle = abs(d2 - d1)
        angle = 360 - angle if angle > 180 else angle

        # give the turn speeds based on the angle
        if angle > cutoff_angle and i != 0:

            # set turn bool to true and get the turn coordinates
            turn_bool[i] = True
            turn_coords[i] = (lat_cur, lon_cur)

            # calculate the turn speed based on the angle.
            if angle < 100:
                turn_speed[i] = 10
            elif angle < 150:
                turn_speed[i] = 5
            else:
                turn_speed[i] = 2
        else:
            turn_coords[i] = (-9999.9, -9999.9)

        # update the previous values at the end of the loop
        lat_prev = lat_cur
        lon_prev = lon_cur

    # make first entry to turn bool true (entering constrained airspace)
    turn_bool[0] = True

    return turn_bool, turn_speed, turn_coords


def create_scenario_text(acidx, lats, lons, turn_bool):
    """
    Creates the scenario text and file path for a given aircraft.

    Parameters
    ----------
    acidx : int
        The aircraft index.
    lats : numpy.ndarray
        The latitudes of the path.
    lons : numpy.ndarray
        The longitudes of the path.
    cruise_alts : numpy.ndarray
        The possible cruise altitudes of the path.
    cruise_alt_changes : numpy.ndarray
        A boolean array indicating whether the
        cruise altitude changes at a given waypoint.
    turn_bool : numpy.ndarray
        A boolean array indicating whether the
        aircraft turns at a given waypoint.

    Returns
    -------
    scenario_lines : list
        The scenario text. Each item is a line in the scenario.
    scenario_path : str
        The file path to the scenario file scenarios/R{acidx}.scn.
    """

    # set cruise altitudes
    cruise_alts = np.array([30, 60, 90])

    # bearing of the first segment
    achdg = qdrdist(lats[0], lons[0], lats[1], lons[1])

    # start a list of strings
    scenario_lines = []

    alt = np.random.choice(cruise_alts)

    # first lines
    scenario_lines.append("00:00:00>CASMACHTHR 0")
    scenario_lines.append("00:00:00>VIS TRAFFIC PROJTRAFFIC")
    scenario_lines.append("00:00:00>setrefpoint 491733,6830838")
    scenario_lines.append("00:00:00>setreflength 0.3")
    scenario_lines.append(
        f"00:00:00>CRE R{acidx} M600 {lats[0]} {lons[0]} {achdg} {alt} 5"
    )

    # Create the add waypoints command
    addwypoint_lines = [f"00:00:00>ADDWAYPOINTS R{acidx}"]
    # add the rest of the lines as waypoints
    for i in range(1, len(lats)):
        # if turn_bool[i] or cruise_alt_changes[i]:
        if turn_bool[i]:
            addwypoint_lines.append(f"{lats[i]} {lons[i]},{alt},3,TURNSPD,1")
        else:
            addwypoint_lines.append(f"{lats[i]} {lons[i]},{alt},3,FLYBY, 0")

    # add the last waypoint twice
    # addwypoint_lines.append(f"{lats[-1]} {lons[-1]},{alt},3,FLYBY, 0")

    # join into one string
    scenario_lines.append(",".join(addwypoint_lines))

    # turn vnav and lnav on
    scenario_lines.append(f"00:00:00>LNAV R{acidx} ON")
    scenario_lines.append(f"00:00:00>VNAV R{acidx} ON")

    # # add the last line to delete the aircraft
    # scenario_lines.append(
    #     f"00:00:00>R{acidx} ATDIST {lats[-1]} {lons[-1]} 0.01 DEL R{acidx}"
    # )

    scenario_lines.append(
        f"00:00:00>PAN R{acidx}"
    )
    scenario_lines.append(
        f"00:00:00>ZOOM 300"
    )
    # write the scenario to a file
    scenario_path = path.join(path.dirname(__file__), f"scenarios/R{acidx}.scn")

    return scenario_lines, scenario_path

"""HELPER FUNCTIONS BELOW"""




def qdrdist(latd1, lond1, latd2, lond2):
    """Calculate bearing, using WGS'84
    In:
        latd1,lond1 en latd2, lond2 [deg] :positions 1 & 2
    Out:
        qdr [deg] = heading from 1 to 2

    Function is from bluesky (geo.py)
    """

    # Convert to radians
    lat1 = np.radians(latd1)
    lon1 = np.radians(lond1)
    lat2 = np.radians(latd2)
    lon2 = np.radians(lond2)

    # Bearing from Ref. http://www.movable-type.co.uk/scripts/latlong.html
    coslat1 = np.cos(lat1)
    coslat2 = np.cos(lat2)

    qdr = np.degrees(
        np.arctan2(
            np.sin(lon2 - lon1) * coslat2,
            coslat1 * np.sin(lat2) - np.sin(lat1) * coslat2 * np.cos(lon2 - lon1),
        )
    )

    return qdr


def rwgs84(latd):
    """Calculate the earths radius with WGS'84 geoid definition
    In:  lat [deg] (latitude)
    Out: R   [m]   (earth radius)

    Function is from bluesky (geo.py)
    """
    lat = np.radians(latd)
    a = 6378137.0  # [m] Major semi-axis WGS-84
    b = 6356752.314245  # [m] Minor semi-axis WGS-84
    coslat = np.cos(lat)
    sinlat = np.sin(lat)

    an = a * a * coslat
    bn = b * b * sinlat
    ad = a * coslat
    bd = b * sinlat

    # Calculate radius in meters
    r = np.sqrt((an * an + bn * bn) / (ad * ad + bd * bd))

    return r

if __name__ == "__main__":
    main()
