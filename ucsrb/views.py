from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.template import loader
import json

def index(request):
    template = loader.get_template('index.html')
    context = {
        'title': 'UCSRB FSTAT',
        'self': {
            'title': 'UCSRB Snowpack Treatment'
        }
    }
    return HttpResponse(template.render(context, request))

###########################################################
###             API Calls                                 #
###########################################################
def get_segment_by_bbox(request):
    # Get bbox [minX, minY, maxX, maxY] from request
    [minX, minY, maxX, maxY] = [float(x) for x in request.GET.getlist('bbox_coords[]')]
    # TODO: Get all stream segments that intersect bbox
    # TODO: Select first returned stream segment (handle 0)
    # TODO: get list of Pourpoints associated with stream segment
    # TODO: build context and return.
    return_json = {
        'name': 'Stream Segment Name',
        'id': 1,
        'geometry': {
          "type": "Feature",
          "properties": {},
          "geometry": {
            "type": "LineString",
            "coordinates": [
              [
                -120.42800903320311,
                47.63777890312004
              ],
              [
                -120.42350292205809,
                47.635783590864854
              ],
              [
                -120.41925430297852,
                47.635320898879414
              ],
              [
                -120.4139757156372,
                47.6343665837201
              ]
            ]
          }
        },
        'pourpoints': [
            {
                'id': 1,
                'geometry':    {
                  "type": "Feature",
                  "properties": {},
                  "geometry": {
                    "type": "Point",
                    "coordinates": [
                      -120.42819142341614,
                      47.637742756836566
                    ]
                  }
                },
                'name': 'Point 1'
            },
            {
                'id': 2,
                'geometry':    {
                  "type": "Feature",
                  "properties": {},
                  "geometry": {
                    "type": "Point",
                    "coordinates": [
                      -120.4241681098938,
                      47.635913722247565
                    ]
                  }
                },
                'name': 'Point 2'
            },
            {
                'id': 3,
                'geometry':    {
                  "type": "Feature",
                  "properties": {},
                  "geometry": {
                    "type": "Point",
                    "coordinates": [
                      -120.41897535324097,
                      47.6353570468383
                    ]
                  }
                },
                'name': 'Point 3'
            },
            {
                'id': 4,
                'geometry':    {
                  "type": "Feature",
                  "properties": {},
                  "geometry": {
                    "type": "Point",
                    "coordinates": [
                      -120.41693687438966,
                      47.63480036549851
                    ]
                  }
                },
                'name': 'Point 4'
            },
            {
                'id': 5,
                'geometry':    {
                  "type": "Feature",
                  "properties": {},
                  "geometry": {
                    "type": "Point",
                    "coordinates": [
                      -120.41339635848999,
                      47.63433043507602
                    ]
                  }
                },
                'name': 'Point 5'
            },
        ]
    }
    return JsonResponse(return_json)

def get_segment_by_id(request):
    segment_id = request.GET.get('id')
    # TODO: query for stream segment with given ID
    # TODO: get list of Pourpoints associated with stream segment
    # TODO: build context and return.
    return_json = {
        'name': 'Stream Segment Name',
        'id': 1,
        'geometry': {
          "type": "Feature",
          "properties": {},
          "geometry": {
            "type": "LineString",
            "coordinates": [
              [
                -120.42800903320311,
                47.63777890312004
              ],
              [
                -120.42350292205809,
                47.635783590864854
              ],
              [
                -120.41925430297852,
                47.635320898879414
              ],
              [
                -120.4139757156372,
                47.6343665837201
              ]
            ]
          }
        },
        'pourpoints': [
            {
                'id': 1,
                'geometry':    {
                  "type": "Feature",
                  "properties": {},
                  "geometry": {
                    "type": "Point",
                    "coordinates": [
                      -120.42819142341614,
                      47.637742756836566
                    ]
                  }
                },
                'name': 'Point 1'
            },
            {
                'id': 2,
                'geometry':    {
                  "type": "Feature",
                  "properties": {},
                  "geometry": {
                    "type": "Point",
                    "coordinates": [
                      -120.4241681098938,
                      47.635913722247565
                    ]
                  }
                },
                'name': 'Point 2'
            },
            {
                'id': 3,
                'geometry':    {
                  "type": "Feature",
                  "properties": {},
                  "geometry": {
                    "type": "Point",
                    "coordinates": [
                      -120.41897535324097,
                      47.6353570468383
                    ]
                  }
                },
                'name': 'Point 3'
            },
            {
                'id': 4,
                'geometry':    {
                  "type": "Feature",
                  "properties": {},
                  "geometry": {
                    "type": "Point",
                    "coordinates": [
                      -120.41693687438966,
                      47.63480036549851
                    ]
                  }
                },
                'name': 'Point 4'
            },
            {
                'id': 5,
                'geometry':    {
                  "type": "Feature",
                  "properties": {},
                  "geometry": {
                    "type": "Point",
                    "coordinates": [
                      -120.41339635848999,
                      47.63433043507602
                    ]
                  }
                },
                'name': 'Point 5'
            },
        ]
    }
    return JsonResponse(return_json)
