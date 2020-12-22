from flask import Blueprint, request, Response, render_template
from model.roads import Roads
from pyldapi import ContainerRenderer
import conf
import ast
import folium
print(__name__)
routes = Blueprint('controller', __name__)

DEFAULT_ITEMS_PER_PAGE=50

@routes.route('/', strict_slashes=True)
def home():
    return render_template('home.html')


@routes.route('/rds/')
def roads():
    # Search specific items using keywords
    search_string = request.values.get('search')

    try:

        # get the register length from the online DB
        sql = 'SELECT COUNT(*) FROM "transportroads"'
        if search_string:
            sql += '''WHERE UPPER(cast("id" as text)) LIKE '%{search_string}%' OR UPPER("name") LIKE '%{search_string}%';
                   '''.format(search_string=search_string.strip().upper())

        no_of_items = conf.db_select(sql)[0][0]

        page = int(request.values.get('page')) if request.values.get('page') is not None else 1
        per_page = int(request.values.get('per_page')) \
                   if request.values.get('per_page') is not None else DEFAULT_ITEMS_PER_PAGE
        offset = (page - 1) * per_page

        # get the id and name for each record in the database
        sql = '''SELECT "id", "name" FROM "transportroads"'''
        if search_string:
            sql += '''WHERE UPPER(cast("id" as text)) LIKE '%{search_string}%' OR UPPER("name") LIKE '%{search_string}%'
                   '''.format(search_string=search_string.strip().upper())
        sql += '''ORDER BY "name"
                OFFSET {} LIMIT {}'''.format(offset, per_page)

        items = []
        for item in conf.db_select(sql):
            items.append(
                (item[0], item[1])
            )
    except Exception as e:
        print(e)
        return Response('The Roads database is offline', mimetype='text/plain', status=500)

    return ContainerRenderer(request=request,
                            instance_uri=request.url,
                            label='Roads Register',
                            comment='A register of Roads',
                            parent_container_uri='http://linked.data.gov.au/def/placenames/PlaceName',
                            parent_container_label='QLD_Roads',
                            members=items,
                            members_total_count=no_of_items,
                            profiles=None,
                            default_profile_token=None,
                            super_register=None,
                            page_size_max=1000,
                            register_template=None,
                            per_page=per_page,
                            search_query=search_string,
                            search_enabled=True
                            ).render()


@routes.route('/map')
def show_map():
    '''
    Function to render a map around the specified line
    '''

    name = request.values.get('name')
    coords_list = ast.literal_eval(request.values.get('coords'))[0]

    # swap x & y for mapping
    points = []
    for coords in coords_list:
        points.append(tuple([coords[1], coords[0]]))

    ave_lat = sum(p[0] for p in points) / len(points)
    ave_lon = sum(p[1] for p in points) / len(points)

    # create a new map object
    folium_map = folium.Map(location=[ave_lat, ave_lon], zoom_start=15)
    tooltip = 'Click for more information'

    folium.PolyLine(points, color="red", weight=2.5, opacity=1, popup = name, tooltip=tooltip).add_to(folium_map)

    return folium_map.get_root().render()


@routes.route('/rds/<string:roads_id>')
def road(roads_id):
    roads = Roads(request, request.base_url)
    return roads.render()

