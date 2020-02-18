# path()関数のインボート
from django.urls import path
from sheori.views import spot, recommend, mypage
# ルーティングの設定
app_name = 'sheori'
urlpatterns = [
    path('spot', spot.list_view, name='spot_list'),
    path('spot/<slug:spot_id>', spot.detail_view, name='spot_detail'),
    path('spot/<slug:spot_id>/rate', spot.rate, name='spot_rate'),
    path('recommend/result/<slug:route_id>/save', recommend.route_save, name='route_save'),
    path('recommend', recommend.form_view, name='recommend_form'),
    path('recommend/result/', recommend.make_result, name='recommend_result'),
    path('recommend/result/<slug:route_id>', recommend.route_view, name='route_view'),
    path('mypage', mypage.mypage_top, name='mypage_top'),
    ]
