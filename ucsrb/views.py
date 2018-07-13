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
from accounts.forms import LogInForm, SignUpForm

def accounts_context():
    context = {
        'form': LogInForm(),
        'login_title': 'Login',
        'login_intro': 'Access your account',
        'registration_form': SignUpForm(),
        'registration_title': ' ', # space is needed to hide the defualt and insert a &nbsp; space
        'forgot_password_link': 'Forgot Password?',
        'register_link': ' ', # space is needed to hide the defualt and insert a &nbsp; space
        'help_link': ' ', # space is needed to hide the defualt and insert a &nbsp; space
    }
    return context

def index(request):
    template = loader.get_template('ucsrb/index.html')
    context = accounts_context()
    context['title'] = 'UCSRB FSTAT'
    return HttpResponse(template.render(context, request))

def home(request):
    template = loader.get_template('ucsrb/home.html')
    context = accounts_context()
    context['title'] = 'UCSRB'
    return HttpResponse(template.render(context, request))

def help(request):
    template = loader.get_template('ucsrb/help.html')
    context = accounts_context()
    context['title'] = 'UCSRB Terms Defined'
    return HttpResponse(template.render(context, request))

def methods(request):
    template = loader.get_template('ucsrb/methods.html')
    context = accounts_context()
    context['title'] = 'UCSRB Methods'
    return HttpResponse(template.render(context, request))

def app(request):
    template = loader.get_template('ucsrb/app.html')
    context = accounts_context()
    context['title'] = 'UCSRB'
    context['MAPBOX_TOKEN'] = settings.MAPBOX_ACCESS_TOKEN
    context['MAP_TECH'] = 'ol4'
    return HttpResponse(template.render(context, request))

def get_user_scenario_list(request):
    user_scenarios_list = []
    user_scenarios = TreatmentScenario.objects.filter(user=request.user)
    for us in user_scenarios:
        user_scenarios_list.append({
            "id": us.pk,
            "name": us.name,
            "description": us.description,
        })
    return JsonResponse(sorted(user_scenarios_list, key=lambda k: k['name'].lower()), safe=False)

def get_json_error_response(error_msg="Error", status_code=500, context={}):
    context['success'] = False
    context['error_msg'] = error_msg
    response = JsonResponse(context)
    response.status_code = status_code
    return response

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
    vegUnits = VegPlanningUnit.objects.filter(geometry__coveredby=bbox)
    # Select center-most veg unit (handle 0)
    if vegUnits.count() > 1:
        centerVegUnit = VegPlanningUnit.objects.filter(geometry__coveredby=bboxCenter)
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
    if request.method == 'GET':
        from .models import PourPoint
        ppt = PourPoint.objects.get(id=float(id))
    return JsonResponse(json.loads('{"id":%s,"geojson": %s}' % (ppt.pk, ppt.geometry.geojson)))

def get_basin(request):
    # focus_area = {"id": None, "geojson": None}
    if request.method == 'GET':
        from .models import FocusArea
        unit_id = request.GET['pourPoint']
        layer = 'PourPointOverlap'
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
                return get_json_error_response('Anonymous Users Not Allowed. Please log in.', 401, context)

        try:
            scenario = TreatmentScenario.objects.create(
                user=user,
                name=scenario_name,
                description=None,
                focus_area=True,
                focus_area_input=focus_area
            )
        except:
            # Technically we're testing for psycopg2's InternalError GEOSIntersects TopologyException
            return get_json_error_response('Drawings overlap. Please start over.', 500, context)

        if not scenario.geometry_dissolved:
            return get_json_error_response('Drawing does not cover any forested land in the Upper Columbia', 500, context)
        final_geometry = scenario.geometry_dissolved
        # EPSG:2163 = US National Atlas Equal Area
        final_geometry.transform(2163)
        if final_geometry.area/4046.86 < settings.MIN_TREATMENT_ACRES:
            return get_json_error_response('Treatment does not cover enough forested land to make a difference', 500, context)
        # return geometry to web mercator
        final_geometry.transform(3857)
        return JsonResponse(json.loads('{"id":%s,"geojson": %s}' % (scenario.pk, scenario.geometry_dissolved.geojson)))
    return get_json_error_response('Unable to save drawing.', 500, context)

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

# NEEDS:
#   pourpoint_id
### RDH - actually, we need to determine this from a given treatment scenario
### --- get all discrete ppt basins that intersect the treatment
### --- for each, get all downstream ppts
### --- consolidate all lists (including initial ppts) into a single unique list
def get_downstream_pour_points(request):
    from ucsrb.models import PourPoint, FocusArea
    pourpoint_id = request.GET.get('pourpoint_id')

    downstream_ids = []
    # TODO: get topology lookup strategy

    downstream_ppts = []
    for id in downstream_ids:
        ppt_dict = {}
        ppt = PourPoint.objects.get(pk=id)
        focus_area = FocusArea.objects.get(unit_id=id, unit_type='PourPointDiscrete')
        ppt_dict = {
            'name': focus_area.description,
            'id': id,
            'geometry': ppt.geometry.json
        }
        downstream_ppts.append(ppt_dict)
    return JsonResponse(downstream_ppts, safe=False)

def sort_output(flow_output):
    results = {}
    def get_timestamp_from_string(time_string):
        from datetime import datetime
        return datetime.strptime(time_string, "%m.%d.%Y-%H:%M:%S")
    for rx in flow_output.keys():
        time_keys = sorted(list(flow_output[rx].keys()), key=get_timestamp_from_string)
        results[rx] = [{'timestep':time_key, 'flow': flow_output[rx][time_key]} for time_key in time_keys]
    return results

def get_results_delta(flow_output):
    from copy import deepcopy
    out_dict = deepcopy(flow_output)
    for timestep in out_dict['baseline'].keys():
        baseflow = deepcopy(out_dict['baseline'][timestep])
        for rx in out_dict.keys():
            out_dict[rx][timestep] -= baseflow

    return sort_output(out_dict)

def get_results_7d_low(flow_output, sorted_results):
    from copy import deepcopy
    out_dict = deepcopy(flow_output)
    for rx in sorted_results.keys():
        for index, treatment_result in enumerate(sorted_results[rx]):
            timestep = treatment_result['timestep']
            if index < 7*8:
                flows = [x['flow'] for x in sorted_results[rx][0:56]]
            else:
                flows = [x['flow'] for x in sorted_results[rx][index-55:index+1]]
            low_flow = min(float(x) for x in flows)
            out_dict[rx][timestep] = low_flow
    return sort_output(out_dict)

def get_results_7d_mean(flow_output, sorted_results):
    from copy import deepcopy
    out_dict = deepcopy(flow_output)
    for rx in sorted_results.keys():
        for index, treatment_result in enumerate(sorted_results[rx]):
            timestep = treatment_result['timestep']
            if index < 7*8:
                flows = [x['flow'] for x in sorted_results[rx][0:56]]
            else:
                flows = [x['flow'] for x in sorted_results[rx][index-55:index+1]]
            mean_flow = sum(flows)/float(len(flows))
            out_dict[rx][timestep] = mean_flow
    return sort_output(out_dict)


def parse_flow_results(baseline_csv, treatment_csv):
    import csv
    from copy import deepcopy
    output_dict = {}

    with open(baseline_csv) as csvfile:
        csvReader = csv.DictReader(csvfile)
        for row in csvReader:
            if row['ppt_ID'] == 'bottom_basin':
                basin = 'bottom_basin'
            else:
                [basin, treatment] = row['ppt_ID'].split('-')
            if not basin in output_dict.keys():
                output_dict[basin] = {
                    'baseline': {}
                }
            # Convert total 3-hour flow to per-second flow
            output_dict[basin]['baseline'][row['Time']] = float(row['Value'])/3/60/60

    output_dict['bottom_basin']['mechanical'] = deepcopy(output_dict['bottom_basin']['baseline'])
    output_dict['bottom_basin']['rx_burn'] = deepcopy(output_dict['bottom_basin']['baseline'])
    output_dict['bottom_basin']['catastrophic_fire'] = deepcopy(output_dict['bottom_basin']['baseline'])

    with open(treatment_csv) as csvfile:
        csvReader = csv.DictReader(csvfile)
        for row in csvReader:
            [basin_id, treatment] = row['ppt_ID'].split('-')
            timestamp = row['Time']
            try:
                # get difference for upstream basin for timestamp from baseline
                delta = float(row['Value'])/3/60/60 - output_dict[basin]['baseline'][timestamp]
                # apply difference to bottom_basin
                output_dict['bottom_basin'][treatment][timestamp] += delta
            except:
                print('unable to update baseline value for %s %s %s' % (basin, treatment, timestamp))

    return output_dict['bottom_basin']

def get_basin_input_dict(basin_data, basin_geom, treatment_geom, row_id, treatment='baseline'):
    from ucsrb import project_settings as ucsrb_settings
    from ucsrb.models import VegPlanningUnit
    out_dict = {}
    vpus = VegPlanningUnit.objects.filter(geometry__intersects=basin_geom)

    for field in ucsrb_settings.HYDRO_INPUT_HEADERS:
        if 'thc_' in field:
            thc_id = int(field.split('_')[1])
            thc_veg_units = vpus.filter(topo_height_class_majority=thc_id)
            thc_acres = 0
            for veg_unit in thc_veg_units:
                # Reduce fractional coverage TO treatment target (take lowest val)
                if veg_unit.geometry.intersects(treatment_geom) and ucsrb_settings.TREATMENT_TARGETS[treatment] < veg_unit.percent_fractional_coverage:
                    thc_acres += veg_unit.acres*(ucsrb_settings.TREATMENT_TARGETS[treatment]/100)
                else:
                    thc_acres += veg_unit.acres*(veg_unit.percent_fractional_coverage/100)
            out_dict[field] = thc_acres
        else:
            if hasattr(basin_data, field):
                out_dict[field] = basin_data.__getattribute__(field)

    # we don't care about just basin id, but treatment, too. Using custom IDs.
    out_dict['ppt_ID'] = row_id

    # have the weather station fields been added to the ppbasin?
    has_weather_key = False
    # weather_key = 'mazama'
    #       (@ basin 2174, @ basin 2293)
    #       (20, 300k)
    weather_key = 'trinity'
    #       (20, 300k)
    # weather_key = 'poperidge'
    #       (15, 2M)
    # weather_key = 'plain'
    #       (20, 300k)
    # weather_key = 'winthrop'
    #       (billions, 5Q)
    for key in ucsrb_settings.WEATHER_STATIONS.keys():
        if not hasattr(basin_data, key):
            out_dict[key] = 0
        elif basin_data[key] > 0:
            has_weather_key = True
            weather_key = key

    if not has_weather_key:
        # NOTE: currently we only have climate data to support certain dates for certain weather station data.
        #   Due to this, we cannot 'weight' our stations, but must treat them as a binary: 0 or 100%.
        out_dict[weather_key] = 1

    out_dict['start_time'] = ucsrb_settings.WEATHER_STATIONS[weather_key]['start']
    out_dict['end_time'] = ucsrb_settings.WEATHER_STATIONS[weather_key]['end']

    return out_dict


def run_hydro_model(in_csv):
    from ucsrb import project_settings as ucsrb_settings
    import subprocess
    import os

    command = '/usr/bin/Rscript'
    script_location = "%s/%s" % (ucsrb_settings.ANALYSIS_DIR, 'DHSVMe.R')
    out_csv = "%s_out.csv" % ''.join(in_csv.lower().split('.csv'))

    r_output = subprocess.call([
        command, script_location,           # call the script with R
        '-i', in_csv,                       # location of input csv
        '-o', out_csv,                      # location to write csv output - comment out to get as a stream
        '-c', ucsrb_settings.ANALYSIS_DIR,  # Where the coefficient input files live
        '-t', "Coeff_*"                     # format to use to identify necessary coefficient files by year
    ])

    if ucsrb_settings.DELETE_CSVS:
        os.remove(in_csv)

    return out_csv

# NEEDS:
#   pourpoint_id
#   treatment_id
@cache_page(60 * 60) # 1 hour of caching
def get_hydro_results_by_pour_point_id(request):
    from ucsrb.models import PourPointBasin, TreatmentScenario, FocusArea, PourPoint
    from ucsrb import project_settings as ucsrb_settings
    import csv
    import time
    import os

    # Get pourpoint_id from request or API
    pourpoint_id = request.GET.get('pourpoint_id')
    ppb_d_data = PourPointBasin.objects.get(pk=pourpoint_id)
    ppb_d = FocusArea.objects.get(unit_id=pourpoint_id, unit_type='PourPointDiscrete')
    ppb_o = FocusArea.objects.get(unit_id=pourpoint_id, unit_type='PourPointOverlap')
    # Get treatment_id from request or API
    treatment_id = request.GET.get('treatment_id')
    treatment = TreatmentScenario.objects.get(pk=treatment_id)

    baseline_input_rows = []
    baseline_input_rows.append(get_basin_input_dict(ppb_d_data, ppb_d.geometry, treatment.geometry_dissolved, 'bottom_basin'))

    treatment_input_rows = []
    # - Get all encompassed discrete basins
    discrete_basin_ids = [x.id for x in PourPoint.objects.filter(geometry__coveredby=ppb_o.geometry)]
    if ppb_o.unit_id in discrete_basin_ids:
        # discrete_basin_ids.append(ppb_o.unit_id)
        discrete_basin_ids.remove(ppb_0.unit_id)
    sub_basins = FocusArea.objects.filter(unit_type="PourPointDiscrete", unit_id__in=discrete_basin_ids)

    # if len(sub_basins) > 5, this may take a LONG time to work through.
    # TODO: Disable 'Evaluate' button when too many Veg Units are impacted (issue #134)
    if len(sub_basins) > 10:
        print("Running Hydro model on %d basins! This may be a while..." % len(sub_basins))

    # - For each d_basin that intersects treatent scenario:
    for d_basin in sub_basins:
        sub_basin_id = d_basin.unit_id
        sub_basin_data = PourPointBasin.objects.get(pk=sub_basin_id)
        for treatment_type in ucsrb_settings.TREATMENT_TARGETS.keys():
            row_id = "%s-%s" % (sub_basin_id, treatment_type)
            if treatment_type == 'baseline':
                baseline_input_rows.append(get_basin_input_dict(sub_basin_data, d_basin.geometry, treatment.geometry_dissolved, row_id, treatment_type))
            else:
                treatment_input_rows.append(get_basin_input_dict(sub_basin_data, d_basin.geometry, treatment.geometry_dissolved, row_id, treatment_type))

    baseline_csv_filename = "%s/%s_%s_baseline.csv" % (ucsrb_settings.CSV_DIR, str(request.user.id), str(int(time.time()*100)))
    treatment_csv_filename = "%s/%s_%s_treatment.csv" % (ucsrb_settings.CSV_DIR, str(request.user.id), str(int(time.time()*100)))


    # write baseline csv
    with open(baseline_csv_filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=ucsrb_settings.HYDRO_INPUT_HEADERS)
        writer.writeheader()
        for row in baseline_input_rows:
            writer.writerow(row)

    # write delta csv
    with open(treatment_csv_filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=ucsrb_settings.HYDRO_INPUT_HEADERS)
        writer.writeheader()
        for row in treatment_input_rows:
            writer.writerow(row)

    results = {}
    baseline_out_csv = run_hydro_model(baseline_csv_filename)
    treatment_out_csv = run_hydro_model(treatment_csv_filename)
    flow_output = parse_flow_results(baseline_out_csv, treatment_out_csv)

    if ucsrb_settings.DELETE_CSVS:
        os.remove(baseline_out_csv)
        os.remove(treatment_out_csv)

    absolute_results = sort_output(flow_output)
    #   delta flow
    delta_results = get_results_delta(flow_output)
    #   7-day low-flow (needs sort_by_time)
    seven_d_low_results = get_results_7d_low(flow_output, absolute_results)
    seven_d_mean_results = get_results_7d_mean(flow_output, absolute_results)

    results = [
        {
            'title': 'Absolute Flow Rate @ 3hr Steps',
            'data': absolute_results
        },
        {
            'title': 'Seven Day Low Flow @ 3hr Steps',
            'data': seven_d_low_results
        },
        {
            'title': 'Seven Day Mean Flow @ 3hr Steps',
            'data': seven_d_mean_results
        },
        {
        'title': 'Change in Flow Rate @ 3hr Steps',
        'data': delta_results
        },
    ]

    return JsonResponse({'results': results})

@cache_page(60 * 60) # 1 hour of caching
def get_results_by_scenario_id(request):
    from ucsrb.models import TreatmentScenario, FocusArea, PourPoint, PourPointBasin
    from features.registry import get_feature_by_uid
    scenario_id = request.GET.get('id')
    export = request.GET.get('export')
    try:
        treatment = get_feature_by_uid(scenario_id)
    except:
        return get_json_error_response('Treatment with given ID (%s) does not exist' % scenario_id, 500, {})

    containing_overlap_basins = FocusArea.objects.filter(unit_type='PourPointOverlap', geometry__intersects=treatment.geometry_dissolved)

    impacted_pourpoint_ids = [x.unit_id for x in containing_overlap_basins]
    downstream_ppts = PourPoint.objects.filter(id__in=impacted_pourpoint_ids)

    if export:
        print("Export %s" % export)
    else:
        aggregate_results = treatment.aggregate_results()
        return_json = {
            'scenario': {
                'name': treatment.name,
                'acres': aggregate_results['total_acres']
            },
            'aggregate_results': aggregate_results['results_list'],
            'treatment_areas': [
                # TODO: Is this the 'boundary area' for the treatment, or the filtered veg-units themselves (which we already have)
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
            'pourpoints': [ {'id': x.pk, 'name': '', 'geometry': json.loads(x.geometry.json) } for x in downstream_ppts ]

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
    from ucsrb.models import VegPlanningUnit, FocusArea, PourPoint
    # from ucsrb import project_settings as ucsrb_settings
    # TODO: This would be nicer if it generically knew how to filter fields
    # by name, and what kinds of filters they were. For now, hard code.
    notes = []

    filter_dict = {}
    exclude_dict = {}

    if 'focus_area' in filters.keys() and 'focus_area_input' in filters.keys() and filters['focus_area']:
        # focus_area = FocusArea.objects.get(pk=filters['focus_area_input']).geometry;
        focus_area = FocusArea.objects.get(pk=filters['focus_area_input']);
        veg_unit_type_field = settings.FOCUS_AREA_FIELD_ID_LOOKUP[focus_area.unit_type]
        if veg_unit_type_field:
            if veg_unit_type_field == 'dwnstream_ppt_id':
                discrete_basin_ids = [x.id for x in PourPoint.objects.filter(geometry__coveredby=focus_area.geometry)]
                if not focus_area.unit_id in discrete_basin_ids:
                    discrete_basin_ids.append(focus_area.unit_id)
                filter_dict['dwnstream_ppt_id__in'] = discrete_basin_ids
            else:
                filter_dict[veg_unit_type_field] = focus_area.unit_id
        else:
                filter_dict['geometry__intersects'] = focus_area.geometry
    else:
        notes = ['Please Filter By Focus Area']
        query = VegPlanningUnit.objects.filter(pk=None)
        return (query, notes)

    if 'private_own' in filters.keys() and filters['private_own']:
        exclude_dict['pub_priv_own__icontains']='private'   # real value is 'Private land'

    if 'pub_priv_own' in filters.keys() and filters['pub_priv_own']:
        if 'pub_priv_own_input' in filters.keys():
            filter_dict['pub_priv_own__iexact'] = filters['pub_priv_own_input']

    if 'lsr_percent' in filters.keys() and filters['lsr_percent']:
        filter_dict['lsr_percent__lt'] = settings.LSR_THRESHOLD

    if 'has_critical_habitat' in filters.keys() and filters['has_critical_habitat']:
        filter_dict['percent_critical_habitat__lt'] = settings.CRIT_HAB_THRESHOLD
        exclude_dict['has_critical_habitat'] = True

    # if 'area' in filters.keys() and filters['area']:
    #     # RDH 1/8/18: filter(geometry__area_range(...)) does not seem available.
    #     # query = query.filter(geometry__area__range=(filters['area_min'], filters['area_max']))
    #
    #     # RDH 1/9/18: Why can't we use the model's 'Run Filters' function?
    #     # RDH 1/26/18: Because the model object doesn't exist yet.
    #     pu_ids = [pu.pk for pu in query if pu.geometry.area <= float(filters['area_max']) and pu.geometry.area>= float(filters['area_min'])]
    #     query = (query.filter(pk__in=pu_ids))

    if 'percent_roadless' in filters.keys() and filters['percent_roadless']:
        filter_dict['percent_roadless__lt'] = settings.ROADLESS_THRESHOLD

    if 'road_distance' in filters.keys() and filters['road_distance']:
        if 'road_distance_max' in filters.keys():
            filter_dict['road_distance__lte'] = float(filters['road_distance_max'])

    if 'percent_wetland' in filters.keys() and filters['percent_wetland']:
        filter_dict['percent_wetland__lt'] = settings.WETLAND_THRESHOLD

    if 'percent_riparian' in filters.keys() and filters['percent_riparian']:
        filter_dict['percent_riparian__lt'] = settings.RIPARIAN_THRESHOLD

    if 'slope' in filters.keys() and filters['slope']:
        if 'slope_max' in filters.keys():
            filter_dict['slope__lte'] = float(filters['slope_max'])

    if 'percent_fractional_coverage' in filters.keys() and filters['percent_fractional_coverage']:
        if 'percent_fractional_coverage_min' in filters.keys():
            filter_dict['percent_fractional_coverage__gte'] = float(filters['percent_fractional_coverage_min'])
        if 'percent_fractional_coverage_max' in filters.keys():
            filter_dict['percent_fractional_coverage__lte'] = float(filters['percent_fractional_coverage_max'])

    if 'percent_high_fire_risk_area' in filters.keys() and filters['percent_high_fire_risk_area']:
        filter_dict['percent_high_fire_risk_area__gt'] = settings.FIRE_RISK_THRESHOLD

    # 11 and 21 = ridgetops
    # 12 and 22 = north facing slopes
    # 13 and 23 = south facing slopes
    # 14 and 24 = valley bottoms
    # 15 and 25 = east and west facing slopes

    exclusion_list = []
    if 'landform_type' in filters.keys() and filters['landform_type']:
        if not 'landform_type_checkboxes_0' in filters.keys() or not filters['landform_type_include_north']:
            exclusion_list += [12, 22]
        if not 'landform_type_checkboxes_1' in filters.keys() or not filters['landform_type_include_south']:
            exclusion_list += [13, 23]
        if not 'landform_type_checkboxes_2' in filters.keys() or not filters['landform_type_include_ridgetop']:
            exclusion_list += [11, 21]
        if not 'landform_type_checkboxes_3' in filters.keys() or not filters['landform_type_include_floors']:
            exclusion_list += [14, 24]
        if not 'landform_type_checkboxes_4' in filters.keys() or not filters['landform_type_include_east_west']:
            exclusion_list += [15, 25]

    query = VegPlanningUnit.objects.filter(**filter_dict).exclude(**exclude_dict)
    # For some reason multiple keys in 'exclude_dict' don't always seem to process correctly
    if len(exclusion_list) > 0:
        query = query.exclude(topo_height_class_majority__in=exclusion_list)

    return (query, notes)

def parse_filter_checkboxes(request):
    filter_dict = dict(request.GET.items())
    landform_checkboxes = {
        'landform_type_checkboxes_0': 'landform_type_include_north',
        'landform_type_checkboxes_1': 'landform_type_include_south',
        'landform_type_checkboxes_2': 'landform_type_include_ridgetop',
        'landform_type_checkboxes_3': 'landform_type_include_floors',
        'landform_type_checkboxes_4': 'landform_type_include_east_west',
    }
    for checkbox_key in landform_checkboxes.keys():
        if checkbox_key in filter_dict.keys():
            if filter_dict[checkbox_key] == 'true':
                filter_dict[landform_checkboxes[checkbox_key]] = True
            else:
                filter_dict[landform_checkboxes[checkbox_key]] = False
        else:
            filter_dict[landform_checkboxes[checkbox_key]] = False
    return filter_dict


'''
'''
@cache_page(60 * 60) # 1 hour of caching
def get_filter_count(request, query=False, notes=[]):
    if not query:
        filter_dict = parse_filter_checkboxes(request)
        (query, notes) = run_filter_query(filter_dict)
    # from scenarios import views as scenarioViews
    # return scenarioViews.get_filter_count(request, query, notes)
    count = query.count()
    area_m2 = 0
    if count < 15000:
        for pu in query:
            clone_pu = pu.geometry.clone()
            clone_pu.transform(2163)
            area_m2 += clone_pu.area

        return HttpResponse("%d acres" % int(area_m2/4046.86), status=200)
    return HttpResponse("too many", status=200)


'''
'''
@cache_page(60 * 60) # 1 hour of caching
def get_filter_results(request, query=False, notes=[]):
    if not query:
        filter_dict = parse_filter_checkboxes(request)
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
            'mgmt_alloc_code': p_unit.mgmt_alloc_code,
            'mgmt_description': p_unit.mgmt_description,
            'mgmt_unit_id': p_unit.mgmt_unit_id,
            'dwnstream_ppt_id': p_unit.dwnstream_ppt_id,
            'topo_height_class_majority': p_unit.topo_height_class_majority
        })
    return HttpResponse(dumps(json))


def get_scenarios(request, scenario_model='treatmentscenario'):
    from scenarios.views import get_scenarios as scenarios_get_scenarios
    return scenarios_get_scenarios(request, scenario_model, 'ucsrb')

def demo(request, template='ucsrb/demo.html'):
    from scenarios import views as scenarios_views
    return scenarios_views.demo(request, template)
