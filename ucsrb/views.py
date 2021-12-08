# Create your views here.
from collections import OrderedDict
from copy import deepcopy, copy
from datetime import datetime
from humanize import intcomma
import time
import json
import os
from pathlib import Path
import zipfile

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

def claim_treatment_area(request):
    json_response = {
        'status': 'Failed',
        'code': 500,
        'message': 'Unknown.',
    }
    try:
        scenario_id = request.GET['scenario']
        scenario = get_feature_by_uid('ucsrb_treatmentscenario_{}'.format(scenario_id))
        user = request.user
        anon_user = User.objects.get(pk=settings.ANONYMOUS_USER_PK)
        if user.is_authenticated and scenario and scenario.user == anon_user:
            scenario.user = user
            scenario.save()
        elif not user.is_authenticated:
            json_response['code'] = 300
            json_response['message'] = 'User is not authenticated.'
            return JsonResponse(json_response)
        elif not scenario:
            json_response['code'] = 400
            json_response['message'] = 'Treatment Scenario not found.'
            return JsonResponse(json_response)
        elif not scenario.user == anon_user:
            json_response['code'] = 300
            json_response['message'] = 'Treatment Scenario is owned by another user.'
            return JsonResponse(json_response)

        json_response['status'] = 'Success'
        json_response['code'] = 200

    except Exception as e:
        json_response['message'] = '{}.'.format(e)

    return JsonResponse(json_response)

def login_check(request):
    json_response = {
        'status': 'Failed',
        'code': 500,
        'message': 'Unknown.',
        'is_authenticated': False
    }
    user = request.user
    return JsonResponse({
        'status': 'Success',
        'code': 200,
        'message': None,
        'is_authenticated': user.is_authenticated,
    })

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

def clean_zip_file(tmp_zip_file):
    is_clean = False
    zipname = tmp_zip_file.name
    if zipfile.is_zipfile(zipname):
        zip = zipfile.ZipFile(zipname)
        if len([x for x in zip.namelist() if '/' in x]) > 0:
            new_tmp_zip = NamedTemporaryFile(mode='w+',delete=True, suffix='.zip')
            outzip = zipfile.ZipFile(new_tmp_zip.name, 'w')
            file_parts = [(x.split('/')[-1], zip.read(x)) for x in zip.namelist()]
            for part in file_parts:
                try:
                    outzip.writestr(part[0],part[1])
                    if '.shp' in part[0]:
                        is_clean=True
                except IndexError as e:
                    # weird error from zipfile.py line 1792 in writestr
                    pass
            outzip.close()
            tmp_zip_file.close()
            tmp_zip_file = new_tmp_zip
        else:
            is_clean = True

    return (tmp_zip_file, is_clean)

def upload_treatment_shapefile(request):
    context = {}
    if request.method == 'POST':
        form = UploadShapefileForm(request.POST, request.FILES)
        if form.is_valid():
            tmp_zip_file = NamedTemporaryFile(mode='wb+',delete=True, suffix='.zip')
            for chunk in request.FILES['zipped_shapefile'].chunks():
                tmp_zip_file.write(chunk)
            tmp_zip_file.seek(0)
            (tmp_zip_file, is_clean) = clean_zip_file(tmp_zip_file)
            if is_clean:
                try:
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
                except Exception as e:
                    message = "Error when attempting to read provided shapefile: {}".format(e)
                    return get_json_error_response(message, 400, context)
            else:
                message = "Error: Unable to read provided file. Be sure you upload a zipfile (.zip) that contains a .shp, .dbf, etc..."
                return get_json_error_response(message, 400, context)
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

    focus_area.geometry.transform(2163)
    treatment_acres = int(round(focus_area.geometry.area/4046.86, 0))
    # return geometry to web mercator
    focus_area.geometry.transform(3857)
    if treatment_acres > settings.MAX_TREATMENT_ACRES:
        return get_json_error_response('Treatment is too large ({} acres). Please keep it under {} acres.'.format(intcomma(treatment_acres), intcomma(settings.MAX_TREATMENT_ACRES)))

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
    except Exception as e:
        # Technically we're testing for psycopg2's InternalError GEOSIntersects TopologyException
        return get_json_error_response('Unexpected error: "{}". This could be the result of trying to treat entirely in a designated Wilderness, please review your data to ensure you include a portion that is outside the Wilderness and start over.'.format(e), 500, context)

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
        results[rx] = {}
        for treatment in flow_output[rx].keys():
            time_keys = sorted([x for x in flow_output[rx][treatment].keys() if not x == 'records_available'], key=get_timestamp_from_string)
            if len(time_keys) > 0:
                results[rx][treatment] = [{'timestep':time_key, 'flow': flow_output[rx][treatment][time_key]} for time_key in time_keys]
    return results

def get_results_delta(flow_output):
    if type(flow_output) == OrderedDict:
        # while OrderedDict seems appropriate, the logic is written for an object with a list.
        # Rather than haveing to write and maintain to pieces of code to do the
        # same job, just convert it:
        out_dict = json.loads(json.dumps(flow_output))
    else:
        out_dict = deepcopy(flow_output)

    if type(out_dict[settings.NORMAL_YEAR_LABEL][settings.TREATED_LABEL]) in [dict, OrderedDict]:
        # flow_results
        for weather_year in out_dict.keys():
            for timestep in out_dict[weather_year][settings.TREATED_LABEL].keys():
                baseflow = flow_output[weather_year][settings.UNTREATED_LABEL][timestep]
                for rx in out_dict[weather_year].keys():
                    # be sure not to process the 'records_available' key:
                    if timestep in out_dict[weather_year][rx].keys():
                        out_dict[weather_year][rx][timestep] -= baseflow
        return sort_output(out_dict)
    elif type(out_dict[settings.NORMAL_YEAR_LABEL][settings.TREATED_LABEL]) == list:
        # previously-deltaed data
        for weather_year in out_dict.keys():
            for treatment in out_dict[weather_year].keys():
                for index, timestep in enumerate(out_dict[weather_year][treatment]):
                    # Testing has shown that this logic is sound - chronological order is maintained across treatment.
                    baseflow = flow_output[weather_year][settings.UNTREATED_LABEL][index]['flow']
                    out_dict[weather_year][treatment][index]['flow'] -= baseflow

    return out_dict

def get_results_xd_low(flow_output, sorted_results, days):
    from copy import deepcopy
    from statistics import median
    out_dict = deepcopy(flow_output)
    sept_median_x_day_low = {}

    for rx in sorted_results.keys():
        sept_median_x_day_low[rx] = {}
        for treatment in sorted_results[rx].keys():
            sept_list = []
            for index, treatment_result in enumerate(sorted_results[rx][treatment]):
                timestep = treatment_result['timestep']
                time_object = datetime.strptime(timestep, "%m.%d.%Y-%H:%M:%S")
                x_day_timestep_count = int(days*(24/settings.TIME_STEP_REPORTING))
                if index < x_day_timestep_count:
                    flows = [x['flow'] for x in sorted_results[rx][treatment][0:x_day_timestep_count]]
                else:
                    flows = [x['flow'] for x in sorted_results[rx][treatment][index-(x_day_timestep_count-1):index+1]]
                low_flow = min(float(x) for x in flows)
                out_dict[rx][treatment][timestep] = low_flow
                if time_object.month == 9:
                    sept_list.append(low_flow)
            sept_median_x_day_low[rx][treatment] = median(sept_list)

    return (sort_output(out_dict), sept_median_x_day_low)

def get_results_xd_mean(flow_output, sorted_results, days):
    from copy import deepcopy
    out_dict = deepcopy(flow_output)
    for rx in sorted_results.keys():
        for treatment in sorted_results[rx].keys():
            for index, treatment_result in enumerate(sorted_results[rx][treatment]):
                timestep = treatment_result['timestep']
                x_day_timestep_count = int(days*(24/settings.TIME_STEP_REPORTING))
                if index < x_day_timestep_count:
                    flows = [x['flow'] for x in sorted_results[rx][treatment][0:x_day_timestep_count]]
                else:
                    flows = [x['flow'] for x in sorted_results[rx][treatment][index-(x_day_timestep_count-1):index+1]]
                mean_flow = sum(flows)/float(len(flows))
                out_dict[rx][treatment][timestep] = mean_flow
    return sort_output(out_dict)

def parse_flow_results(overlap_basin, treatment):
    flow_results = {}
    steps_to_aggregate = settings.TIME_STEP_REPORTING/settings.TIME_STEP_HOURS

    for model_year in settings.MODEL_YEARS.keys():

        output_dict = OrderedDict({})
        annual_water_volume = {}
        sept_avg_flow = {}
        flow_results[model_year] = {}

        flow_data_tuples = []

        # We only draw the 'untreated baseline' year, not 'untreated wet/dry' years.
        # if model_year == settings.NORMAL_YEAR_LABEL:
        baseline_readings = StreamFlowReading.objects.filter(
            segment_id=overlap_basin.unit_id,
            is_baseline=True,
            time__gte=settings.MODEL_YEARS[model_year]['start'],
            time__lte=settings.MODEL_YEARS[model_year]['end'],
            )
        flow_data_tuples.append((settings.UNTREATED_LABEL, baseline_readings))
        # else:
        #     flow_data_tuples.append((settings.UNTREATED_LABEL, []))

        treated_readings = StreamFlowReading.objects.filter(
            segment_id=overlap_basin.unit_id,
            treatment=treatment,
            time__gte=settings.MODEL_YEARS[model_year]['start'],
            time__lte=settings.MODEL_YEARS[model_year]['end'],
            )

        # flow_data_tuples.append((model_year, treated_readings))
        flow_data_tuples.append((settings.TREATED_LABEL, treated_readings))

        for (treatment_type, readings_data) in flow_data_tuples:
            aggregate_volume = 0
            sept_flow = 0
            sept_records = 0
            annual_water_volume[treatment_type] = 0
            output_dict[treatment_type] = OrderedDict({})
            record_count = 0
            try:
                readings_data = readings_data.order_by('time')
            except AttributeError as e:
                # we use empty lists when no query was made.
                pass
            for index, reading in enumerate(list(readings_data)):
                record_count += 1
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

def get_float_change_as_rounded_string(rx_val,baseline):
    change_val = float(rx_val) - float(baseline)
    if change_val > 0:
        return "+%s" % str(round(change_val,2))
    else:
        return str(round(change_val,2))


def absolute_chart(chart_data):
    # out_chart = OrderedDict({})
    if settings.OVERRIDE_UNTREATED_CHART_LABEL:
        chart_untreated_label = settings.OVERRIDE_UNTREATED_CHART_LABEL
    else:
        chart_untreated_label = settings.UNTREATED_LABEL
    out_chart = {}
    out_chart[chart_untreated_label] = chart_data[settings.NORMAL_YEAR_LABEL][settings.UNTREATED_LABEL]
    out_chart[settings.DRY_YEAR_LABEL] = chart_data[settings.DRY_YEAR_LABEL][settings.TREATED_LABEL]
    out_chart[settings.WET_YEAR_LABEL] = chart_data[settings.WET_YEAR_LABEL][settings.TREATED_LABEL]
    out_chart[settings.NORMAL_YEAR_LABEL] = chart_data[settings.NORMAL_YEAR_LABEL][settings.TREATED_LABEL]

    return out_chart

def delta_chart(chart_data):
    # out_chart = OrderedDict({})
    out_chart = {}
    out_chart[settings.DRY_YEAR_LABEL] = chart_data[settings.DRY_YEAR_LABEL][settings.TREATED_LABEL]
    out_chart[settings.WET_YEAR_LABEL] = chart_data[settings.WET_YEAR_LABEL][settings.TREATED_LABEL]
    out_chart[settings.NORMAL_YEAR_LABEL] = chart_data[settings.NORMAL_YEAR_LABEL][settings.TREATED_LABEL]

    return out_chart

# NEEDS:
#   pourpoint_id
#   treatment_id
# @cache_page(60 * 60) # 1 hour of caching
def get_hydro_results_by_pour_point_id(request):
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
    est_type = 'Modeled'
    impute_id = ppt.id
    flow_results = parse_flow_results(overlap_basin, treatment)

    flow_output = {
        settings.NORMAL_YEAR_LABEL: flow_results[settings.NORMAL_YEAR_LABEL]['flow_output'],
        settings.WET_YEAR_LABEL: flow_results[settings.WET_YEAR_LABEL]['flow_output'],
        settings.DRY_YEAR_LABEL: flow_results[settings.DRY_YEAR_LABEL]['flow_output']
    }

    avg_flow_results = {}

    # Baseline water yield (bas_char)
    # Cubic Feet per year (annual volume) / Square Feet (basin area) * 12 (inches/foot) = x inches/year
    baseline_water_yield = {}
    absolute_results = {}
    #   delta flow
    delta_results = {}
    seven_d_low_results = {}
    sept_median_7_day_low = {}
    #   1-day low-flow
    one_d_low_results = {}
    sept_median_1_day_low = {}

    seven_d_mean_results = {}
    one_d_mean_results = {}
    delta_1_d_low_results = {}
    delta_1_d_mean_results = {}
    delta_7_d_low_results = {}
    delta_7_d_mean_results = {}

    for weather_year in flow_results.keys():
        baseline_water_yield[weather_year] = str(round(flow_results[weather_year]['annual_water_volume'][settings.UNTREATED_LABEL]/(basin_acres*43560)*12, 2))

    absolute_results = sort_output(flow_output)
    delta_results = get_results_delta(flow_output)

    (seven_d_low_results, sept_median_7_day_low) = get_results_xd_low(flow_output, absolute_results, 7)
    (one_d_low_results, sept_median_1_day_low) = get_results_xd_low(flow_output, absolute_results, 1)
    seven_d_mean_results = get_results_xd_mean(flow_output, absolute_results, 7)
    one_d_mean_results = get_results_xd_mean(flow_output, absolute_results, 1)
    delta_1_d_low_results = get_results_delta(one_d_low_results)
    delta_1_d_mean_results = get_results_delta(one_d_mean_results)
    delta_7_d_low_results = get_results_delta(seven_d_low_results)
    delta_7_d_mean_results = get_results_delta(seven_d_mean_results)
    for weather_year in flow_results.keys():
        avg_flow_results[weather_year] = {}
        for treatment_type in [settings.UNTREATED_LABEL, settings.TREATED_LABEL]:
            avg_flow_results[weather_year][treatment_type] = str(round(flow_results[weather_year]['annual_water_volume'][treatment_type]/(365*24*60*60), 2))

    charts = [
        {'title': 'Absolute Flow Rate','data': absolute_chart(absolute_results)},
        {'title': 'Seven Day Low Flow','data': absolute_chart(seven_d_low_results)},
        {'title': 'Seven Day Mean Flow','data': absolute_chart(seven_d_mean_results)},
        {'title': 'One Day Low Flow','data': absolute_chart(one_d_low_results)},
        {'title': 'One Day Mean Flow','data': absolute_chart(one_d_mean_results)},
        # {'title': 'Change in Flow Rate','data': delta_chart(delta_results)},
        # {'title': 'Change in 7 Day Low Flow Rate','data': delta_chart(delta_7_d_low_results)},
        # {'title': 'Change in 7 Day Mean Flow Rate','data': delta_chart(delta_7_d_mean_results)},
        # {'title': 'Change in 1 Day Low Flow Rate','data': delta_chart(delta_1_d_low_results)},
        # {'title': 'Change in 1 Day Mean Flow Rate','data': delta_chart(delta_1_d_mean_results)},
        {'title': 'Change in Flow Rate','data': absolute_chart(delta_results)},
        {'title': 'Change in 7 Day Low Flow Rate','data': absolute_chart(delta_7_d_low_results)},
        {'title': 'Change in 7 Day Mean Flow Rate','data': absolute_chart(delta_7_d_mean_results)},
        {'title': 'Change in 1 Day Low Flow Rate','data': absolute_chart(delta_1_d_low_results)},
        {'title': 'Change in 1 Day Mean Flow Rate','data': absolute_chart(delta_1_d_mean_results)},
    ]

    bas_char_data = []
    bas_char_data.append({
        'key': 'Total area upslope of this gauging station',
        'value': basin_acres,
        'unit': 'acres',
        'help': '\'Upslope\' means \'all area that drains water to this point.\''
    })
    vus = VegPlanningUnit.objects.filter(dwnstream_ppt_id__in=upslope_ppts)
    acres_forested = int(sum([x.acres for x in vus]))
    bas_char_data.append({
        'key': 'Total forested area upslope',
        'value': acres_forested,
        'unit': 'acres',
        'help': '\'Upslope\' means \'all area that drains water to this point.\''
    })
    # bas_char_data.append({'key': 'Percent Forested', 'value': int(acres_forested/basin_acres*100), 'unit': '%' })
    bas_char_data.append({'key': 'Baseline water yield', 'value': baseline_water_yield[settings.NORMAL_YEAR_LABEL], 'unit': 'inches/year' })
    bas_char_data.append({'key': 'Baseline average annual flow', 'value': avg_flow_results[settings.NORMAL_YEAR_LABEL][settings.UNTREATED_LABEL], 'unit': 'CFS' })
    bas_char_data.append({'key': 'Baseline September mean flow', 'value': flow_results[settings.NORMAL_YEAR_LABEL]['sept_avg_flow'][settings.UNTREATED_LABEL], 'unit': 'CFS' })
    bas_char_data.append({'key': 'Baseline September median 7 day avg low flow', 'value': round(sept_median_7_day_low[weather_year][settings.UNTREATED_LABEL], 2), 'unit': 'CFS' })

    hydro_char_data = []
    hydro_char_data.append({'key': '<b>Change in average annual flow from proposed management</b>', 'value': '', 'unit': '' })
    # for weather_year in [x for x in avg_flow_results.keys() if not x == settings.UNTREATED_LABEL]:
    for weather_year in flow_results.keys():
        treatment_type_change = get_float_change_as_rounded_string(avg_flow_results[weather_year][settings.TREATED_LABEL],avg_flow_results[weather_year][settings.UNTREATED_LABEL])
        hydro_char_data.append({'key': '&nbsp;&nbsp;&nbsp;&nbsp;- %s' % weather_year, 'value': treatment_type_change, 'unit': 'CFS' }) #Baseline annl flow - 50 annl flow

    hydro_char_data.append({'key': '<b>Change in average September flow from proposed management </b>', 'value': '', 'unit': '' })
    # for weather_year in [x for x in sept_avg_flow.keys() if not x == settings.UNTREATED_LABEL]:
    for weather_year in flow_results.keys():
        if flow_results[weather_year]['flow_output'][settings.UNTREATED_LABEL]['records_available'] and flow_results[weather_year]['flow_output'][settings.TREATED_LABEL]['records_available']:
            treatment_type_sept_avg_change = get_float_change_as_rounded_string(flow_results[weather_year]['sept_avg_flow'][settings.TREATED_LABEL],flow_results[weather_year]['sept_avg_flow'][settings.UNTREATED_LABEL])
        else:
            treatment_type_sept_avg_change = 'Data not yet available'
        hydro_char_data.append({'key': '&nbsp;&nbsp;&nbsp;&nbsp;- %s' % weather_year, 'value': treatment_type_sept_avg_change, 'unit': 'CFS' })

    hydro_char_data.append({
        'key': '<b>Change in Sept. 7-day low flow from proposed management </b>',
        'value': '',
        'unit': '',
        # 'help': 'These values represent the difference between a {}, untreated year and various years that have had the proposed management applied'.format(settings.NORMAL_YEAR_LABEL)
    })
    # for weather_year in [x for x in sept_median_7_day_low.keys() if not x == settings.UNTREATED_LABEL]:
    for weather_year in flow_results.keys():
        # treatment_type_sept_7_day_low_diff = get_float_change_as_rounded_string(sept_median_7_day_low[weather_year],sept_median_7_day_low[settings.UNTREATED_LABEL])
        treatment_type_sept_7_day_low_diff = get_float_change_as_rounded_string(sept_median_7_day_low[weather_year][settings.TREATED_LABEL],sept_median_7_day_low[weather_year][settings.UNTREATED_LABEL])
        hydro_char_data.append({'key': '&nbsp;&nbsp;&nbsp;&nbsp;- %s' % weather_year, 'value': treatment_type_sept_7_day_low_diff, 'unit': 'CFS' })

    prop_mgmt_data = []
    basin_veg_units = treatment.veg_units.filter(geometry__intersects=overlap_basin.geometry) #within may be more accurate, but slower
    treatment_acres = sum([x.acres for x in basin_veg_units])
    prop_mgmt_data.append({'key': 'Total forested area in proposed treatment', 'value': int(treatment_acres), 'unit': 'acres' })

    summary_reports = []
    summary_reports.append({'title': 'Basin Characteristics','data': bas_char_data,'help': "These results are from a DHSVM run with climate data from a normal or average hydrologic year."})
    summary_reports.append({'title': 'Hydrologic Characteristics','data': hydro_char_data,'help': "Each of these results is for a DHSVM run with climate data from a representative dry, normal (average), and wet hydrologic year."})
    summary_reports.append({'title': 'Proposed Management','data': prop_mgmt_data})

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
        if treatment.job_can_run(settings.NORMAL_YEAR_LABEL) or treatment.job_can_run(settings.DRY_YEAR_LABEL) or treatment.job_can_run(settings.WET_YEAR_LABEL):
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

    weather_year_results = {
        settings.NORMAL_YEAR_LABEL: None,
        settings.WET_YEAR_LABEL: None,
        settings.DRY_YEAR_LABEL: None
    }
    for weather_year in settings.MODEL_YEARS.keys():
        weather_year_results[weather_year] = {
            'progress': None,
            'model_progress': 0,
            'import_progress': 0,
            'task_status': 'Initializing (1/4)',
            'error': 'None',
            'last_line': '',
            'age': None
        }

        if treatment.job_status(weather_year) == 'None':
            weather_year_results[weather_year]['task_status'] = 'Queued (0/4)'
        if treatment.job_status(weather_year) == 'FAILURE':
            weather_year_results[weather_year]['task_status'] = 'Failure. Restarting...'
            treatment.set_report()
        elif treatment.job_status(weather_year) != 'SUCCESS':
            # Attempt to re-run the job - if job is too new, it won't restart, just continue
            weather_year_results[weather_year]['progress'] = 0
            # check out /tmp/runs/run_{id}/output/Streamflow.only
            flow_outfile = "/tmp/runs/run_{}_{}/output/Streamflow.Only".format(treatment.id, weather_year)
            if Path(flow_outfile).exists():

                try:
                    weather_year_results[weather_year]['last_line'] = get_last_flow_line(flow_outfile)

                    [month, day, year] = weather_year_results[weather_year]['last_line'].split('-')[0].split('.')[0:3]
                    model_time = weather_year_results[weather_year]['last_line'].split(' ')[0].split('-')[1]
                    model_progress_date = datetime.strptime("{}.{}.{}-{}".format(month, day, year, model_time), "%m.%d.%Y-%H:%M:%S")
                    # model_year_type = settings.MODEL_YEAR_LOOKUP[str(year)]
                    model_year = settings.MODEL_YEARS[weather_year]
                    total_time = model_year['end'] - model_year['start']
                    completed_time = model_progress_date - model_year['start']
                    weather_year_results[weather_year]['model_progress'] = (completed_time.total_seconds()/total_time.total_seconds())*100*settings.MODEL_PROGRESS_FACTOR   #50% of the progress is modelling, so /2
                    weather_year_results[weather_year]['task_status'] = 'Modelling (2/4)'
                except (ValueError, IndexError) as e:
                    # Streamflow file doesn't have 2 complete entries yet.
                    weather_year_results[weather_year]['error'] = str(e)
                    print(e)
                    pass
                except OSError as e:
                    # Streamflow file empty
                    pass

                import_status_file = "/tmp/runs/run_{}_{}/output/dhsvm_status.log".format(treatment.id, weather_year)
                if Path(import_status_file).exists():
                    weather_year_results[weather_year]['task_status'] = 'Importing (3/4)'
                    with open(import_status_file, 'r') as f:
                        inlines=f.readlines()
                        weather_year_results[weather_year]['import_progress'] = int(inlines[-1])*settings.IMPORT_PROGRESS_FACTOR

            weather_year_results[weather_year]['progress'] = round(weather_year_results[weather_year]['model_progress']) + round(weather_year_results[weather_year]['import_progress'])
        else:
            weather_year_results[weather_year]['task_status'] = 'Complete'
            weather_year_results[weather_year]['progress'] = 100

        try:
            weather_year_results[weather_year]['age'] = treatment.job_age(weather_year).total_seconds()
        except AttributeError as e:
            weather_year_results[weather_year]['age'] = 0

    return JsonResponse(weather_year_results)

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
