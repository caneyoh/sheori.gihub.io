from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import re
import datetime
import pandas as pd
from math import sin, cos, acos, radians





from sheori.scripts.recommend.recommend_main import RecommendRoute
from sheori.scripts.recommend.cross_tabulation import CrossTable

from sheori.models import Spot, BusStop, RouteMap, Route, SaveRoute

EARTH_RAD = 6378.137
METER_PER_MINUTE = 2.778 * 60


def form_view(request):  # フォームを表示
    return render(request, 'sheori/recommend_form.html')


def make_result(request):  # フォームの入力をAPIに伝達、リターン値を用いてテンプレートに表示
    var = request.GET
    start_point = var.get('start_point')
    goal_point = (var.get('goal_point'))
    must_spot = var.get('must_spot')
    start_time = (var.get('start_time'))
    goal_time = (var.get('goal_time'))
    # results = RecommendRoute(gender, household, station, limit).main()
    route_id = RecommendRoute(start_point, goal_point, must_spot, start_time, goal_time, request).main()
    # result = [[route_spots_copy], sum_time, [time_list], [dist_list]]
    print("AAAAAAAAAAAAAAAAAAAAAA")
    return redirect('sheori:route_view', route_id)


def route_view(request, route_id):
    route = Route.objects.get(id=route_id)
    maps = RouteMap.objects.filter(route=route)
    maps = sorted(maps, key=lambda map_: map_.order)
    route_spots = []
    time_list = []
    dist_list = []
    sum_time = datetime.time(0, 00, 00)
    for i in range(len(maps)):
        if i == 0:
            route_spots.append(maps[i].start_point.id)
        elif maps[i] == maps[-1]:
            route_spots.append(maps[i].goal_point.id)
        else:
            route_spots.append(maps[i].spot.id)

    for i in range(len(route_spots) - 1):
        if i != 0:
            df_spot, df_user, df_bus_stop = read_data()
            df_spot_extracted = df_spot[df_spot['id'] == route_spots[int(i)]]
            # spot_spend_time_list = df_spot_extracted['time_spent_ave'].values[0].split(':')
            spot_spend_time = df_spot_extracted['time_spent_ave'].values[0]
            # spot_spend_time = datetime.time(int(spot_spend_time_list[0]), int(spot_spend_time_list[1]),
            #                                 int(spot_spend_time_list[2]))
            sum_time = add_times(sum_time, spot_spend_time).time()
            time_list.append(spot_spend_time)
        spot_a = get_position(route_spots[i])
        spot_b = get_position(route_spots[i + 1])
        dist_a_b = dist_on_sphere(spot_a, spot_b)
        time_a_b = get_time(dist_a_b)
        time_a_b = minute_to_hour(time_a_b)
        dist_a_b = round(dist_a_b * 1000)
        # if type(sum_time) == datetime.datetime:
        #     sum_time = sum_time.time()
        sum_time = add_times(sum_time, time_a_b).time()
        time_list.append(time_a_b)
        dist_list.append(dist_a_b)
    results = [route_spots, sum_time, time_list, dist_list]
    spot_name = []
    spot_id = []
    for x in results[0]:
        if re.match('B', x):
            spot_name.append(BusStop.objects.get(id=x).name)
        else:
            spot_name.append(Spot.objects.get(id=x).name)
    results[0] = spot_name
    spot_names = results[0]
    sum_time = results[1]
    time_list = results[2]
    dist_list = results[3]
    start_list = [spot_names.pop(0), time_list.pop(0), dist_list.pop(0)]
    main = []
    for i in range(len(spot_names) - 1):
        main_list = []
        main_list.append(Spot.objects.get(name=spot_names[i]))
        main_list.append(time_list[i * 2])
        main_list.append(time_list[i * 2 - 1])
        main_list.append(dist_list[i])
        main.append(main_list)
    goal_list = spot_names[-1]
    route_ = Route.objects.get(id=route_id)
    save_condition = SaveRoute.objects.filter(user=request.user.profile).filter(route=route_)
    if len(save_condition) == 0:
        save = True
    else:
        save = False
    save_num = SaveRoute.objects.filter(route=route_).count()
    packed_route = {
        'route': route_id,
        'start_list': start_list,
        'main': main,
        'goal_list': goal_list,
        'sum_time': sum_time,
        'save': save,
        'save_num': save_num,
    }
    return render(request, 'sheori/recommend_result.html', packed_route)


@login_required
def route_save(request, route_id):
    route_ = Route.objects.get(id=route_id)
    route_save_condition = SaveRoute.objects.filter(user=request.user.profile).filter(route=route_)
    if len(route_save_condition) != 0:
        save_data = SaveRoute.objects.get(user=request.user.profile, route=route_)
        save_data.delete()
        route_.save_num -= 1
        route_.save()
    else:
        SaveRoute.objects.create(
            user=request.user.profile,
            route=route_,
        )
        route_.save_num += 1
        route_.save()
    return redirect('sheori:route_view', route_id)


def get_position(any_id):
    df_spot, df_user, df_bus_stop = read_data()
    if re.match('B', any_id):
        df_spot_extracted = df_bus_stop[df_bus_stop["id"] == str(any_id)]
        spot = df_spot_extracted['latitude'].values[0], df_spot_extracted['longitude'].values[0]
    else:
        df_spot_extracted = df_spot[df_spot["id"] == str(any_id)]
        spot = df_spot_extracted['latitude'].values[0], df_spot_extracted['longitude'].values[0]
    return spot


def read_data():
    df_spot = pd.DataFrame.from_records(list(Spot.objects.values()))
    df_bus_stop = pd.DataFrame.from_records(list(BusStop.objects.values()))
    df_user, _ = CrossTable().get()
    return df_spot, df_user, df_bus_stop


def get_time( dist):
    time = dist * 1000 / METER_PER_MINUTE
    return time


def add_times(time, add_time):
    if type(time) == datetime.datetime:
        time = time.time()
    if type(add_time) == datetime.datetime:
        add_time = add_time.time()
    added_time = datetime.datetime.combine(datetime.date.today(), time) +\
                 datetime.timedelta(hours=add_time.hour, minutes=add_time.minute)
    return added_time


def latlng_to_xyz(lat, lng):
    rlat, rlng = radians(lat), radians(lng)
    coslat = cos(rlat)
    return coslat * cos(rlng), coslat * sin(rlng), sin(rlat)


def dist_on_sphere(pos0, pos1, radius=EARTH_RAD):
    xyz0, xyz1 = latlng_to_xyz(*pos0), latlng_to_xyz(*pos1)
    return acos(sum(x * y for x, y in zip(xyz0, xyz1))) * radius


def minute_to_hour(minute):
    minute = round(minute)
    hour = minute // 60
    minute = minute % 60
    time = datetime.time(hour, minute, 00)
    return time
