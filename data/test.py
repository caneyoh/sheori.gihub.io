import pandas as pd
import datetime
import re
from math import sin, cos, acos, radians
EARTH_RAD = 6378.137
METER_PER_MINUTE = 2.778 * 60


def latlng_to_xyz(lat, lng):
    rlat, rlng = radians(lat), radians(lng)
    coslat = cos(rlat)
    return coslat*cos(rlng), coslat*sin(rlng), sin(rlat)


def dist_on_sphere(pos0, pos1, radius=EARTH_RAD):
    xyz0, xyz1 = latlng_to_xyz(*pos0), latlng_to_xyz(*pos1)
    return acos(sum(x * y for x, y in zip(xyz0, xyz1)))*radius


def minute_to_hour(minute):
    minute = round(minute)
    hour = minute // 60
    minute = minute % 60
    time = datetime.time(hour, minute, 00)
    return time


start_point = str("金沢駅")    # スタート地点
goal_point = str("片町")    # ゴール地点
must_spot = str("尾山神社")    # 絶対にいく地点
limit = datetime.time(8, 00, 00)    # 移動可能時間


def read_data():
    df_spot = pd.read_csv("Spot.csv")
    df_bus_stop = pd.read_csv("BusStop.csv")
    df_user = pd.read_csv("Cross.csv")
    return df_spot, df_user, df_bus_stop


def detect_point(df_bus_stop, point):
    """
    ユーザーの指定したpointを参照し、指定されたbus_stop_idを返す関数
    """
    df_point_extracted = df_bus_stop[df_bus_stop["name"] == point]
    point_id = str(df_point_extracted['bus_stop_id'].values[0])
    return point_id


def detect_spot(df_spot, spot):
    """
    ユーザーの指定したspotを参照し、指定されたspot_idを返す関数
    """
    df_spot_extracted = df_spot[df_spot["name"] == spot]
    spot_id = str(df_spot_extracted['id'].values[0])

    return spot_id


def get_position(any_id):
    df_spot, df_user, df_bus_stop = read_data()
    if re.match('B', any_id):
        df_spot_extracted = df_bus_stop[df_bus_stop["bus_stop_id"] == str(any_id)]
        spot = df_spot_extracted['latitude'].values[0], df_spot_extracted['longitude'].values[0]
    else:
        df_spot_extracted = df_spot[df_spot["id"] == str(any_id)]
        spot = df_spot_extracted['latitude'].values[0], df_spot_extracted['longitude'].values[0]
    return spot


def get_name(any_id):
    df_spot, df_user, df_bus_stop = read_data()
    if re.match('B', any_id):
        df_spot_extracted = df_bus_stop[df_bus_stop["bus_stop_id"] == str(any_id)]
        spot = df_spot_extracted['name'].values[0]
    else:
        df_spot_extracted = df_spot[df_spot["id"] == str(any_id)]
        spot = df_spot_extracted['name'].values[0]
    return spot


def get_time(dist):
    time = dist * 1000 / METER_PER_MINUTE
    return time


def add_times(time, add_time):
    added_time = datetime.datetime.combine(datetime.date.today(), time) + datetime.timedelta(hours=add_time.hour,
                                                                                             minutes=add_time.minute)
    return added_time


def make_route_list(x, spots_list, root_list):
    for i in range(x):
        spots_list.append(root_list[i])
    return spots_list


# ====================================================================================
def main(start_point_name, goal_point_name, must_spot_name, limit_time):
    """1. Spotリストから平均評価点の上位xの物を抽出する"""
    df_spot, df_user, df_bus_stop = read_data()     # dfを取得,cfを作成
    route_lists = []
    """1-1. 各spotの平均評価点をリストに抽出"""
    average_list = []
    for length in range(30):
        spot_id = df_spot['id'].values[length]
        df_scores = df_user[df_user[spot_id] != 0]
        average = round(df_scores[spot_id].mean(), 2)
        average_list.append((spot_id, average))
    must_spot_id = detect_spot(df_spot, must_spot_name)
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
    start_point_id = detect_point(df_bus_stop, start_point_name)
    goal_point_id = detect_point(df_bus_stop, goal_point_name)
    for i in range(limit_time.hour):
        spots = []
        spots.append(start_point_id)
        spots.append(must_spot_id)
        spots_list = make_route_list(i, spots, sorted_id_list)
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
                spot_1 = get_position(route_spots_copy[i])
                spot_2 = get_position(route_spots_copy[i + 1])
                spot_3 = get_position(spot)
                dist_1_2 = dist_on_sphere(spot_1, spot_2)
                dist_1_3 = dist_on_sphere(spot_1, spot_3)
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
                spot_spend_time_list = df_spot_extracted['time_spent_ave'].values[0].split(':')
                spot_spend_time = datetime.time(int(spot_spend_time_list[0]), int(spot_spend_time_list[1]),
                                                int(spot_spend_time_list[2]))
                sum_time = add_times(sum_time, spot_spend_time).time()
                time_list.append(spot_spend_time)
            spot_a = get_position(route_spots_copy[i])
            spot_b = get_position(route_spots_copy[i + 1])
            dist_a_b = dist_on_sphere(spot_a, spot_b)
            time_a_b = get_time(dist_a_b)
            time_a_b = minute_to_hour(time_a_b)
            dist_a_b = round(dist_a_b * 1000)
            # if type(sum_time) == datetime.datetime:
            #     sum_time = sum_time.time()
            sum_time = add_times(sum_time, time_a_b).time()
            time_list.append(time_a_b)
            dist_list.append(dist_a_b)
        packed_route = [route_spots_copy, sum_time, time_list, dist_list]
        if sum_time > add_times(limit_time, datetime.time(1, 00, 00)).time():
            continue
        if len(route_lists) == 0:
            route_lists = packed_route
        else:
            if packed_route[1] > route_lists[1]:
                route_lists = packed_route
            else:
                continue
    for spot in route_lists[0]:
        print(get_name(spot))
    print(route_lists)


# ====================================================================================
main(start_point, goal_point, must_spot, limit)
"""
注意！
limitが小さすぎた際は適したルートが算出されず、エラーが発生する。
"""
