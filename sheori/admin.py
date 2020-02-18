from django.contrib import admin

# モデルをインポート
from .models import Profile, Spot, ScoreLog, BusStop, RouteMap, Route, SaveRoute, SpotImage

# 管理サイトへのモデルの登録
admin.site.register(Profile)
admin.site.register(Spot)
admin.site.register(ScoreLog)
admin.site.register(BusStop)
admin.site.register(RouteMap)
admin.site.register(Route)
admin.site.register(SaveRoute)
admin.site.register(SpotImage)
