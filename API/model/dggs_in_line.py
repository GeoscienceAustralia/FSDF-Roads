import math
from rhealpixdggs import dggs
rdggs = dggs.RHEALPixDGGS()

from shapely.geometry import shape, LineString, MultiLineString
from geojson.utils import coords

'''
def line_to_DGGS(myLineObj, resolution):  # one poly and the attribute record for it
    """
    Takes a line and a resolution and returns a list of DGGS cells objects.
    myLineObj is expected to be a shapely MultiLineString or LineString object.    
    """
    doneDGGScells = [] #to accumlate a list of completed cells
    arrLines = []
    if(isinstance(myLineObj, MultiLineString)):        
        arrLines = list(myLineObj)
    else: #assume this is a LineString object
        arrLines.append(myLineObj)
    #iterate through list of LineStrings    
    for currLine in arrLines:
        for pt in currLine.coords:  # for each point calculate the DGGS by calling on the DGGS engine
            # ask the engine what cell thisPoint is in
            thisDGGS = rdggs.cell_from_point(resolution, pt, plane=False)# plane=false therefore on the ellipsoid curve
            #add cell if not already in there
            if thisDGGS not in doneDGGScells: # == new one
                doneDGGScells.append(thisDGGS) # save as a done cell
    return doneDGGScells
'''


'''
developed by Joseph Bell at Geoscience Australia June 2020
'''
def densify_my_line(line_to_densify, resolution):
    '''
    densify a line based on the resolution of the cells
    designed to return a continuous string of ajoining DGGS cells along a line feature
    '''

    resArea = (rdggs.cell_area(resolution, plane=False))  # ask engine for area of cell
    # math to define a suitable distance between vertices - ensures good representation of the line - a continuous run of cells to define the line
    min_dist = math.sqrt(float(resArea))/300000  # width of cell changes with sqrt of the area - 300000 is a constant that can be changed but will change output


    for line_points in line_to_densify:  # this is the outer [] for multi-line object

        edgeData = []  # we are going to make a list of edges based on pairs of vertices
        previous = (0, 0)  # placeholder for previous point
        for vertex in line_points:
            #print(vertex)
            if previous != (0, 0):  # not the beginning
                newEdge = (previous, vertex)
                #print('new edge', newEdge)
                edgeData.append(newEdge)
                previous = vertex  # remember for the next iteration
            else:
                previous = vertex
        # now calculate the length of segment
        new_line = []
        for edge in edgeData:
            dx = edge[1][0] - edge[0][0]
            dy = edge[1][1] - edge[0][1]
            #print('dxdy', dx, dy)
            line_length = math.sqrt((dx*dx) + (dy*dy))  # length in degrees
            segments = round(line_length / min_dist)  # figure number of segments needed
            if segments == 0:  # cannot be 0
                segments = 1  # chage zero to to one
            densified_line = (split([edge[1][0], edge[1][1]], [edge[0][0], edge[0][1]], segments))  #using split function below

            new_line.append(densified_line)  # add this segment into the output line
    return new_line  # we return this line in the datset with extra points along it (densified)


def split(start, end, segments):
    '''
   add vertices to a line to densify
   must decide on how many segments you need using the densify_my_line function above
   usually called from the densify_my_line function
    '''
    x_delta = (end[0] - start[0]) / float(segments)
    y_delta = (end[1] - start[1]) / float(segments)
    points = []
    for i in range(1, segments):
        points.append([start[0] + i * x_delta, start[1] + i * y_delta])
    return [start] + points + [end]


def line_to_DGGS(line_coords, resolution):  # one poly and the attribute record for it
    """
    Takes a list of line coords and a resolution and returns a list of DGGS cells objects.
    """
    doneDGGScells = [] #to accumlate a list of completed cells
    arrLines = []
    for pt in line_coords:  # for each point calculate the DGGS by calling on the DGGS engine
        # ask the engine what cell thisPoint is in
        thisDGGS = rdggs.cell_from_point(resolution, pt, plane=False)# plane=false therefore on the ellipsoid curve
        #add cell if not already in there
        if thisDGGS not in doneDGGScells: # == new one
            doneDGGScells.append(thisDGGS) # save as a done cell
    return doneDGGScells


def get_cells_in_feature(fea, resolution, return_cell_obj=False):
    geom = shape((fea['geometry']))
    cells = []
    if isinstance(geom, MultiLineString):
        # return cell object for line
        fea['geometry']['coordinates'] = densify_my_line(fea['geometry']['coordinates'], resolution)
        curr_coords = list(coords(fea))
        cells = line_to_DGGS(curr_coords, resolution)
    elif isinstance(geom, LineString):
        fea['geometry']['coordinates'] = densify_my_line([fea['geometry']['coordinates']], resolution)
        curr_coords = list(coords(fea))
        cells = line_to_DGGS(curr_coords, resolution)

    return cells


def get_cells_in_geojson(geojson, resolution, return_cell_obj=False):
    list_cells = []
    for fea in geojson['features']:  # for feature in attribute table
        res_cells = get_cells_in_feature(fea, resolution, return_cell_obj)
        list_cells = list(list_cells + res_cells)
    return list_cells


def reduce_duplicate_cells_2d_array(cells):
    # input 2-d array of cells
    # return original cells (str or object)
    unique_cells = []
    unique_cells_str = []
    for cell_array in cells:
        # 1-d array
        for cell in cell_array:
            cell_id = str(cell)
            if cell_id not in unique_cells_str:
                unique_cells_str.append(cell_id)
                unique_cells.append(cell)
    return unique_cells


def reduce_duplicate_cells_1d_array(cells):
    unique_cells = []
    unique_cells_str = []
    for cell in cells:
        cell_id = str(cell)
        if cell_id not in unique_cells_str:
            unique_cells_str.append(cell_id)
            unique_cells.append(cell)
    return unique_cells


def get_cells_in_json_and_return_in_json(geo_json, resolution, if_polygon):
    cells = get_cells_in_geojson(geo_json, resolution, if_polygon)
    cells = reduce_duplicate_cells_1d_array(cells)
    meta = {
        "cells_count": len(cells)
    }
    return {
        "meta": meta,
        "dggs_cells": [str(cell) for cell in cells],
        # "payload": geojson_obj
    }
