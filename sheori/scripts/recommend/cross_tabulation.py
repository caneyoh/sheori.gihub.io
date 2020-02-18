import pandas as pd
import numpy as np
import argparse
from tqdm import tqdm
import time
from sheori.models import ScoreLog, Spot, Route, Profile, RouteMap, BusStop


class CrossTable(object):
    def _make_profile(self):
        profiles = pd.DataFrame.from_records(list(Profile.objects.values()))
        profiles.set_index('id')

        return profiles

    def _make_table(self):
        idx_profile = Profile.objects.values_list('id', flat=True)
        col_spot = Spot.objects.values_list('id', flat=True)

        cf = pd.DataFrame(index=idx_profile, columns=col_spot).fillna(0)

        for log in ScoreLog.objects.iterator():
            cf.at[log.profile_id, log.spot_id] = log.score

        return cf

    def get(self):
        profile = self._make_profile()
        cf = self._make_table()

        joined = profile.set_index('id').join(cf)

        return joined, cf

    def _make_routes(self):
        routes = pd.DataFrame.from_records(list(Route.objects.values()))
        routes.set_index('id')

        return routes

    def _make_route_table(self):
        idx_route = Route.objects.values_list('id', flat=True)
        col_spot = Spot.objects.values_list('id', flat=True)
        col_bus_stop = BusStop.objects.values_list('id', flat)

        cf = pd.DataFrame(index=idx_route, columns=col_spot)

        for log in RouteMap.objects.iterator():
            cf.at[log.route_id, log.spot_id] = log.order

        return cf

    def get_route(self):
        route = self._make_routes()
        cf = self._make_route_table()

        joined = route.set_index('id').join(cf)

        return joined, cf

