# -*- coding: utf-8 -*-

from flask import render_template, Response

import conf
from pyldapi import Renderer, Profile
from rdflib import Graph, URIRef, RDF, Namespace, Literal, BNode
from rdflib.namespace import XSD   #imported for 'export_rdf' function

from .gazetteer import GAZETTEERS, NAME_AUTHORITIES

# for DGGSC:C zone attribution
import json
import requests
import ast
# DGGS_API_URI = "http://ec2-3-26-44-145.ap-southeast-2.compute.amazonaws.com/api/search/"
DGGS_API_URI = "https://dggs.loci.cat/api/search/"
DGGS_uri = 'http://ec2-52-63-73-113.ap-southeast-2.compute.amazonaws.com/AusPIX-DGGS-dataset/ausPIX/'

from rhealpixdggs import dggs
rdggs = dggs.RHEALPixDGGS()

class Roads(Renderer):
    """
    This class represents a placename and methods in this class allow a placename to be loaded from the GA placenames
    database and to be exported in a number of formats including RDF, according to the 'PlaceNames Ontology'

    [[and an expression of the Dublin Core ontology, HTML, XML in the form according to the AS4590 XML schema.]]??
    """

    def __init__(self, request, uri):
        format_list = ['text/html', 'text/turtle', 'application/ld+json', 'application/rdf+xml']
        views = {
            # 'NCGA': Profile(
            #     'http://linked.data.gov.au/def/placenames/',
            #     'Place Names View',
            #     'This is the combined view of places and placenmaes delivered by the Place Names dataset in '
            #     'accordance with the Place Names Profile',
            #     format_list,
            #     'text/html'
            # ),
            'Roads': Profile(
                'http://linked.data.gov.au/def/roads/',
                'Roads View',
                'This view is for roads delivered by the roads dataset'
                ' in accordance with the Roads Profile',
                format_list,
                'text/html'
            )
        }

        super(Roads, self).__init__(request, uri, views, 'Roads')

        self.id = uri.split('/')[-1]

        self.hasName = {
            'uri': 'http://linked.data.gov.au/def/roads/',
            'label': 'Roads:',
            'comment': 'The Entity has a name (label) which is a text sting.',
            'value': None
        }

        # self.thisLine = {
        #     'label': None,
        #     'uri': None
        # }

        self.functional_class = None,
        self.surface = None
        self.custodian_agency = None
        self.state_route_number = None
        self.road_direction = None
        self.speedlimit = None
        self.operational_status = None
        self.trafficability = None
        self.national_route_number = None

        self.thisLine = []
        self.lineCords = []

        self.register = {
            'label': None,
            'uri': None
        }

        self.authority = {
            'label': None,
            'web': None
        }
        self.email = None

        self.modifiedDate = None

        self.hasPronunciation = None   # None == don't display
        # pronunciation will only be displyed on webpage if it exists

        q = '''
            SELECT 
              	"name",
                "uri",
                "functional_class",
                "surface",
                "custodian_agency",
                "state_route_number",
                "road_direction",
                "speedlimit",
                "operational_status",
                "trafficability",
                "national_route_number",
                "featuresubtype", 
                "feature_date",
                "feature_source",
                "attribute_date",
                "attribute_source",
                "vertical_accuracy",
                "planimetric_accuracy",
                "source_ufi",
                "source_jurisdiction",                
                "custodian_licensing",
                "loading_date",
                "shape_length",
                "road_type",
                "road_suffix",
                "ground_relationship",
                "number_of_lanes",
                "seasonality",
                "alternative_name",
                "divided",
                "authority",
                "useraccess",
                ST_AsGeoJSON(geom) As geom
            FROM "transportroads"
            WHERE "id" = '{}'
        '''.format(self.id)

        for road in conf.db_select(q):
            self.hasName['value'] = str(road[0])
            self.uri = road[1]

            self.functional_class = road[2],
            self.surface = road[3]
            self.custodian_agency = road[4]
            self.state_route_number = road[5]
            self.road_direction = road[6]
            self.speedlimit = road[7]
            self.operational_status = road[8]
            self.trafficability = road[9]
            self.national_route_number = road[10]

            # self.authority['label'] = (NAME_AUTHORITIES[str(road[-3])]['label'])
            # self.authority['web'] = (NAME_AUTHORITIES[str(road[-3])]['web'])
            # self.email = (NAME_AUTHORITIES[str(road[-3])]['email'])
            #
            # self.register['uri'] = (GAZETTEERS[str(road[-3])]['uri_id'])
            # self.register['label'] = (GAZETTEERS[str(road[-3])]['label'])

            # get geometry from database
            self.geom = ast.literal_eval(road[-1])
            self.lineCords = self.geom['coordinates']

            # using the web API to find the DGGS cells for the geojson
            dggs_api_param = {
                'resolution': 9,
                "dggs_as_polygon": False
            }

            geo_json = {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": self.geom
                    }
                ]
            }

            res = requests.post('{}find_dggs_by_geojson'.format(DGGS_API_URI), params=dggs_api_param, json=geo_json)
            self.listOfCells = res.json()['dggs_cells']

            for cell in self.listOfCells:
                self.thisLine.append({'label': str(cell),
                                      'uri': '{}{}'.format(DGGS_uri, str(cell))})


    def render(self):
        if self.profile == 'alt':
            return self._render_alt_profile()  # this function is in Renderer
        elif self.mediatype in ['text/turtle', 'application/ld+json', 'application/rdf+xml']:
            return self.export_rdf(self.profile)
        else:  # default is HTML response: self.format == 'text/html':
            return self.export_html(self.profile)


    def export_html(self, model_view='Roads'):
        html_page = 'roads.html'
        return Response(        # Response is a Flask class imported at the top of this script
            render_template(     # render_template is also a Flask module
                html_page,   # uses the html template to send all this data to it.
                id=self.id,
                hasName=self.hasName,
                coordinate_list=self.lineCords,
                functional_class=self.functional_class,
                surface=self.surface,
                custodian_agency=self.custodian_agency,
                state_route_number=self.state_route_number,
                road_direction=self.road_direction,
                speedlimit=self.speedlimit,
                operational_status=self.operational_status,
                trafficability=self.trafficability,
                national_route_number=self.national_route_number,

                # authority=self.authority,
                # authority_email = self.email,
                # register=self.register,
                # hasNameFormality=self.hasNameFormality,
                # supplyDate=self.supplyDate,
                # longitude = self.x,
                # latitude = self.y,
                ausPIX_DGGS = self.thisLine
            ),
            status=200,
            mimetype='text/html'
        )

    def _generate_wkt(self):
        if self.id is not None and self.x is not None and self.y is not None:
            return 'POINT({} {})'.format(self.y, self.x)
        else:
            return ''

    def _generate_dggs(self):
        if self.id is not None and self.thisCell is not None:
            return '{}'.format(self.thisCell)
        else:
            return ''


    def export_rdf(self, model_view='NCGA'):
        g = Graph()  # make instance of a RDF graph

        # namespace declarations
        dcterms = Namespace('http://purl.org/dc/terms/')  # already imported
        g.bind('dcterms', dcterms)
        geo = Namespace('http://www.opengis.net/ont/geosparql#')
        g.bind('geo', geo)
        owl = Namespace('http://www.w3.org/2002/07/owl#')
        g.bind('owl', owl)
        rdfs = Namespace('http://www.w3.org/2000/01/rdf-schema#')
        g.bind('rdfs', rdfs)

        # specific to placename datasdet
        place = Namespace('http://linked.data.gov.au/dataset/placenames/place/')
        g.bind('place', place)
        pname = URIRef('http://linked.data.gov.au/dataset/placenames/placenames/')
        g.bind('pname', pname)
        # made the cell ID the subject of the triples
        auspix = URIRef('http://ec2-52-63-73-113.ap-southeast-2.compute.amazonaws.com/AusPIX-DGGS-dataset/')
        g.bind('auspix', auspix)
        pn = Namespace('http://linked.data.gov.au/def/placenames/')
        g.bind('pno', pn)

        geox = Namespace('http://linked.data.gov.au/def/geox#')
        g.bind('geox', geox)
        g.bind('xsd', XSD)
        sf = Namespace('http://www.opengis.net/ont/sf#')
        g.bind('sf', sf)
        ptype = Namespace('http://pid.geoscience.gov.au/def/voc/ga/PlaceType/')
        g.bind('ptype', ptype)

        # build the graphs
        official_placename = URIRef('{}{}'.format(pname, self.id))
        this_place = URIRef('{}{}'.format(place, self.id))
        g.add((official_placename, RDF.type, URIRef(pn + 'OfficialPlaceName')))
        g.add((official_placename, dcterms.identifier, Literal(self.id, datatype=pn.ID_GAZ)))
        g.add((official_placename, dcterms.identifier, Literal(self.auth_id, datatype=pn.ID_AUTH)))
        g.add((official_placename, dcterms.issued, Literal(str(self.supplyDate), datatype=XSD.dateTime)))
        g.add((official_placename, pn.name, Literal(self.hasName['value'], lang='en-AU')))
        g.add((official_placename, pn.placeNameOf, this_place))
        g.add((official_placename, pn.wasNamedBy, URIRef(self.authority['web'])))
        g.add((official_placename, rdfs.label, Literal(self.hasName['value'])))

        # if NCGA view, add the place info as well
        if model_view == 'NCGA':
            g.add((this_place, RDF.type, URIRef(pn + 'Place')))
            g.add((this_place, dcterms.identifier, Literal(self.id, datatype=pn.ID_GAZ)))
            g.add((this_place, dcterms.identifier, Literal(self.auth_id, datatype=pn.ID_AUTH)))

            place_point = BNode()
            g.add((place_point, RDF.type, URIRef(sf + 'Point')))
            g.add((place_point, geo.asWKT, Literal(self._generate_wkt(), datatype=geo.wktLiteral)))
            g.add((this_place, geo.hasGeometry, place_point))

            place_dggs = BNode()
            g.add((place_dggs, RDF.type, URIRef(geo + 'Geometry')))
            g.add((place_dggs, geox.asDGGS, Literal(self._generate_dggs(), datatype=geox.dggsLiteral)))
            g.add((this_place, geo.hasGeometry, place_dggs))

            g.add((this_place, pn.hasPlaceClassification, URIRef(ptype + self.featureType['label'])))
            g.add((this_place, pn.hasPlaceClassification, URIRef(ptype + self.hasCategory['label'])))
            g.add((this_place, pn.hasPlaceClassification, URIRef(ptype + self.hasGroup['label'])))
            g.add((this_place, pn.hasPlaceName, official_placename))

        if self.mediatype == 'text/turtle':
            return Response(
                g.serialize(format='turtle'),
                mimetype = 'text/turtle'
            )
        elif self.mediatype == 'application/rdf+xml':
            return Response(
                g.serialize(format='application/rdf+xml'),
                mimetype = 'application/rdf+xml'
            )
        else: # JSON-LD
            return Response(
                g.serialize(format='json-ld'),
                mimetype = 'application/ld+json'
            )


if __name__ == '__main__':
    pass




