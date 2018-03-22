from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import json
from ucsrb.models import TreatmentScenario
from django.conf import settings
from django.views.decorators.cache import cache_page

def index(request):
    template = loader.get_template('ucsrb/index.html')
    context = {
        'title': 'UCSRB FSTAT',
        'self': {
            'title': 'UCSRB Snowpack Treatment'
        }
    }
    return HttpResponse(template.render(context, request))

def home(request):
    template = loader.get_template('ucsrb/home.html')
    context = {
        'title': 'UCSRB',
        'self': {
            'title': 'UCSRB'
        }
    }
    return HttpResponse(template.render(context, request))

def app(request):
    template = loader.get_template('ucsrb/app.html')
    # user_scenario_list = get_user_scenario_list(request)
    context = {
        'MAPBOX_TOKEN': settings.MAPBOX_ACCESS_TOKEN,
        # 'user_scenario_list': user_scenario_list,
    }
    context['MAP_TECH'] = 'ol4'
    return HttpResponse(template.render(context, request))

def sign_in(request):
    context = {}
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        context['success'] = True
        context['username'] = username
        context['user_id'] = user.id
        # allow user to save, load, or continue
        return JsonResponse(context)
    else:
        context['success'] = False
        context['error_msg'] = 'Invalid username/password.'
        # Return an 'invalid login' error message.
        return JsonResponse(context)

def sign_out(request):
    logout(request)
    # Redirect to a success page or success message
    # no error thrown by logout
    return HttpResponse('logout successful')

def register(request):
    context = {}
    username = request.POST['username']
    email = request.POST['email']
    password = request.POST['password']
    password_confirm = request.POST['password_confirm']
    if password != password_confirm:
        context['success'] = False
        context['error_msg'] = 'Password does not match the confirm password.'
        return JsonResponse(context)
    try:
        user = User.objects.create_user(username, email, password)
        user_auth = authenticate(request, username=username, password=password)
        if user_auth is not None:
            login(request, user)
            context['success'] = True
            context['username'] = username
            return JsonResponse(context)
        else:
            context['success'] = False
            context['error_msg'] = 'Invalid username/password.'
            return JsonResponse(context)
    except:
        context['success'] = False
        context['error_msg'] = 'User already exists.'
        return JsonResponse(context)

def get_user_scenario_list(request):
    user_scenarios_list = []
    user_scenarios = TreatmentScenario.objects.filter(user=request.user)
    for us in user_scenarios:
        user_scenarios_list.append({
            "id": us.pk,
            "name": us.name,
            "description": us.description,
        })
    return JsonResponse(user_scenarios_list, safe=False)


###########################################################
###             API Calls                                 #
###########################################################
def build_bbox(minX, minY, maxX, maxY):
    from django.contrib.gis.geos import Polygon, Point
    bbox = Polygon( ((minX,minY), (minX,maxY), (maxX,maxY), (maxX,minY), (minX,minY)) )
    bboxCenter = Point( ((minX + maxX)/2,(minY+maxY)/2))
    return (bbox, bboxCenter)

def get_veg_unit_by_bbox(request):
    [minX, minY, maxX, maxY] = [float(x) for x in request.GET.getlist('bbox_coords[]')]
    bbox, bboxCenter = build_bbox(minX, minY, maxX, maxY)
    # Get all veg units that intersect bbox (planning units)
    from .models import VegPlanningUnit
    vegUnits = VegPlanningUnit.objects.filter(geometry__intersects=bbox)
    # Select center-most veg unit (handle 0)
    if vegUnits.count() > 1:
        centerVegUnit = VegPlanningUnit.objects.filter(geometry__intersects=bboxCenter)
        if centerVegUnit.count() == 1:
            retVegUnit = centerVegUnit[0].geometry.geojson
        else:
            retVegUnit = vegUnits[0].geometry.geojson
    elif vegUnits.count() == 1:
        retVegUnit = vegUnits[0].geometry.geojson
    else:
        retVegUnit = {}
    # TODO: build context and return.

    return JsonResponse(json.loads(retVegUnit))

def get_segment_by_bbox(request):
    [minX, minY, maxX, maxY] = [float(x) for x in request.GET.getlist('bbox_coords[]')]
    bbox, bboxCenter = build_bbox(minX, minY, maxX, maxY)
    # TODO: Get all stream segments that intersect bbox
    # from .models import StreamSegment
    # segments = StreamSegments.objects.filter(geometry__intersect=bbox)

    # TODO: Select first returned stream segment (handle 0)
    # if segments.count() > 1:
    #     centerSegment = StreamSegment.objects.filter(geometry__intersects=bboxCenter)
    #     if centerSegment.count() == 1:
    #         retSegment = centerSegment[0]
    #     else:
    #         retSegment = segments[0]
    # elif segments.count() ==1:
    #     retSegment = segments[0]
    # else:
    #     retSegment = {}
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
                -13456724.956927,
                6267755.715506
              ],
              [
                # -120.42350292205809,
                # 47.635783590864854
                -13444104.937438,
                6262993.345038
              ],
              [
                # -120.41925430297852,
                # 47.635320898879414
                -13434206.953435,
                6244962.538670

              ],
              [
                # -120.4139757156372,
                # 47.6343665837201
                -13413984.236904,
                6260226.324847
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
                        -13413984.236904,
                        6260226.324847
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
                        -13434206.953435,
                        6244962.538670
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
                        -13456724.956927,
                        6267755.715506
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
                        -13419383.213187,
                        6256862.791188
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

def get_basin(request):
    # focus_area = {"id": None, "geojson": None}
    if request.method == 'GET':
        from .models import FocusArea
        unit_id = request.GET['pourPoint']
        layer = 'PourPoint'
        focus_area = FocusArea.objects.get(unit_type=layer, unit_id=unit_id)
    return JsonResponse(json.loads('{"id":%s,"geojson": %s}' % (focus_area.pk, focus_area.geometry.geojson)))

def save_drawing(request):
    context = {}
    if request.method == 'POST':
        from .models import FocusArea, TreatmentScenario
        featJson = request.POST['drawing']
        from django.contrib.gis.geos import MultiPolygon, Polygon, GEOSGeometry
        polys = []
        for feature in json.loads(featJson)['features']:
            polys.append(GEOSGeometry(json.dumps(feature['geometry'])))

        if polys[0].geom_type == 'MultiPolygon' and len(polys) == 1:
            geometry = polys[0]
        else:
            try:
                geometry = MultiPolygon(polys)
            except TypeError:
                for poly in polys:
                    if poly.geom_type == 'MultiPolygon':
                        poly = poly.union(poly) #RDH: in tests this seems to
                                # result in a Polygon - I'm not sure that this
                                # is always true, but I don't know that this
                                # is a real use case anyway...
                geometry = MultiPolygon(polys)
                print('ucsrb.views.save drawing: List of polygons may contain an illegal multipolygon.')
        layer = 'Drawing'
        focus_area = FocusArea.objects.create(unit_type=layer, geometry=geometry)
        focus_area.save()

        scenario_name = request.POST['name']
        description = request.POST['description']

        user = request.user
        if not user.is_authenticated:
            if settings.ALLOW_ANONYMOUS_DRAW == True:
                from django.contrib.auth.models import User
                user = User.objects.get(pk=settings.ANONYMOUS_USER_PK)
            else:
                context['success'] = False
                context['error_msg'] = 'Anonymous Users Not Allowed. Please log in.'
                # Return an 'invalid login' error message.
                response = JsonResponse(context)
                response.status_code = 401
                return response

        scenario = TreatmentScenario.objects.create(
            user=user,
            name=scenario_name,
            description=None,
            focus_area=True,
            focus_area_input=focus_area
        )

        if not scenario.geometry_dissolved:
            context['success'] = False
            context['error_msg'] = 'Drawing does not cover any forested land in the Upper Columbia'
            response = JsonResponse(context)
            response.status_code = 500
            return response
        final_geometry = scenario.geometry_dissolved
        # EPSG:2163 = US National Atlas Equal Area
        final_geometry.transform(2163)
        if final_geometry.area/4046.86 < settings.MIN_TREATMENT_ACRES:
            context['success'] = False
            context['error_msg'] = 'Treatment does not cover enough forested land to make a difference'
            response = JsonResponse(context)
            response.status_code = 500
            return response
        # return geometry to web mercator
        final_geometry.transform(3857)
        return JsonResponse(json.loads('{"id":%s,"geojson": %s}' % (scenario.pk, scenario.geometry_dissolved.geojson)))
    context['success'] = False
    context['error_msg'] = 'Unable to save drawing.'
    # Return an 'invalid login' error message.
    response = JsonResponse(context)
    response.status_code = 500
    return response

'''
Take a point in 3857 and return the feature at that point for a given FocusArea type
Primarily developed as a failsafe for not having pour point basin data.
'''
def get_focus_area_at(request):
    from django.contrib.gis.geos import Point
    focus_area = {"id": None, "geojson": None}
    if request.method == 'GET':
        from .models import FocusArea
        point = request.GET.getlist('point[]')
        pointGeom = Point( (float(point[0]), float(point[1])))
        layer = request.GET['layer']
        focus_area = FocusArea.objects.get(unit_type=layer, geometry__intersects=pointGeom)
    return JsonResponse(json.loads('{"id":%s,"geojson": %s}' % (focus_area.unit_id, focus_area.geometry.geojson)))

def get_focus_area(request):
    focus_area = {"id": None, "geojson": None}
    if request.method == 'GET':
        from .models import FocusArea
        unit_id = request.GET['id']
        layer = request.GET['layer']
        focus_area = FocusArea.objects.get(unit_type=layer.upper(), unit_id=unit_id)

    return JsonResponse(json.loads('{"id":%s,"geojson": %s}' % (focus_area.pk, focus_area.geometry.geojson)))


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

'''
'''

def run_filter_query(filters):
    from collections import OrderedDict
    from ucsrb.models import VegPlanningUnit, FocusArea
    # TODO: This would be nicer if it generically knew how to filter fields
    # by name, and what kinds of filters they were. For now, hard code.
    notes = []

    if 'focus_area' in filters.keys() and 'focus_area_input' in filters.keys() and filters['focus_area']:
        focus_area = FocusArea.objects.get(pk=filters['focus_area_input']).geometry;
        query = VegPlanningUnit.objects.filter(geometry__intersects=focus_area)
    else:
        notes = ['Please Filter By Focus Area']
        query = VegPlanningUnit.objects.filter(pk=None)
        return (query, notes)

    if 'private_own' in filters.keys() and filters['private_own']:
        if 'avoid_private_input' in filters.keys():
            if filters['avoid_private_input'] == 'Avoid':
                pu_ids = [pu.pk for pu in query if pu.pub_priv_own.lower() not in ['private land', 'private']]
            else:
                pu_ids = [pu.pk for pu in query if pu.pub_priv_own.lower() in ['private land', 'private']]
        else:
            pu_ids = [pu.pk for pu in query if pu.pub_priv_own.lower() not in ['private land', 'private']]
        query = (query.filter(pk__in=pu_ids))

    if 'pub_priv_own' in filters.keys() and filters['pub_priv_own']:
        if 'pub_priv_own_input' in filters.keys():
            pu_ids = [pu.pk for pu in query if pu.pub_priv_own.lower() == filters['pub_priv_own_input'].lower()]
        else:
            pu_ids = [pu.pk for pu in query]
        query = (query.filter(pk__in=pu_ids))

    if 'lsr_percent' in filters.keys() and filters['lsr_percent']:
        pu_ids = [pu.pk for pu in query if pu.lsr_percent < settings.LSR_THRESHOLD]
        query = (query.filter(pk__in=pu_ids))

    if 'has_critical_habitat' in filters.keys() and filters['has_critical_habitat']:
        pu_ids = [pu.pk for pu in query if pu.percent_critical_habitat < settings.CRIT_HAB_THRESHOLD and not pu.has_critical_habitat]
        query = (query.filter(pk__in=pu_ids))

    # if 'area' in filters.keys() and filters['area']:
    #     # RDH 1/8/18: filter(geometry__area_range(...)) does not seem available.
    #     # query = query.filter(geometry__area__range=(filters['area_min'], filters['area_max']))
    #
    #     # RDH 1/9/18: Why can't we use the model's 'Run Filters' function?
    #     # RDH 1/26/18: Because the model object doesn't exist yet.
    #     pu_ids = [pu.pk for pu in query if pu.geometry.area <= float(filters['area_max']) and pu.geometry.area>= float(filters['area_min'])]
    #     query = (query.filter(pk__in=pu_ids))

    if 'percent_roadless' in filters.keys() and filters['percent_roadless']:
        pu_ids = [pu.pk for pu in query if pu.percent_roadless < settings.ROADLESS_THRESHOLD]
        query = (query.filter(pk__in=pu_ids))

    if 'road_distance' in filters.keys() and filters['road_distance']:
        if 'road_distance_max' in filters.keys():
            pu_ids = [pu.pk for pu in query if pu.road_distance <= float(filters['road_distance_max'])]
            query = (query.filter(pk__in=pu_ids))

    if 'percent_wetland' in filters.keys() and filters['percent_wetland']:
        pu_ids = [pu.pk for pu in query if pu.percent_wetland < settings.WETLAND_THRESHOLD]
        query = (query.filter(pk__in=pu_ids))

    if 'percent_riparian' in filters.keys() and filters['percent_riparian']:
        pu_ids = [pu.pk for pu in query if pu.percent_riparian < settings.RIPARIAN_THRESHOLD]
        query = (query.filter(pk__in=pu_ids))

    if 'slope' in filters.keys() and filters['slope']:
        if 'slope_max' in filters.keys():
            pu_ids = [pu.pk for pu in query if pu.slope <= float(filters['slope_max'])]
            query = (query.filter(pk__in=pu_ids))

    if 'percent_fractional_coverage' in filters.keys() and filters['percent_fractional_coverage']:
        if 'percent_fractional_coverage_min' in filters.keys():
            pu_ids = [pu.pk for pu in query if pu.percent_fractional_coverage >= float(filters['percent_fractional_coverage_min'])]
            query = (query.filter(pk__in=pu_ids))
        if 'percent_fractional_coverage_max' in filters.keys():
            pu_ids = [pu.pk for pu in query if pu.percent_fractional_coverage <= float(filters['percent_fractional_coverage_max'])]
            query = (query.filter(pk__in=pu_ids))

    if 'percent_high_fire_risk_area' in filters.keys() and filters['percent_high_fire_risk_area']:
        pu_ids = [pu.pk for pu in query if pu.percent_high_fire_risk_area < settings.FIRE_RISK_THRESHOLD]
        query = (query.filter(pk__in=pu_ids))

    return (query, notes)


'''
'''
@cache_page(60 * 60) # 1 hour of caching
def get_filter_count(request, query=False, notes=[]):
    if not query:
        filter_dict = dict(request.GET.items())
        (query, notes) = run_filter_query(filter_dict)
    from scenarios import views as scenarioViews
    return scenarioViews.get_filter_count(request, query, notes)
    # return HttpResponse(query.count(), status=200)


'''
'''
@cache_page(60 * 60) # 1 hour of caching
def get_filter_results(request, query=False, notes=[]):
    if not query:
        filter_dict = dict(request.GET.items())
        (query, notes) = run_filter_query(filter_dict)
    from scenarios import views as scenarioViews
    return scenarioViews.get_filter_results(request, query, notes)


@cache_page(60 * 60) # 1 hour of caching
def get_planningunits(request):
    from ucsrb.models import VegPlanningUnit
    from json import dumps
    json = []
    # planningunits = PlanningUnit.objects.filter(avg_depth__lt=0.0, min_wind_speed_rev__isnull=False)
    planningunits = VegPlanningUnit.objects.all()
    for p_unit in planningunits:
        json.append({
            'id': p_unit.pk,
            'wkt': p_unit.geometry.wkt,
            'acres': p_unit.acres,
            'huc_2_id': p_unit.huc_2_id,
            'huc_4_id': p_unit.huc_4_id,
            'huc_6_id': p_unit.huc_6_id,
            'huc_8_id': p_unit.huc_8_id,
            'huc_10_id': p_unit.huc_10_id,
            'huc_12_id': p_unit.huc_12_id,
            'pub_priv_own': p_unit.pub_priv_own,
            'lsr_percent': p_unit.lsr_percent,
            'has_critical_habitat': p_unit.has_critical_habitat,
            'percent_critical_habitat': p_unit.percent_critical_habitat,
            'percent_roadless': p_unit.percent_roadless,
            'percent_wetland': p_unit.percent_wetland,
            'percent_riparian': p_unit.percent_riparian,
            'slope': p_unit.slope,
            'road_distance': p_unit.road_distance,
            'percent_fractional_coverage': p_unit.percent_fractional_coverage,
            'percent_high_fire_risk_area': p_unit.percent_high_fire_risk_area,
        })
    return HttpResponse(dumps(json))


def get_scenarios(request, scenario_model='treatmentscenario'):
    from scenarios.views import get_scenarios as scenarios_get_scenarios
    return scenarios_get_scenarios(request, scenario_model, 'ucsrb')

def demo(request, template='ucsrb/demo.html'):
    from scenarios import views as scenarios_views
    return scenarios_views.demo(request, template)
