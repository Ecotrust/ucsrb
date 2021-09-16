# Create your views here.
from collections import OrderedDict
from copy import deepcopy, copy
from datetime import datetime
import time
import json
import os
from pathlib import Path

from accounts.forms import LogInForm, SignUpForm
from geodata.geodata import GeoData
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.gis.geos import MultiPolygon, Polygon, GEOSGeometry, Point
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.temp import NamedTemporaryFile
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template import loader
from django.views.decorators.cache import cache_page
from ucsrb.forms import UploadShapefileForm
from ucsrb.models import FocusArea, TreatmentScenario, StreamFlowReading, TreatmentArea
from features.registry import get_feature_by_uid

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
    context['HERE_TOKEN'] = settings.HERE_API_TOKEN
    context['HERE_APP_CODE'] = settings.HERE_APP_CODE
    context['MAP_TECH'] = 'ol4'
    context['UPLOAD_FORM'] = UploadShapefileForm
    return HttpResponse(template.render(context, request))

# def sandbox(request):
#     template = loader.get_template('ucsrb/sandbox.html')
#     context = accounts_context()
#     context['title'] = 'UCSRB Sandbox'
#     return HttpResponse(template.render(context, request))
#
# def sandbox_json(request, id):
#     ta_geojson_list = []
#     geojson_response = {
#         "type": "FeatureCollection",
#         "features": []
#     }
#     tas = TreatmentArea.objects.filter(scenario__pk=id)
#     for ta in tas:
#         geojson_response['features'].append(json.loads(ta.geojson))
#
#     return JsonResponse(geojson_response)



###########################################################
###             API Calls                                 #
###########################################################

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

def build_bbox(minX, minY, maxX, maxY):
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

def create_treatment_areas(request):
    if request.method == 'GET':
        scenario_id = request.GET['scenario']
        scenario = get_feature_by_uid(scenario_id)

        final_geometry = copy(scenario.geometry_dissolved)

        # Turns out break_up_multipolygons trashes the input value: copy it!
        split_polys = break_up_multipolygons(copy(final_geometry), [])
        prescription_selection = scenario.prescription_treatment_selection
        context = {}

        # if not scenario.geometry_dissolved.num_geom > 0:
        if len(split_polys) < 1 or final_geometry.num_geom < 1:
            return get_json_error_response('Drawing does not cover any forested land in the Upper Columbia', 500, context)

        return get_scenario_treatment_areas_geojson(scenario, final_geometry, split_polys, prescription_selection, context)

def save_drawing(request):
    context = {}
    if request.method == 'POST':
        featJson = request.POST['drawing']
        scenario_name = request.POST['name']
        description = request.POST['description']
        if 'prescription_treatment_selection' in request.POST.keys():
            prescription_selection = request.POST['prescription_treatment_selection']
        else:
            prescription_selection = "flow"


        return define_scenario(request, featJson, scenario_name, description, prescription_selection)
    return get_json_error_response('Unable to save drawing.', 500, context)

def upload_treatment_shapefile(request):
    context = {}
    if request.method == 'POST':
        form = UploadShapefileForm(request.POST, request.FILES)
        if form.is_valid():
            tmp_zip_file = NamedTemporaryFile(mode='wb+',delete=True, suffix='.zip')
            for chunk in request.FILES['zipped_shapefile'].chunks():
                tmp_zip_file.write(chunk)
            tmp_zip_file.seek(0)
            projection = request.POST['shp_projection']
            geodata = GeoData()
            if projection and len(projection) > 1:
                geodata.read(tmp_zip_file.name, projection=projection)
            else:
                geodata.read(tmp_zip_file.name)

            tmp_zip_file.close()
            featJson = geodata.getUnion(format='geojson', projection='EPSG:3857')
            scenario_name = request.POST['treatment_name']
            if len(scenario_name) < 1:
                scenario_name = '.'.join(request.FILES['zipped_shapefile'].name.split('.')[:-1])
            description = request.POST['treatment_description']

            prescription_selection = request.POST['prescription_treatment_selection']

            return define_scenario(request, featJson, scenario_name, description, prescription_selection)
        else:
            message = "Errors: "
            for key in form.errors.keys():
                message += "\n %s: %s" % (key, form.errors[key])

            return get_json_error_response(message, 400, context)
    else:
        form = UploadShapefileForm()

    return render(request, 'upload_modal.html', {'UPLOAD_FORM':form})

def break_up_multipolygons(multipolygon, polygon_list=[]):
    if multipolygon.geom_type == 'MultiPolygon':
        if multipolygon.num_geom > 0:
            new_poly = multipolygon.pop()
            polygon_list = break_up_multipolygons(new_poly, polygon_list)
            polygon_list = break_up_multipolygons(multipolygon, polygon_list)
    elif multipolygon.geom_type == 'Polygon':
            polygon_list.append(multipolygon)
    return polygon_list


def define_scenario(request, featJson, scenario_name, description, prescription_selection):
    context = {}
    polys = []
    split_polys = []
    for feature in json.loads(featJson)['features']:
        geos_geom = GEOSGeometry(json.dumps(feature['geometry']))
        # GEOS assumes 4326 when given GeoJSON (by definition this should be true)
        # However, we've always used 3857, even in GeoJSON.
        # Fixing this would be great, but without comprehensive testing, it's safer
        # to perpetuate this breach of standards.
        geos_geom.srid = settings.GEOMETRY_DB_SRID
        polys.append(geos_geom)

    for poly in polys:
        split_polys = break_up_multipolygons(poly, split_polys)

    geometry = MultiPolygon(split_polys)
    layer = 'Drawing'
    focus_area = FocusArea.objects.create(unit_type=layer, geometry=geometry)
    focus_area.save()

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
            description=description,
            focus_area=True,
            focus_area_input=focus_area,
            prescription_treatment_selection=prescription_selection
        )
    except:
        # Technically we're testing for psycopg2's InternalError GEOSIntersects TopologyException
        return get_json_error_response('Treatment Areas overlap. Please review your data and start over.', 500, context)

    if not scenario.geometry_dissolved:
        return get_json_error_response('Drawing does not cover any forested land in the Upper Columbia', 500, context)
    final_geometry = scenario.geometry_dissolved


    return get_scenario_treatment_areas_geojson(scenario, final_geometry, split_polys, prescription_selection, context)

def get_scenario_treatment_areas_geojson(scenario, final_geometry, split_polys, prescription_selection, context):
    # EPSG:2163 = US National Atlas Equal Area
    final_geometry.transform(2163)
    if final_geometry.area/4046.86 < settings.MIN_TREATMENT_ACRES:
        return get_json_error_response('Treatment does not cover enough forested land to make a difference', 500, context)
    # return geometry to web mercator
    final_geometry.transform(3857)

    tas = []

    for new_ta_geom in split_polys:
        new_ta_geom.transform(3857)
        new_ta = TreatmentArea.objects.create(
            scenario=scenario,
            prescription_treatment_selection=prescription_selection,
            geometry=new_ta_geom
        )
        tas.append(new_ta)

    ta_geojson_list = []
    for ta in tas:
        ta_geojson_list.append(ta.geojson)
    geojson_response = '{"type": "FeatureCollection","features": [%s]}' % ', '.join(ta_geojson_list)

    return JsonResponse(json.loads('{"id":%s,"geojson": %s,"footprint": %s}' % (scenario.pk, geojson_response, scenario.geometry_dissolved.geojson)))


def set_treatment_prescriptions(request):
    json_response = {
        'status': 'Failed',
        'code': 500,
        'message': 'Unknown',
        'records_updated': 0,
        'records_sent': -9999
    }
    if request.method=="POST":
        try:
            received_json_data = json.loads(request.body.decode("utf-8"))
        except Exception as e:
            json_response['message'] = "Unable to read posted data. {}".format(e)
            return JsonResponse(json_response)
        if not 'treatment_prescriptions' in received_json_data.keys():
            json_response['code'] = 400
            json_response['message'] = "Required 'treatment_prescriptions' key not found in supplied JSON."
            return JsonResponse(json_response)
        json_response['records_sent'] = len(received_json_data['treatment_prescriptions'])
        for treatment in received_json_data['treatment_prescriptions']:
            ta = TreatmentArea.objects.get(pk=int(treatment['id']))
            # check treatment's Scenario's owner matches user
            if ta.scenario.user == request.user or (request.user.is_anonymous and ta.scenario.user.pk == settings.ANONYMOUS_USER_PK):
                ta.prescription_treatment_selection = treatment['prescription']
                ta.save()
                json_response['records_updated'] = json_response['records_updated']+1
            else:
                json_response['code'] = 300
                json_response['message'] = "User does not have permission to update TreatmentArea with ID: {}".format(treatment['id'])
                return JsonResponse(json_response)
        if json_response['records_updated'] > 0 and json_response['records_updated'] == json_response['records_sent']:
            # return success
            json_response['status'] = 'Success'
            json_response['code'] = 200
            json_response['message'] = "Successfully updated all TreatmentAreas"
        elif json_response['records_updated'] > 0:
            json_response['message'] = "Unknown Error: Not all records could be updated."
        elif json_response['records_updated'] == json_response['records_sent']:
            json_response['code'] = 400
            json_response['message'] = "0 records supplied for updated"
        else:
            json_response['message'] = "Unknown Error Occurred"
    else:
        json_response['code'] = 400
        json_response['message'] = 'Request Denied: Requests must be of type "POST".'
    return JsonResponse(json_response)

'''
Take a point in 3857 and return the feature at that point for a given FocusArea type
Primarily developed as a failsafe for not having pour point basin data.
'''
def get_focus_area_at(request):
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
    results = OrderedDict({})
    def get_timestamp_from_string(time_string):
        return datetime.strptime(time_string, "%m.%d.%Y-%H:%M:%S")
    for rx in flow_output.keys():
        time_keys = sorted([x for x in flow_output[rx].keys() if not x == 'records_available'], key=get_timestamp_from_string)
        if len(time_keys) > 0:
            results[rx] = [{'timestep':time_key, 'flow': flow_output[rx][time_key]} for time_key in time_keys]
    return results

def get_results_delta(flow_output):
    if type(flow_output) == OrderedDict:
        # while OrderedDict seems appropriate, the logic is written for an object with a list.
        # Rather than haveing to write and maintain to pieces of code to do the
        # same job, just convert it:
        out_dict = json.loads(json.dumps(flow_output))
    else:
        out_dict = deepcopy(flow_output)
    for treatment in out_dict.keys():
        if type(out_dict[treatment]) == dict:
            for timestep in out_dict[treatment].keys():
                baseflow = flow_output[treatment][timestep]
                for rx in out_dict.keys():
                    # be sure not to process the 'records_available' key:
                    if timestep in out_dict[rx].keys():
                        out_dict[rx][timestep] -= baseflow
            return sort_output(out_dict)
        elif type(out_dict[treatment]) == list:
            for rx in out_dict.keys():
                for index, timestep in enumerate(out_dict[rx]):
                    # Testing has shown that this logic is sound - chronological order is maintained across rx.
                    # if not flow_output['baseline'][index]['timestep'] == out_dict[rx][index]['timestep']:
                    #     print('ERROR: Mismatch Timesteps: %s --- %s' % (flow_output['baseline'][index]['timestep'], out_dict[rx][index]['timestep']))
                    baseflow = flow_output['baseline'][index]['flow']
                    out_dict[rx][index]['flow'] -= baseflow

    return out_dict

def get_results_xd_low(flow_output, sorted_results, days):
    from copy import deepcopy
    from statistics import median
    out_dict = deepcopy(flow_output)
    sept_median_x_day_low = {}
    for rx in sorted_results.keys():
        sept_list = []
        for index, treatment_result in enumerate(sorted_results[rx]):
            timestep = treatment_result['timestep']
            time_object = datetime.strptime(timestep, "%m.%d.%Y-%H:%M:%S")
            x_day_timestep_count = int(days*(24/settings.TIME_STEP_REPORTING))
            if index < x_day_timestep_count:
                flows = [x['flow'] for x in sorted_results[rx][0:x_day_timestep_count]]
            else:
                flows = [x['flow'] for x in sorted_results[rx][index-(x_day_timestep_count-1):index+1]]
            low_flow = min(float(x) for x in flows)
            out_dict[rx][timestep] = low_flow
            if time_object.month == 9:
                sept_list.append(low_flow)
        sept_median_x_day_low[rx] = median(sept_list)
    return (sort_output(out_dict), sept_median_x_day_low)

def get_results_xd_mean(flow_output, sorted_results, days):
    from copy import deepcopy
    out_dict = deepcopy(flow_output)
    for rx in sorted_results.keys():
        for index, treatment_result in enumerate(sorted_results[rx]):
            timestep = treatment_result['timestep']
            x_day_timestep_count = int(days*(24/settings.TIME_STEP_REPORTING))
            if index < x_day_timestep_count:
                flows = [x['flow'] for x in sorted_results[rx][0:x_day_timestep_count]]
            else:
                flows = [x['flow'] for x in sorted_results[rx][index-(x_day_timestep_count-1):index+1]]
            mean_flow = sum(flows)/float(len(flows))
            out_dict[rx][timestep] = mean_flow
    return sort_output(out_dict)

def parse_flow_results(overlap_basin, treatment):
    flow_results = {}
    steps_to_aggregate = settings.TIME_STEP_REPORTING/settings.TIME_STEP_HOURS

    for model_year in settings.MODEL_YEARS.keys():

        output_dict = OrderedDict({})
        annual_water_volume = {}
        sept_avg_flow = {}
        flow_results[model_year] = {}

        baseline_readings = StreamFlowReading.objects.filter(
            segment_id=overlap_basin.unit_id,
            is_baseline=True,
            time__gte=settings.MODEL_YEARS[model_year]['start'],
            time__lte=settings.MODEL_YEARS[model_year]['end'],
            ).order_by('time')
        treated_readings = StreamFlowReading.objects.filter(
            segment_id=overlap_basin.unit_id,
            treatment=treatment,
            time__gte=settings.MODEL_YEARS[model_year]['start'],
            time__lte=settings.MODEL_YEARS[model_year]['end'],
            ).order_by('time')

        for (treatment_type, readings_data) in [('baseline', baseline_readings), ('treated', treated_readings)]:
            record_count = len(readings_data)
            aggregate_volume = 0
            sept_flow = 0
            sept_records = 0
            annual_water_volume[treatment_type] = 0
            output_dict[treatment_type] = OrderedDict({})
            for index, reading in enumerate(readings_data):
                time_object = reading.time
                # Get volume of flow for timestep in Cubic Feet
                timestep_volume = reading.value * 35.3147 * settings.TIME_STEP_HOURS # readings are in m^3/hr
                aggregate_volume += timestep_volume
                annual_water_volume[treatment_type] = annual_water_volume[treatment_type] + timestep_volume
                if index%steps_to_aggregate == 0:
                    output_dict[treatment_type][reading.timestamp] = aggregate_volume/settings.TIME_STEP_REPORTING/60/60 #get ft^3/s
                    aggregate_volume = 0
                if time_object.month == 9:
                    sept_flow += timestep_volume/settings.TIME_STEP_HOURS/60/60
                    sept_records += 1
            if sept_records > 0:
                sept_avg_flow[treatment_type] = str(round(sept_flow/sept_records, 2))
            else:
                sept_avg_flow[treatment_type] = 'unknown'
            if record_count > 0:
                output_dict[treatment_type]['records_available'] = True
            else:
                output_dict[treatment_type]['records_available'] = False
        flow_results[model_year] = {
            'flow_output': output_dict,
            'annual_water_volume': annual_water_volume,
            'sept_avg_flow': sept_avg_flow
        }
    return flow_results

def calculate_basin_fc(ppt, basin_area, included_ppts, scenario=None, target_fc=-1):
    from ucsrb.models import FocusArea, PourPoint, VegPlanningUnit

    if scenario and target_fc >= 0:
        planning_units = [int(x) for x in scenario.planning_units.split(',')]
    else:
        planning_units = False

    veg_units = VegPlanningUnit.objects.filter(dwnstream_ppt_id__in=included_ppts)
    veg_fc_total = 0
    for vu in veg_units:
        if planning_units and vu.id in planning_units and vu.percent_fractional_coverage > target_fc:
            veg_fc_total += target_fc * vu.acres
        else:
            veg_fc_total += vu.percent_fractional_coverage * vu.acres
    return veg_fc_total/basin_area

def get_float_change_as_rounded_string(rx_val,baseline):
    change_val = float(rx_val) - float(baseline)
    if change_val > 0:
        return "+%s" % str(round(change_val,2))
    else:
        return str(round(change_val,2))

# NEEDS:
#   pourpoint_id
#   treatment_id
# @cache_page(60 * 60) # 1 hour of caching
def get_hydro_results_by_pour_point_id(request, year='baseline'):
    from ucsrb.models import TreatmentScenario, FocusArea, PourPoint, VegPlanningUnit
    import csv
    import time
    import os

    # start = datetime.now()
    # previous_stamp = datetime.now()
    # checkpoint = 0
    # #1
    # checkpoint += 1
    # print("Checkpoint %d: total - %d, step - %d" % (checkpoint, (datetime.now()-start).total_seconds(), (datetime.now()-previous_stamp).total_seconds()))
    # previous_stamp = datetime.now()

    # Get pourpoint_id from request or API
    pourpoint_id = request.GET.get('pourpoint_id')
    ppt = PourPoint.objects.get(id=pourpoint_id)
    # Get treatment_id from request or API
    treatment_id = request.GET.get('treatment_id')
    treatment = TreatmentScenario.objects.get(pk=treatment_id)
    overlap_basin = FocusArea.objects.filter(unit_type='PourPointOverlap', unit_id=pourpoint_id)[0]

    # RDH 09/03/2018
    # Some of the data I need is at the Overlapping Ppt Basin level, while some is aggregated to
    # the PourPointBasin, which I am discovering was calculated to the Discrete Ppt Basins.
    # Since the Discrete Ppt basins and the Overlapping ppt basins DO NOT MATCH, you will see
    # a lot of workarounds in this section.
    # If the two layers are made to match in the future this could be MUCH simpler.
    upslope_ppts = [x.id for x in PourPoint.objects.filter(geometry__intersects=overlap_basin.geometry)]
    if pourpoint_id not in upslope_ppts:
        upslope_ppts.append(pourpoint_id)
    # drainage_basins = FocusArea.objects.filter(unit_id__in=upslope_ppts, unit_type="PourPointOverlap")
    # basin_acres = sum([x.area for x in drainage_basins])
    overlap_geometry = overlap_basin.geometry
    overlap_geometry.transform(2163)
    basin_acres = round(overlap_geometry.area/4046.86, 2)
    # return geometry to web mercator
    overlap_geometry.transform(3857)

    # if ppt.imputed_ppt:
    #     imputed_ppt = ppt.imputed_ppt
    # else:
    #     imputed_ppt = PourPoint.objects.get(id=settings.DEFAULT_NN_PPT)
    #
    # if ppt == imputed_ppt:
    est_type = 'Modeled'
    # else:
    #     est_type = 'Imputed'
    # impute_id = str(imputed_ppt.pk)
    impute_id = ppt.id

    # results_csvs = OrderedDict({})
    # results_csvs['baseline'] = os.path.join(settings.NN_DATA_DIR,"veg%s" % imputed_ppt.watershed_id,"_base","%s.csv" % imputed_ppt.streammap_id)
    # (results_csvs['reduce to 50'], rx_50) = get_flow_csv_match(imputed_ppt, rx_fc_pct_delta['reduce to 50'])
    # (results_csvs['reduce to 30'], rx_30) = get_flow_csv_match(imputed_ppt, rx_fc_pct_delta['reduce to 30'])
    # (results_csvs['reduce to 0'], rx_0) = get_flow_csv_match(imputed_ppt, rx_fc_pct_delta['reduce to 0'])

    # (flow_output, annual_water_volume, sept_avg_flow) = parse_flow_results(overlap_basin, treatment)
    flow_results = parse_flow_results(overlap_basin, treatment)

    flow_output = flow_results[year]['flow_output']
    annual_water_volume = flow_results[year]['annual_water_volume']
    sept_avg_flow = flow_results[year]['sept_avg_flow']

    # TUNING: For large basins, this can take over 1 minute to run.
    basin_fractional_coverage = {
        'baseline': calculate_basin_fc(ppt, basin_acres, upslope_ppts),
        # 'treated': calculate_basin_fc(ppt, basin_acres, upslope_ppts, treatment, treatment_id)

        # 'reduce to 50': calculate_basin_fc(ppt, basin_acres, upslope_ppts, treatment, 50),
        # 'reduce to 30': calculate_basin_fc(ppt, basin_acres, upslope_ppts, treatment, 30),
        # 'reduce to 0': calculate_basin_fc(ppt, basin_acres, upslope_ppts, treatment, 0)
    }

    rx_fc_pct_delta = {}
    rx_fc_delta = {}
    # for rx in ['reduce to 50', 'reduce to 30', 'reduce to 0']:
    for rx in [x for x in basin_fractional_coverage.keys() if not x == 'baseline']:
        if basin_fractional_coverage['baseline'] == 0:
            rx_fc_delta[rx] = 0
            rx_fc_pct_delta[rx] = 0
        else:
            rx_fc_delta[rx] = basin_fractional_coverage['baseline'] - basin_fractional_coverage[rx]
            rx_fc_pct_delta[rx] = rx_fc_delta[rx]/basin_fractional_coverage['baseline']*100


    # Baseline water yield (bas_char)
    # Cubic Feet per year (annual volume) / Square Feet (basin area) * 12 (inches/foot) = x inches/year
    baseline_water_yield = str(round(annual_water_volume['baseline']/(basin_acres*43560)*12, 2))
    # Average Annual Flow: Total flow in cubic feet divided by seconds in year - assume year is not Leap.
    avg_flow_results = {
        'baseline': str(round(annual_water_volume['baseline']/(365*24*60*60), 2))
    }
    for treatment_type in annual_water_volume.keys():
        if not treatment_type == 'baseline' and flow_output[treatment_type]['records_available']:
            avg_flow_results[treatment_type] = str(round(annual_water_volume[treatment_type]/(365*24*60*60), 2))
    # r50_average_flow = str(round(annual_water_volume['reduce to 50']/(365*24*60*60), 2))
    # r30_average_flow = str(round(annual_water_volume['reduce to 30']/(365*24*60*60), 2))
    # r0_average_flow = str(round(annual_water_volume['reduce to 0']/(365*24*60*60), 2))

    absolute_results = sort_output(flow_output)

    #   delta flow
    delta_results = get_results_delta(flow_output)

    #   7-day low-flow (needs sort_by_time)
    (seven_d_low_results, sept_median_7_day_low) = get_results_xd_low(flow_output, absolute_results, 7)
    #   1-day low-flow
    (one_d_low_results, sept_median_1_day_low) = get_results_xd_low(flow_output, absolute_results, 1)

    seven_d_mean_results = get_results_xd_mean(flow_output, absolute_results, 7)
    one_d_mean_results = get_results_xd_mean(flow_output, absolute_results, 1)

    delta_1_d_low_results = get_results_delta(one_d_low_results)
    delta_1_d_mean_results = get_results_delta(one_d_mean_results)
    delta_7_d_low_results = get_results_delta(seven_d_low_results)
    delta_7_d_mean_results = get_results_delta(seven_d_mean_results)

    charts = [
        {'title': 'Absolute Flow Rate','data': absolute_results},
        {'title': 'Seven Day Low Flow','data': seven_d_low_results},
        {'title': 'Seven Day Mean Flow','data': seven_d_mean_results},
        {'title': 'One Day Low Flow','data': one_d_low_results},
        {'title': 'One Day Mean Flow','data': one_d_mean_results},
        {'title': 'Change in Flow Rate','data': delta_results},
        {'title': 'Change in 7 Day Low Flow Rate','data': delta_7_d_low_results},
        {'title': 'Change in 7 Day Mean Flow Rate','data': delta_7_d_mean_results},
        {'title': 'Change in 1 Day Low Flow Rate','data': delta_1_d_low_results},
        {'title': 'Change in 1 Day Mean Flow Rate','data': delta_1_d_mean_results},
    ]

    bas_char_data = []
    bas_char_data.append({'key': 'Total area upslope of this gauging station', 'value': basin_acres, 'unit': 'acres' })
    vus = VegPlanningUnit.objects.filter(dwnstream_ppt_id__in=upslope_ppts)
    acres_forested = int(sum([x.acres for x in vus]))
    bas_char_data.append({'key': 'Total forested area upslope', 'value': acres_forested, 'unit': 'acres' })
    # bas_char_data.append({'key': 'Percent Forested', 'value': int(acres_forested/basin_acres*100), 'unit': '%' })
    bas_char_data.append({'key': 'Baseline water yield', 'value': baseline_water_yield, 'unit': 'inches/year' })
    bas_char_data.append({'key': 'Baseline average annual flow', 'value': avg_flow_results['baseline'], 'unit': 'CFS' })
    bas_char_data.append({'key': 'Baseline September mean flow', 'value': sept_avg_flow['baseline'], 'unit': 'CFS' })
    bas_char_data.append({'key': 'Baseline September median 7 day avg low flow', 'value': round(sept_median_7_day_low['baseline'], 2), 'unit': 'CFS' })

    hydro_char_data = []
    hydro_char_data.append({'key': '<b>Change in average annual flow from proposed management</b>', 'value': '', 'unit': '' })
    for treatment_type in avg_flow_results.keys():
        if not treatment_type == 'baseline':
            treatment_type_change = get_float_change_as_rounded_string(avg_flow_results[treatment_type],avg_flow_results['baseline'])
            hydro_char_data.append({'key': '&nbsp;&nbsp;&nbsp;&nbsp;- %s' % treatment_type, 'value': treatment_type_change, 'unit': 'CFS' }) #Baseline annl flow - 50 annl flow

    # r50_change = get_float_change_as_rounded_string(r50_average_flow,avg_flow_results['baseline'])
    # hydro_char_data.append({'key': '&nbsp;&nbsp;&nbsp;&nbsp;- Reducing fractional coverage to 50%', 'value': r50_change, 'unit': 'CFS' }) #Baseline annl flow - 50 annl flow
    # r30_change = get_float_change_as_rounded_string(r30_average_flow,avg_flow_results['baseline'])
    # hydro_char_data.append({'key': '&nbsp;&nbsp;&nbsp;&nbsp;- Reducing fractional coverage to 30%', 'value': r30_change, 'unit': 'CFS' }) #Baseline annl flow - 30 annl flow
    # r0_change = get_float_change_as_rounded_string(r0_average_flow,avg_flow_results['baseline'])
    # hydro_char_data.append({'key': '&nbsp;&nbsp;&nbsp;&nbsp;- Reducing fractional coverage to 0%', 'value': r0_change, 'unit': 'CFS' }) #Baseline annl flow - 0 annl flow

    hydro_char_data.append({'key': '<b>Change in average September flow from proposed management </b>', 'value': '', 'unit': '' })
    for treatment_type in [x for x in sept_avg_flow.keys() if not x == 'baseline']:
        if flow_output[treatment_type]['records_available']:
            treatment_type_sept_avg_change = get_float_change_as_rounded_string(sept_avg_flow[treatment_type],sept_avg_flow['baseline'])
        else:
            treatment_type_sept_avg_change = 'Data not yet available'
        hydro_char_data.append({'key': '&nbsp;&nbsp;&nbsp;&nbsp;- %s' % treatment_type, 'value': treatment_type_sept_avg_change, 'unit': 'CFS' })

        # r50_sept_avg_change = get_float_change_as_rounded_string(sept_avg_flow['reduce to 50'],sept_avg_flow['baseline'])
        # hydro_char_data.append({'key': '&nbsp;&nbsp;&nbsp;&nbsp;- Reducing fractional coverage to 50%', 'value': r50_sept_avg_change, 'unit': 'CFS' }) #Baseline sept flow - 50 sept flow
        # r30_sept_avg_change = get_float_change_as_rounded_string(sept_avg_flow['reduce to 30'],sept_avg_flow['baseline'])
        # hydro_char_data.append({'key': '&nbsp;&nbsp;&nbsp;&nbsp;- Reducing fractional coverage to 30%', 'value': r30_sept_avg_change, 'unit': 'CFS' }) #Baseline sept flow - 30 sept flow
        # r0_sept_avg_change = get_float_change_as_rounded_string(sept_avg_flow['reduce to 0'],sept_avg_flow['baseline'])
        # hydro_char_data.append({'key': '&nbsp;&nbsp;&nbsp;&nbsp;- Reducing fractional coverage to 0%', 'value': r0_sept_avg_change, 'unit': 'CFS' }) #Baseline sept flow - 0 sept flow

    hydro_char_data.append({'key': '<b>Change in Sept. 7-day low flow from proposed management </b>', 'value': '', 'unit': '' })
    for treatment_type in [x for x in sept_median_7_day_low.keys() if not x == 'baseline']:
        treatment_type_sept_7_day_low_diff = get_float_change_as_rounded_string(sept_median_7_day_low[treatment_type],sept_median_7_day_low['baseline'])
        hydro_char_data.append({'key': '&nbsp;&nbsp;&nbsp;&nbsp;- %s' % treatment_type, 'value': treatment_type_sept_7_day_low_diff, 'unit': 'CFS' })
    # r50_sept_7_day_low_diff = get_float_change_as_rounded_string(sept_median_7_day_low['reduce to 50'],sept_median_7_day_low['baseline'])
    # hydro_char_data.append({'key': '&nbsp;&nbsp;&nbsp;&nbsp;- Reducing fractional coverage to 50%', 'value': r50_sept_7_day_low_diff, 'unit': 'CFS' }) #Baseline sept flow - 50 sept flow
    # r30_sept_7_day_low_diff = get_float_change_as_rounded_string(sept_median_7_day_low['reduce to 30'],sept_median_7_day_low['baseline'])
    # hydro_char_data.append({'key': '&nbsp;&nbsp;&nbsp;&nbsp;- Reducing fractional coverage to 30%', 'value': r30_sept_7_day_low_diff, 'unit': 'CFS' }) #Baseline sept flow - 30 sept flow
    # r0_sept_7_day_low_diff = get_float_change_as_rounded_string(sept_median_7_day_low['reduce to 0'],sept_median_7_day_low['baseline'])
    # hydro_char_data.append({'key': '&nbsp;&nbsp;&nbsp;&nbsp;- Reducing fractional coverage to 0%', 'value': r0_sept_7_day_low_diff, 'unit': 'CFS' }) #Baseline sept flow - 0 sept flow

    prop_mgmt_data = []
    basin_veg_units = treatment.veg_units.filter(geometry__intersects=overlap_basin.geometry) #within may be more accurate, but slower
    treatment_acres = sum([x.acres for x in basin_veg_units])
    prop_mgmt_data.append({'key': 'Total forested area in proposed treatment', 'value': int(treatment_acres), 'unit': 'acres' })
    prop_mgmt_data.append({'key': '<b>Reduction in avg fractional coverage from proposed management</b>', 'value': '', 'unit': '' })
    for treatment_type in [x for x in rx_fc_delta.keys() if not x == 'baseline']:
        prop_mgmt_data.append({'key': '&nbsp;&nbsp;&nbsp;&nbsp;- %s' % treatment_type, 'value': str(round(rx_fc_delta[treatment_type],2)), 'unit': '%' })
    # prop_mgmt_data.append({'key': '&nbsp;&nbsp;&nbsp;&nbsp;- Reducing fractional coverage to 50%', 'value': str(round(rx_fc_delta['reduce to 50'],2)), 'unit': '%' }) #Baseline avg fc - 50 avg fc
    # prop_mgmt_data.append({'key': '&nbsp;&nbsp;&nbsp;&nbsp;- Reducing fractional coverage to 30%', 'value': str(round(rx_fc_delta['reduce to 30'],2)), 'unit': '%' }) #Baseline avg fc - 30 avg fc
    # prop_mgmt_data.append({'key': '&nbsp;&nbsp;&nbsp;&nbsp;- Reducing fractional coverage to 0%', 'value': str(round(rx_fc_delta['reduce to 0'],2)), 'unit': '%' }) #Baseline avg fc - 0 avg fc

    # flow_est_data = []
    # flow_est_data.append({'key': 'Estimation Type','value': est_type,'unit': ''})
    # if settings.DEBUG:
    #     flow_est_data.append({'key': 'Imputed ppt_ID','value': impute_id,'unit': ''})
    #     flow_est_data.append({'key': 'Imputed veg mgmt scenario (50)','value': rx_50,'unit': ''})
    #     flow_est_data.append({'key': 'Imputed veg mgmt scenario (30)','value': rx_30,'unit': ''})
    #     flow_est_data.append({'key': 'Imputed veg mgmt scenario (0)','value': rx_0,'unit': ''})
    # if ppt.confidence > 9:
    #     confidence = 'NA'
    # elif ppt.confidence > 6:
    #     confidence = 'extremely high'
    # elif ppt.confidence > 4:
    #     confidence = 'high'
    # elif ppt.confidence > 2:
    #     confidence = 'moderate'
    # elif ppt.confidence > 1:
    #     confidence = 'low'
    # else:
    #     confidence = 'extremely low'
    # flow_est_data.append({'key': 'Baseline Confidence', 'value': confidence, 'unit': ''})
    # flow_est_data.append({'key': 'Change in Flow Confidence', 'value': "TBD", 'unit': '%'})

    summary_reports = []
    # if settings.DEBUG:
    #     summary_reports.append(
    #         {
    #             'title': 'Debug Data',
    #             'data': [
    #                 {'key': 'Gauging station ID', 'value': pourpoint_id, 'unit': ''},
    #                 # {'key': 'Overlap Basin Area', 'value': basin_acres, 'unit': 'Acres'},
    #                 # {'key': 'Agg. Ppt Basin Area', 'value': agg_ppt_basin_acres, 'unit': 'Acres'},
    #                 {'key': 'Agg. Ppt Basin Area', 'value': basin_acres, 'unit': 'Acres'},
    #             ]
    #         }
    #     )
    summary_reports.append({'title': 'Basin Characteristics','data': bas_char_data})
    summary_reports.append({'title': 'Hydrologic Characteristics','data': hydro_char_data})
    summary_reports.append({'title': 'Proposed Management','data': prop_mgmt_data})
    # summary_reports.append({'title': 'Flow Estimation Confidence','data': flow_est_data})

    results = [
        {
            'type': 'Summary',
            'reports': summary_reports
        },
        {
            'type': 'charts',
            'reports' : charts
         }
    ]

    return JsonResponse({
        'results': results, # TODO: Support 3 years in Hydro reports
        'basin': overlap_basin.geometry.json
    })

@cache_page(60 * 60) # 1 hour of caching
def get_results_by_scenario_id(request):
    from ucsrb.models import TreatmentScenario, FocusArea, PourPoint

    scenario_id = request.GET.get('id')
    export = request.GET.get('export')
    try:
        treatment = get_feature_by_uid(scenario_id)
    except:
        return get_json_error_response('Treatment with given ID (%s) does not exist' % scenario_id, 500, {})

    veg_units = treatment.veg_units
    impacted_pourpoint_ids = list(set([x.dwnstream_ppt_id for x in veg_units]))
    intermediate_downstream_ppts = PourPoint.objects.filter(id__in=impacted_pourpoint_ids)

    # imputation_ids = []
    # for lookup in ScenarioNNLookup.objects.all():
    #     if lookup.ppt_id not in imputation_ids:
    #         imputation_ids.append(lookup.ppt_id)

    # RDH: Again, some ppts we thought we had modeled, but couldn't - A few of those we couldn't even impute, so skip 'em.
    # imputation_ids = [x for x in imputation_ids if x not in settings.PROBLEMATIC_POUR_POINTS]
    # viable_reporting_ppt_ids = [x.id for x in PourPoint.objects.filter(imputed_ppt__in=imputation_ids)]
    viable_reporting_ppt_ids = [x.id for x in intermediate_downstream_ppts]

    overlap_basins = FocusArea.objects.filter(unit_type='PourPointOverlap', unit_id__in=viable_reporting_ppt_ids)
    for ppt in intermediate_downstream_ppts:
        overlap_basins = overlap_basins.filter(geometry__intersects=ppt.geometry)

    reportable_ppts = list(set(viable_reporting_ppt_ids).intersection(impacted_pourpoint_ids))
    try:
        containing_basin = sorted(overlap_basins, key= lambda x: x.geometry.area)[0]
        reportable_ppts.append(containing_basin.unit_id)
    except:
        # In case there are no reportable downstream ppts.
        pass

    downstream_ppts = PourPoint.objects.filter(id__in=reportable_ppts)

    if export:
        print("Export %s" % export)
    else:
        if treatment.job_status == 'None' or treatment.aggregate_report is None or len(treatment.aggregate_report) == 0:
            treatment.set_report()
            if treatment.aggregate_report is None or len(treatment.aggregate_report) == 0:
                treatment = get_feature_by_uid(scenario_id)

        # draw/upload seems to have aggregate_report as a string, while
        # filter wizard sets/gets it as object. This is bad, but for now,
        # we'll just cast to a string.
        aggregate_results = eval(str(treatment.aggregate_report))

        return_json = {
            'scenario': {
                'name': treatment.name,
                'acres': aggregate_results['total_acres']
            },
            'aggregate_results': aggregate_results['results_list'],
            'pourpoints': [ {'id': x.pk, 'name': '', 'geometry': json.loads(x.geometry.json) } for x in downstream_ppts ],
            'focus_area': json.loads(treatment.focus_area_input.geometry.json),
            'treatment_areas': json.loads(treatment.treatment_areas_geojson())
        }
        return JsonResponse(return_json)

def get_results_by_state(request):
    return_json = {
        'response': 'TODO :('
    }
    return JsonResponse(return_json)

def get_last_flow_line(flow_outfile):
    # quick 'get last line' code modified from Eugene Yarmash:
    #   https://stackoverflow.com/a/54278929
    with open(flow_outfile, 'rb') as f:
        f.seek(-2, os.SEEK_END)
        newline_found = False  # since last_line may still be being written, 2nd-to-last will have to do.
        current_set = f.read(1)
        while current_set != b'\n' or not newline_found:
            if current_set == b'\n':
                newline_found = True
            f.seek(-2, os.SEEK_CUR)
            current_set = f.read(1)
        last_line = f.readline().decode()
    return last_line

def get_status_by_scenario_id(request):
    from ucsrb.models import TreatmentScenario, FocusArea, PourPoint

    scenario_id = request.GET.get('id')
    try:
        treatment = get_feature_by_uid(scenario_id)
    except:
        return get_json_error_response('Treatment with given ID (%s) does not exist' % scenario_id, 500, {})

    progress = 0
    model_progress = 0
    import_progress = 0
    task_status = 'Initializing (1/4)'

    error = 'None'
    last_line = ''

    if treatment.job_status == 'None':
        task_status = 'Queued (0/4)'
    elif treatment.job_status != 'SUCCESS':
        # Attempt to re-run the job - if job is too new, it won't restart, just continue
        treatment.run_dhsvm()
        # check out /tmp/runs/run_{id}/output/Streamflow.only
        flow_outfile = "/tmp/runs/run_{}/output/Streamflow.Only".format(treatment.id)
        if Path(flow_outfile).exists():

            try:
                last_line = get_last_flow_line(flow_outfile)

                [month, day, year] = last_line.split('-')[0].split('.')[0:3]
                model_time = last_line.split(' ')[0].split('-')[1]
                model_progress_date = datetime.strptime("{}.{}.{}-{}".format(month, day, year, model_time), "%m.%d.%Y-%H:%M:%S")
                model_year_type = settings.MODEL_YEAR_LOOKUP[str(year)]
                model_year = settings.MODEL_YEARS[model_year_type]
                total_time = model_year['end'] - model_year['start']
                completed_time = model_progress_date - model_year['start']
                model_progress = (completed_time.total_seconds()/total_time.total_seconds())*100/2   #50% of the progress is modelling, so /2
                task_status = 'Modelling (2/4)'
            except (ValueError, IndexError) as e:
                # Streamflow file doesn't have 2 complete entries yet.
                error = str(e)
                print(e)
                pass
            except OSError as e:
                # Streamflow file empty
                pass

            import_status_file = "/tmp/runs/run_{}/output/dhsvm_status.log".format(treatment.id)
            if Path(import_status_file).exists():
                task_status = 'Importing (3/4)'
                with open(import_status_file, 'r') as f:
                    inlines=f.readlines()
                    import_progress = int(inlines[-1])/2

        progress = round(model_progress) + round(import_progress)
    else:
        task_status = 'Complete'
        progress = 100

    try:
        job_age = treatment.job_age.total_seconds()
    except AttributeError as e:
        job_age = 0

    # MAX_ACTIVE_JOB_AGE
    return_json = {
        'status': 'Status: {}'.format(task_status),
        'progress': progress,
        'age': job_age,
        'error': error,
        'last_line': last_line
    }
    return JsonResponse(return_json)

'''
'''
def run_filter_query(filters):
    from ucsrb.models import VegPlanningUnit, FocusArea, PourPoint
    # TODO: This would be nicer if it generically knew how to filter fields
    # by name, and what kinds of filters they were. For now, hard code.
    notes = []

    filter_dict = {}
    exclude_dicts = []

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
        exclude_dicts.append({'pub_priv_own__icontains':'private'})   # real value is 'Private land'

    if 'pub_priv_own' in filters.keys() and filters['pub_priv_own']:
        if 'pub_priv_own_input' in filters.keys():
            filter_dict['pub_priv_own__iexact'] = filters['pub_priv_own_input']

    if 'lsr_percent' in filters.keys() and filters['lsr_percent']:
        filter_dict['lsr_percent__lt'] = settings.LSR_THRESHOLD

    if 'has_critical_habitat' in filters.keys() and filters['has_critical_habitat']:
        filter_dict['percent_critical_habitat__lt'] = settings.CRIT_HAB_THRESHOLD
        exclude_dicts.append({'has_critical_habitat':True})

    # if 'area' in filters.keys() and filters['area']:
    #     # RDH 1/8/18: filter(geometry__area_range(...)) does not seem available.
    #     # query = query.filter(geometry__area__range=(filters['area_min'], filters['area_max']))
    #
    #     # RDH 1/9/18: Why can't we use the model's 'Run Filters' function?
    #     # RDH 1/26/18: Because the model object doesn't exist yet.
    #     pu_ids = [pu.pk for pu in query if pu.geometry.area <= float(filters['area_max']) and pu.geometry.area>= float(filters['area_min'])]
    #     query = (query.filter(pk__in=pu_ids))

    # if 'percent_roadless' in filters.keys() and filters['percent_roadless']:
    #     filter_dict['percent_roadless__lt'] = settings.ROADLESS_THRESHOLD

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

    if 'has_burned' in filters.keys() and filters['has_burned']:
        exclude_dicts.append({'has_burned':True})

    if 'has_wilderness_area' in filters.keys() and filters['has_wilderness_area']:
        exclude_dicts.append({'has_wilderness_area':True})

    exclusion_list = []
    if 'landform_type' in filters.keys() and filters['landform_type']:
        if not 'landform_type_checkboxes_0' in filters.keys():
            if not 'landform_type_include_north' in filters.keys() or not filters['landform_type_include_north']:
                exclusion_list += [12, 22]
        if not 'landform_type_checkboxes_1' in filters.keys():
            if not 'landform_type_include_south' in filters.keys() or not filters['landform_type_include_south']:
                exclusion_list += [13, 23]
        if not 'landform_type_checkboxes_2' in filters.keys():
            if not 'landform_type_include_ridgetop' in filters.keys() or not filters['landform_type_include_ridgetop']:
                exclusion_list += [11, 21]
        if not 'landform_type_checkboxes_3' in filters.keys():
            if not 'landform_type_include_floors' in filters.keys() or not filters['landform_type_include_floors']:
                exclusion_list += [14, 24]
        if not 'landform_type_checkboxes_4' in filters.keys():
            if not 'landform_type_include_east_west' in filters.keys() or not filters['landform_type_include_east_west']:
                exclusion_list += [15, 25]
        if len(exclusion_list) > 0:
            exclude_dicts.append({'topo_height_class_majority__in':exclusion_list})
            # query = query.exclude(topo_height_class_majority__in=exclusion_list)

    query = VegPlanningUnit.objects.filter(**filter_dict)
    # We want all exclusions in 'exclude_dict' to be applied independently, not only excluding items that match all
    for exclude_dict in exclude_dicts:
        query = query.exclude(**exclude_dict)

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
    count = query.count()
    area_acres = 0
    for pu in query:
        area_acres += pu.acres

    return HttpResponse("%d acres" % int(area_acres), status=200)

'''
'''
@cache_page(60 * 60) # 1 hour of caching
def get_filter_results(request, query=False, notes=[]):
    if not query:
        filter_dict = parse_filter_checkboxes(request)
        (query, notes) = run_filter_query(filter_dict)
    area_acres = 0
    for pu in query:
        area_acres += pu.acres
    from scenarios import views as scenarioViews
    return scenarioViews.get_filter_results(request, query, notes, {'area_acres': area_acres})

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
            # 'percent_roadless': p_unit.percent_roadless,
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
            'topo_height_class_majority': p_unit.topo_height_class_majority,
            'has_burned': p_unit.has_burned,
            'has_wilderness_area': p_unit.has_wilderness_area
        })
    return HttpResponse(dumps(json))

def get_scenarios(request, scenario_model='treatmentscenario'):
    from scenarios.views import get_scenarios as scenarios_get_scenarios
    return scenarios_get_scenarios(request, scenario_model, 'ucsrb')

def demo(request, template='ucsrb/demo.html'):
    from scenarios import views as scenarios_views
    return scenarios_views.demo(request, template)
