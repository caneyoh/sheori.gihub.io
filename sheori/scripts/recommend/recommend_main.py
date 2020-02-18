import pandas as pd
import datetime
import re
import argparse
import numpy as np
from math import sin, cos, acos, radians
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist


from sheori.models import Route, Spot, BusStop, RouteMap, Profile
from sheori.scripts.recommend.cross_tabulation import CrossTable

EARTH_RAD = 6378.137
METER_PER_MINUTE = 2.778 * 60


class RecommendRoute(object):
    def __init__(self, start_point_name, goal_point_name, must_spot_name, start_time, goal_time, request):
        self.start_point_name = start_point_name
        self.goal_point_name = goal_point_name
        self.must_spot_name = must_spot_name
        self.start_time = self.make_time(start_time)
        self.goal_time = self.make_time(goal_time)
        self.limit_time = self.subtract_times(self.goal_time, self.start_time)
        self.request = request
        pass

    def main(self, console=False):
        """1. Spotリストから平均評価点の上位xの物を抽出する"""
        df_spot, df_user, df_bus_stop = self.read_data()  # dfを取得,cfを作成
        route_lists = []
        """1-1. 各spotの平均評価点をリストに抽出"""
        average_list = []
        for length in range(30):
            spot_id = df_spot['id'].values[length]
            df_scores = df_user[df_user[spot_id] != 0]
            average = round(df_scores[spot_id].mean(), 2)
            average_list.append((spot_id, average))
        must_spot_id = self.detect_spot(df_spot, self.must_spot_name)
        for i, v in enumerate(average_list):
            if v[0] == must_spot_id:
                average_list.pop(average_list.index(v))
        """1-2. average_listをソートする"""
        sorted_average_list = sorted(average_list, key=lambda tup: tup[1], reverse=True)
        sorted_id_list = []
        for list_content in sorted_average_list:
            sorted_id_list.append(list_content[0])
        """1−3. spotの候補を作成"""
        spots_lists = []
        start_point_id = self.detect_point(df_bus_stop, self.start_point_name)
        goal_point_id = self.detect_point(df_bus_stop, self.goal_point_name)
        for i in range(self.limit_time.hour):
            spots = []
            spots.append(start_point_id)
            spots.append(must_spot_id)
            spots_list = self.make_route_list(i, spots, sorted_id_list)
            spots.append(goal_point_id)
            spots_lists.append(spots_list)
        """2. 抽出したspotsからそれぞれのルートを作成し、spotsごとのroute, sum_time, time_list, dist_listを作成する"""
        """2-1. routeを作成する"""
        for spots in spots_lists:
            sum_time = datetime.time(0, 00, 00)
            route_spots = [spots.pop(0), spots.pop(0), spots.pop(-1)]
            route_spots_copy = [route_spots[0], route_spots[1], route_spots[2]]
            for spot in spots:
                for i in range(len(route_spots_copy)):
                    spot_1 = self.get_position(route_spots_copy[i])
                    spot_2 = self.get_position(route_spots_copy[i + 1])
                    spot_3 = self.get_position(spot)
                    dist_1_2 = self.dist_on_sphere(spot_1, spot_2)
                    dist_1_3 = self.dist_on_sphere(spot_1, spot_3)
                    if dist_1_2 >= dist_1_3:
                        """new_spotを最適ルート上に挿入する"""
                        route_spots_copy.insert(i + 1, spot)
                        break
                    elif i == len(route_spots_copy) - 2:
                        """new_spotを最後の一つ前に挿入する"""
                        route_spots_copy.insert(-1, spot)
                        break
                    else:
                        continue
            """2-2. routeの各要素を計算する
            sum_time: 合計所要時間
            time_list: 各スポット間の所要時間
            dist_list: 各スポット間の所要距離
            """
            time_list = []
            dist_list = []
            for i in range(len(route_spots_copy) - 1):
                if i != 0:
                    df_spot_extracted = df_spot[df_spot['id'] == route_spots_copy[int(i)]]
                    # spot_spend_time_list = df_spot_extracted['time_spent_ave'].values[0].split(':')
                    spot_spend_time = df_spot_extracted['time_spent_ave'].values[0]
                    # spot_spend_time = datetime.time(int(spot_spend_time_list[0]), int(spot_spend_time_list[1]),
                    #                                 int(spot_spend_time_list[2]))
                    sum_time = self.add_times(sum_time, spot_spend_time).time()
                    time_list.append(spot_spend_time)
                spot_a = self.get_position(route_spots_copy[i])
                spot_b = self.get_position(route_spots_copy[i + 1])
                dist_a_b = self.dist_on_sphere(spot_a, spot_b)
                time_a_b = self.get_time(dist_a_b)
                time_a_b = self.minute_to_hour(time_a_b)
                dist_a_b = round(dist_a_b * 1000)
                # if type(sum_time) == datetime.datetime:
                #     sum_time = sum_time.time()
                sum_time = self.add_times(sum_time, time_a_b).time()
                time_list.append(time_a_b)
                dist_list.append(dist_a_b)
            packed_route = [route_spots_copy, sum_time, time_list, dist_list]
            if sum_time > self.add_times(self.limit_time, datetime.time(1, 00, 00)).time():
                continue
            if len(route_lists) == 0:
                route_lists = packed_route
            else:
                if packed_route[1] > route_lists[1]:
                    route_lists = packed_route
                else:
                    continue
        if console == True:
            print(route_lists)
        route_id = save_route(route_lists[0])
        return route_id

    def make_time(self, time='00:00'):
        time = time.split(':')  # time = ['00', '00']
        time = datetime.time(int(time[0]), int(time[1]), 00)
        return time

    def latlng_to_xyz(self, lat, lng):
        rlat, rlng = radians(lat), radians(lng)
        coslat = cos(rlat)
        return coslat * cos(rlng), coslat * sin(rlng), sin(rlat)

    def dist_on_sphere(self, pos0, pos1, radius=EARTH_RAD):
        xyz0, xyz1 = self.latlng_to_xyz(*pos0), self.latlng_to_xyz(*pos1)
        return acos(sum(x * y for x, y in zip(xyz0, xyz1))) * radius

    def minute_to_hour(self, minute):
        minute = round(minute)
        hour = minute // 60
        minute = minute % 60
        time = datetime.time(hour, minute, 00)
        return time

    def read_data(self):
        df_spot = pd.DataFrame.from_records(list(Spot.objects.values()))
        df_bus_stop = pd.DataFrame.from_records(list(BusStop.objects.values()))
        df_user, _ = CrossTable().get()
        return df_spot, df_user, df_bus_stop

    def detect_point(self, df_bus_stop, point):
        """
        ユーザーの指定したpointを参照し、指定されたbus_stop_idを返す関数
        """
        df_point_extracted = df_bus_stop[df_bus_stop["name"] == point]
        point_id = str(df_point_extracted['id'].values[0])
        return point_id

    def detect_spot(self, df_spot, spot):
        """
        ユーザーの指定したspotを参照し、指定されたspot_idを返す関数
        """
        df_spot_extracted = df_spot[df_spot["name"] == spot]
        spot_id = str(df_spot_extracted['id'].values[0])

        return spot_id

    def get_position(self, any_id):
        df_spot, df_user, df_bus_stop = self.read_data()
        if re.match('B', any_id):
            df_spot_extracted = df_bus_stop[df_bus_stop["id"] == str(any_id)]
            spot = df_spot_extracted['latitude'].values[0], df_spot_extracted['longitude'].values[0]
        else:
            df_spot_extracted = df_spot[df_spot["id"] == str(any_id)]
            spot = df_spot_extracted['latitude'].values[0], df_spot_extracted['longitude'].values[0]
        return spot

    def get_name(self, any_id):
        df_spot, df_user, df_bus_stop = self.read_data()
        if re.match('B', any_id):
            df_spot_extracted = df_bus_stop[df_bus_stop["bus_stop_id"] == str(any_id)]
            spot = df_spot_extracted['name'].values[0]
        else:
            df_spot_extracted = df_spot[df_spot["id"] == str(any_id)]
            spot = df_spot_extracted['name'].values[0]
        return spot

    def get_time(self, dist):
        time = dist * 1000 / METER_PER_MINUTE
        return time

    def add_times(self, time, add_time):
        if type(time) == datetime.datetime:
            time = time.time()
        if type(add_time) == datetime.datetime:
            add_time = add_time.time()
        added_time = datetime.datetime.combine(datetime.date.today(), time) + datetime.timedelta(hours=add_time.hour,
                                                                                                     minutes=add_time.minute)
        return added_time

    def subtract_times(self, time, subtract_time):
        added_time = datetime.datetime.combine(datetime.date.today(), time) - datetime.timedelta(hours=subtract_time.hour,
                                                                                                 minutes=subtract_time.minute)
        return added_time

    def make_route_list(self, x, spots_list, root_list):
        for i in range(x):
            spots_list.append(root_list[i])
        return spots_list


def save_route(spots):
    # df_route, _ = CrossTable().get_route()
    # route_ids = Route.objects.id
    # for route_id in route_ids:
    #     df_route_spots = df_route[route_id]
    #     df_route_spots.dropna(how='any', axis=1)
    route_ids = Route.objects.all().values_list('id', flat=True)
    check = True
    for route_id in route_ids:
        route = Route.objects.get(id=route_id)
        maps = RouteMap.objects.filter(route=route)
        maps = sorted(maps, key=lambda x: x.order)
        maps_ = []
        for i in range(len(maps)):
            if i == 0:
                maps_.append(maps[i].start_point.id)
            elif maps[i] == maps[-1]:
                maps_.append(maps[i].goal_point.id)
            else:
                maps_.append(maps[i].spot.id)
        if maps_ == spots:
            check = False
            route_id_ = route_id
    if check:
        try:
            max_id = Route.objects.latest('id').id
        except ObjectDoesNotExist:
            max_id = 'R00000000'

        route_id_ = 'R' + (str(int(max_id[1:]) + 1).zfill(8))

        Route.objects.create(
            id=route_id_,
            save_num=0,
        )

        for i, spot_ in enumerate(spots):
            print(Route.objects.filter(id=route_id_))
            if i == 0:
                RouteMap.objects.create(
                    route=Route.objects.filter(id=route_id_)[0],
                    start_point=BusStop.objects.filter(id=spot_)[0],
                    order=i,
                )
            elif spot_ == spots[-1]:
                RouteMap.objects.create(
                    route=Route.objects.filter(id=route_id_)[0],
                    goal_point=BusStop.objects.filter(id=spot_)[0],
                    order=i,
                )
            else:
                RouteMap.objects.create(
                    route=Route.objects.filter(id=route_id_)[0],
                    spot=Spot.objects.filter(id=spot_)[0],
                    order=i,
                )
    return route_id_


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='datatype.')
    parser.add_argument('-g', '--goal_point', required=True)
    parser.add_argument('-s', '--start_point', required=True)
    parser.add_argument('-m', '--must_spot', required=False)
    parser.add_argument('-t', '--start_time', required=False)
    parser.add_argument('-i', '--goal_time', required=False)
    args = parser.parse_args()
    start_point = args.start_point
    goal_point = args.goal_point
    must_spot = args.must_spot
    start_time = args.start_time
    goal_time = args.goal_time
    np.random.seed(seed=1234)
    rn = RecommendRoute(start_point, goal_point, must_spot, start_time, goal_time)
    rn.main(console=True)
