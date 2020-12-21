import json
import requests

DGGS_API_URI = "http://ec2-3-26-44-145.ap-southeast-2.compute.amazonaws.com/api/search/"

# geojson_data = {
#         "type": "FeatureCollection",
#         "features": [
#           {
#             "type": "Feature",
#             "geometry": {
#               "type": "Polygon",
#               "coordinates": [
#                 [
#                   [
#                     149.02233123779297,
#                     -35.294111494793285
#                   ],
#                   [
#                     149.14112091064453,
#                     -35.294111494793285
#                   ],
#                   [
#                     149.14112091064453,
#                     -35.21252670530204
#                   ],
#                   [
#                     149.02233123779297,
#                     -35.21252670530204
#                   ],
#                   [
#                     149.02233123779297,
#                     -35.294111494793285
#                   ]
#                 ]
#               ]
#             }
#           }
#         ]
# }


# import ipyleaflet as ipy
# import ipywidgets as ipyw
# from ipyleaflet import GeoJSON, Map, Marker
#
# x_coord = -35.282
# y_coord = 149.09
#
# map1 = ipy.Map(center=[x_coord, y_coord], zoom=9)
# label = ipyw.Label(layout=ipyw.Layout(width='100%'))
#
# geo_json1 = GeoJSON(data=geojson_data, style = {'color': 'red', 'opacity':0.8, 'weight':1.9, 'fillOpacity':0.3})
# map1.add_layer(geo_json1)
# print (map1)


# geo_json = {
#                 "type": "FeatureCollection",
#                 "features": [
#                     {
#                         "type": "Feature",
#                         "geometry": self.geom
#                     }
#                 ]
#             }


geo_json = {
                'type': 'FeatureCollection',
                'features': [
                    {
                        'type': 'Feature',
                        'geometry':
                            '{"type":"LineString",'
                            '"crs":{'
                            '"type":"name",'
                            '"properties":{"name":"EPSG:7844"}},'
                            '"coordinates":[[152.35897127,-25.449602362],[152.35792223,-25.446064373],[152.360708271,-25.435697362],[152.360624391,-25.435396403]]}'}]}


geo_json = {
            'type': 'FeatureCollection',
            'features': [
                {
                    'type': 'Feature',
                    'geometry': '{'
                                '"type":"LineString",'
                                '"crs":{"type":"name","properties":{"name":"EPSG:7844"}},'
                                '"coordinates":[[152.35897127,-25.449602362],[152.35792223,-25.446064373],[152.360708271,-25.435697362],[152.360624391,-25.435396403]]}'}]}


dggs_api_param = {
    'resolution' : 8,
    "dggs_as_polygon" : False
}

# r = requests.post("https://dggs.loci.cat/api/search/find_dggs_by_geojson", params=dggs_api_param, json=geojson_data)
r = requests.post("{}find_dggs_by_geojson".format(DGGS_API_URI), params=dggs_api_param, json=geojson_data)
print(r.status_code)
res = r.json()

print (res)


