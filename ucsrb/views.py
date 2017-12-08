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
def get_veg_unit_by_bbox(request):
    [minX, minY, maxX, maxY] = [float(x) for x in request.GET.getlist('bbox_coords[]')]
    # TODO: Get all veg units that intersect bbox (planning units)
    # TODO: Select first returned veg unit (handle 0)
    # TODO: build context and return.
    return_json = {
        'id': 1,
        'veg_unit_attrs': [
            ['int_attr', 100],
            ['float_attr', 99.999],
            ['str_attr', 'one hundred'],
            ['bool_attr', True],
            ['list_attr', [1,2,3,4]]
        ]
    }
    return JsonResponse(return_json)

def get_segment_by_bbox(request):
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
                # -120.42800903320311,
                # 47.63777890312004
                -13405984.640957793,
                6046804.319313334
              ],
              [
                # -120.42350292205809,
                # 47.635783590864854
                -13405483.02295974,
                6046474.684628907
              ],
              [
                # -120.41925430297852,
                # 47.635320898879414
                -13405010.068847293,
                6046398.247600632

              ],
              [
                # -120.4139757156372,
                # 47.6343665837201
                -13404422.459192432,
                6046240.596229818
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
                        #   -120.42819142341614,
                        #   47.637742756836566
                        -13406004.94454343,
                        6046798.347670506
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
                        #   -120.4241681098938,
                        #   47.635913722247565
                          -13405557.071330884,
                          6046496.182543105
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
                        # -120.41897535324097,
                        # 47.6353570468383
                        -13404979.016304556,
                        6046404.219243463
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
                        # -120.41693687438966,
                        # 47.63480036549851
                        -13404752.093876868,
                        6046312.255943821
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
                        # -120.41339635848999,
                        # 47.63433043507602
                        -13404357.965449827,
                        6046234.624586983
                    ]
                  }
                },
                'name': 'Point 5'
            },
        ]
    }
    return JsonResponse(return_json)

def get_segment_by_id(request, id):
    print('Segment ID: %s' % str(id))
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
                # -120.42800903320311,
                # 47.63777890312004
                -13405984.640957793,
                6046804.319313334
              ],
              [
                # -120.42350292205809,
                # 47.635783590864854
                -13405483.02295974,
                6046474.684628907
              ],
              [
                # -120.41925430297852,
                # 47.635320898879414
                -13405010.068847293,
                6046398.247600632
              ],
              [
                # -120.4139757156372,
                # 47.6343665837201
                -13404422.459192432,
                6046240.596229818
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
                        #   -120.42819142341614,
                        #   47.637742756836566
                        -13406004.94454343,
                        6046798.347670506
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
                        #   -120.4241681098938,
                        #   47.635913722247565
                        -13405557.071330884,
                        6046496.182543105
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
                        # -120.41897535324097,
                        # 47.6353570468383
                        -13404979.016304556,
                        6046404.219243463
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
                        # -120.41693687438966,
                        # 47.63480036549851
                        -13404752.093876868,
                        6046312.255943821
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
                        # -120.41339635848999,
                        # 47.63433043507602
                        -13404357.965449827,
                        6046234.624586983
                    ]
                  }
                },
                'name': 'Point 5'
            },
        ]
    }
    return JsonResponse(return_json)

def get_pourpoint_by_id(request, id):
    print('Pour Point ID: %s' % str(id))
    # TODO: query for pour point with given ID
    # TODO: query for pour point basin polygon with given ID
    # TODO: calculate area (on PPBasin model? On Madrona PolygonFeature model?)
    # TODO: build context and return.

    return_json = {
        'name': 'Pour Point 1',
        'id': 1,
        'area': 100.0, #acres
        'point_geometry': {
            "type": "Feature",
            "properties": {},
            "geometry": {
              "type": "Point",
              "coordinates": [
                #   -120.41339635848999,
                #   47.63433043507602
                -13404357.965449827,
                6046234.624586983
              ]
            }
          },
          'area_geometry': {
            "type": "Feature",
            "properties": {},
            "geometry": {
              "type": "LineString",
              "coordinates": [
                [
                    #   -120.42800903320311,
                    #   47.63777890312004
                    -13405984.640957793,
                    6046804.319313334
                ],
                [
                    #   -120.42350292205809,
                    #   47.635783590864854
                    -13405483.02295974,
                    6046474.684628907
                ],
                [
                    #   -120.41925430297852,
                    #   47.635320898879414
                    -13405010.068847293,
                    6046398.247600632
                ],
                [
                    #   -120.4139757156372,
                    #   47.6343665837201
                    -13404422.459192432,
                    6046240.596229818
                ]
              ]
            }
          }
    }
    return JsonResponse(return_json)

def filter_results(request):
    # TODO: Determine if pourpoint or management unit (ppid or muid with int in GET)
    # TODO: Query for pp or mu by id
    # TODO: Build filter based on given filters and geometry mask
    # TODO: Construct response out of query results
    return_json = {
        'count': 5,
        'features':{
            "type": "FeatureCollection",
            "features": [
                {
                  "type": "Feature",
                  "properties": {},
                  "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                      [
                        [
                            #   -120.41500568389894,
                            #   47.63523414367604
                            -13404537.114734845,
                            6046383.915657831
                        ],
                        [
                            #   -120.41363239288329,
                            #   47.635783590864854
                            -13404384.240678294,
                            6046474.684628907

                        ],
                        [
                            #   -120.41419029235838,
                            #   47.63636195008517
                            -13404446.345763769,
                            6046570.230914251

                        ],
                        [
                            #   -120.4153060913086,
                            #   47.6360727712752
                            -13404570.555934716,
                            6046522.457771576
                        ],
                        [
                            #   -120.41500568389894,
                            #   47.63523414367604
                            -13404537.114734845,
                            6046383.915657831
                        ]
                      ]
                    ]
                  }
                },
                {
                  "type": "Feature",
                  "properties": {},
                  "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                      [
                        [
                            #   -120.41959762573244,
                            #   47.63679571529933
                            -13405048.287361434,
                            6046641.8906282615
                        ],
                        [
                            #   -120.41826725006105,
                            #   47.63639086787812
                            -13404900.19061915,
                            6046575.008228514
                        ],
                        [
                            #   -120.41749477386473,
                            #   47.63754756647372
                            -13404814.198962338,
                            6046766.100799205
                        ],
                        [
                            #   -120.41839599609375,
                            #   47.637200559583725
                            -13404914.52256195,
                            6046708.773027998
                        ],
                        [
                            #   -120.41989803314209,
                            #   47.63795240493263
                            -13405081.7285613,
                            6046832.983198944
                        ],
                        [
                            #   -120.41959762573244,
                            #   47.63679571529933
                            -13405048.287361434,
                            6046641.8906282615
                        ]
                      ]
                    ]
                  }
                },
                {
                  "type": "Feature",
                  "properties": {},
                  "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                      [
                        [
                            #   -120.41642189025879,
                            #   47.63902232004572
                            -13404694.766105663,
                            6047009.743826828
                        ],
                        [
                            #   -120.41556358337401,
                            #   47.637721069054486
                            -13404599.219820317,
                            6046794.764684806
                        ],
                        [
                            #   -120.41363239288329,
                            #   47.63916690148871
                            -13404384.240678294,
                            6047033.630398162
                        ],
                        [
                            #   -120.41642189025879,
                            #   47.63902232004572
                            -13404694.766105663,
                            6047009.743826828
                        ]
                      ]
                    ]
                  }
                },
                {
                  "type": "Feature",
                  "properties": {},
                  "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                      [
                        [
                            #   -120.41878223419188,
                            #   47.63286277900884
                            -13404957.518390354,
                            6045992.175887919
                        ],
                        [
                            #   -120.42011260986327,
                            #   47.6324000611606
                            -13405105.615132637,
                            6045915.738859648
                        ],
                        [
                            #   -120.4191255569458,
                            #   47.6320530200857
                            -13404995.73690449,
                            6045858.4110884415
                        ],
                        [
                            #   -120.41878223419188,
                            #   47.63286277900884
                            -13404957.518390354,
                            6045992.175887919
                        ]
                      ]
                    ]
                  }
                },
                {
                  "type": "Feature",
                  "properties": {},
                  "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                      [
                        [
                            #   -120.42234420776367,
                            #   47.63485820279691
                            -13405354.035474528,
                            6046321.810572357
                        ],
                        [
                            #   -120.42191505432129,
                            #   47.63396171747802
                            -13405306.262331856,
                            6046173.713830074
                        ],
                        [
                            #   -120.42002677917479,
                            #   47.634221988993744
                            -13405096.0605041,
                            6046216.709658481
                        ],
                        [
                            #   -120.42006969451903,
                            #   47.6348871214221
                            -13405100.837818367,
                            6046326.587886624
                        ],
                        [
                            #   -120.42118549346924,
                            #   47.635118469847434
                            -13405225.047989316,
                            6046364.806400759
                        ],
                        [
                        #   -120.42234420776367,
                        #   47.63485820279691
                        -13405354.035474528,
                        6046321.810572357
                        ]
                      ]
                    ]
                  }
                }
            ]
        }
    }
    return JsonResponse(return_json)

def get_results_by_scenario_id(request):
    scenario_id = request.GET.get('id')
    export = request.GET.get('export')
    if export:
        print("Export %s" % export)
    else:
        # TODO: How do we create treatment areas? If this is just Veg Units then do in separate query
        return_json = {
            'aggregate_results': {
                'forest_types': {
                    'acres_dry': 30,
                    'pct_dry': 60,
                    'forest_totals': 60,        #This is in the comps - I don't know what it means.
                    'acres_wet': 30,
                    'pct_wet': 30,
                    'acres_cool': 30,
                    'pct_cool': 60,
                    'acres_moist': 30,
                    'pct_moist': 60,
                    'pct_deciduous': 50
                },
                'landforms/topography': {
                    'acres_north': 20,
                    'acres_south': 10,
                    'acres_bottom': 10,
                    'acres_top': 5,
                    'avg_slope': 30,
                    'pct_cover_reduction': 5
                }
            },

            'treatment_areas': [
                {
                    'id': 1,
                    'geometry': {
                      "type": "Polygon",
                      "coordinates": [
                        [
                          [
                            # -120.41500568389894,
                            # 47.63523414367604
                            -13404537.114734845,
                            6046383.915657831
                          ],
                          [
                            # -120.41363239288329,
                            # 47.635783590864854
                            -13404384.240678294,
                            6046474.684628907
                          ],
                          [
                            # -120.41419029235838,
                            # 47.63636195008517
                            -13404446.345763769,
                            6046570.230914251
                          ],
                          [
                            # -120.4153060913086,
                            # 47.6360727712752
                            -13404570.555934716,
                            6046522.457771576
                          ],
                          [
                            # -120.41500568389894,
                            # 47.63523414367604
                            -13404537.114734845,
                            6046383.915657831
                          ]
                        ]
                      ]
                    },
                    'results': {
                        'name': 'Region 1',
                        'acres': 40,
                        'pct_deciduous': 50,
                        'acres_north': 20,
                        'acres_moist': 30,
                        'pct_moist': 60
                    }
                },
                {
                    'id': 2,
                    'geometry': {
                      "type": "Polygon",
                      "coordinates": [
                        [
                          [
                            # -120.41959762573244,
                            # 47.63679571529933
                            -13405048.287361434,
                            6046641.8906282615
                          ],
                          [
                            # -120.41826725006105,
                            # 47.63639086787812
                            -13404900.19061915,
                            6046575.008228514
                          ],
                          [
                            # -120.41749477386473,
                            # 47.63754756647372
                            -13404814.198962338,
                            6046766.100799205
                          ],
                          [
                            # -120.41839599609375,
                            # 47.637200559583725
                            -13404914.52256195,
                            6046708.773027998
                          ],
                          [
                            # -120.41989803314209,
                            # 47.63795240493263
                            -13405081.7285613,
                            6046832.983198944
                          ],
                          [
                            # -120.41959762573244,
                            # 47.63679571529933
                            -13405048.287361434,
                            6046641.8906282615
                          ]
                        ]
                      ]
                    },
                    'results': {
                        'name': 'Region 2',
                        'acres': 30,
                        'pct_deciduous': 70,
                        'acres_north': 10,
                        'acres_moist': 10,
                        'pct_moist': 33
                    }
                },
            ],
            'pourpoints': [
                {
                    'id': 1,
                    'name': 'Pour Point 1',
                    'geometry': {
                        "type": "Feature",
                        "properties": {},
                        "geometry": {
                          "type": "Point",
                          "coordinates": [
                            #   -120.41339635848999,
                            #   47.63433043507602
                            -13404357.965449827,
                            6046234.624586983
                          ]
                        }
                    },
                    'hydro_results': {
                        '7_day_low_flow':{
                            'title': '7-day low flow',
                            'chart_title': 'Streamflow: Cubic Feet per Second',
                            'fc_50': {
                                'label': '50% Fractional Coverage',
                                'data': [          # diff from baseline (? these numbers would be a 'total')
                                    ('Jan', 300),
                                    ('Feb', 280),
                                    ('Mar', 320),
                                    ('Apr', 840),
                                    ('May', 1500),
                                    ('Jun', 1500),
                                    ('Jul', 400),
                                    ('Aug', 100),
                                    ('Sep', 100),
                                    ('Oct', 200),
                                    ('Nov', 400),
                                    ('Dec', 300),
                                ]
                            },
                            'fc_30': {
                                'label': '30% Fractional Coverage',
                                'data': [          # 30% fractional coverage results
                                    ('Jan', 300),
                                    ('Feb', 200),
                                    ('Mar', 320),
                                    ('Apr', 700),
                                    ('May', 1000),
                                    ('Jun', 1000),
                                    ('Jul', 800),
                                    ('Aug', 600),
                                    ('Sep', 400),
                                    ('Oct', 240),
                                    ('Nov', 400),
                                    ('Dec', 300),
                                ]
                            },
                            'fc_0': {
                                'label': '0% Fractional Coverage',
                                'data': [          # 0% fractional coverage results
                                    ('Jan', 200),
                                    ('Feb', 200),
                                    ('Mar', 300),
                                    ('Apr', 700),
                                    ('May', 800),
                                    ('Jun', 800),
                                    ('Jul', 800),
                                    ('Aug', 800),
                                    ('Sep', 600),
                                    ('Oct', 360),
                                    ('Nov', 400),
                                    ('Dec', 300),
                                ],
                            }
                        }
                    },
                },
                {
                    'id': 2,
                    'name': 'Pour Point 2',
                    'geometry': {
                        "type": "Feature",
                        "properties": {},
                        "geometry": {
                          "type": "Point",
                          "coordinates": [
                            # -120.4241681098938,
                            # 47.635913722247565
                            -13405557.071330884,
                            6046496.182543105
                          ]
                        }
                    },
                    'hydro_results': {
                        '7_day_low_flow':{
                            'title': '7-day low flow',
                            'chart_title': 'Streamflow: Cubic Feet per Second',
                            'fc_50': {
                                'label': '50% Fractional Coverage',
                                'data': [          # diff from baseline (? these numbers would be a 'total')
                                    ('Jan', 300),
                                    ('Feb', 280),
                                    ('Mar', 320),
                                    ('Apr', 840),
                                    ('May', 1500),
                                    ('Jun', 1500),
                                    ('Jul', 400),
                                    ('Aug', 100),
                                    ('Sep', 100),
                                    ('Oct', 200),
                                    ('Nov', 400),
                                    ('Dec', 300),
                                ]
                            },
                            'fc_30': {
                                'label': '30% Fractional Coverage',
                                'data': [          # 30% fractional coverage results
                                    ('Jan', 300),
                                    ('Feb', 200),
                                    ('Mar', 320),
                                    ('Apr', 700),
                                    ('May', 1000),
                                    ('Jun', 1000),
                                    ('Jul', 800),
                                    ('Aug', 600),
                                    ('Sep', 400),
                                    ('Oct', 240),
                                    ('Nov', 400),
                                    ('Dec', 300),
                                ]
                            },
                            'fc_0': {
                                'label': '0% Fractional Coverage',
                                'data': [          # 0% fractional coverage results
                                    ('Jan', 200),
                                    ('Feb', 200),
                                    ('Mar', 300),
                                    ('Apr', 700),
                                    ('May', 800),
                                    ('Jun', 800),
                                    ('Jul', 800),
                                    ('Aug', 800),
                                    ('Sep', 600),
                                    ('Oct', 360),
                                    ('Nov', 400),
                                    ('Dec', 300),
                                ],
                            }
                        }
                    },
                },
            ]
        }
        return JsonResponse(return_json)

def get_results_by_state(request):
    return_json = {
        'response': 'TODO :('
    }
    return JsonResponse(return_json)

def get_planningunits(request):
    from ucsrb.models import VegPlanningUnit
    from json import dumps
    json = []
    # planningunits = PlanningUnit.objects.filter(avg_depth__lt=0.0, min_wind_speed_rev__isnull=False)
    planningunits = VegPlanningUnit.objects.all()
    for p_unit in planningunits:
        json.append({
            'id': p_unit.id,
            'wkt': p_unit.geometry.wkt,
            'has_roads': p_unit.has_roads,
            'has_endangered_habitat': p_unit.has_endangered_habitat,
            'is_private': p_unit.is_private,
            'has_high_fire_risk': p_unit.has_high_fire_risk,
            'miles_from_road_access': p_unit.miles_from_road_access,
            'vegetation_type': p_unit.vegetation_type,
            'forest_height': p_unit.forest_height,
            'forest_class': p_unit.forest_class,
            'slope': p_unit.slope,
            'canopy_coverage': p_unit.canopy_coverage,
        })
    return HttpResponse(dumps(json))
