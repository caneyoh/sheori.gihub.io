from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now
# from django.urls import reverse

GENDER_LIST = ((0, '男性'), (1, '女性'), (2, '無回答'))
dict_gender_list = dict(GENDER_LIST)
RESIDENCE_LIST = ((0, '有'), (1, '無'))
dict_residence_list = dict(RESIDENCE_LIST)
GENRE_LIST = ((0, '歴史・文化施設'), (1, '美術館・博物館'), (2, '寺社'), (3, '娯楽'), (4, '温泉・銭湯'), (5, 'グルメ'), (6, 'その他'))
genre_list = dict(GENRE_LIST)


# デフォルトであるdjango.dbのmodelsを継承して作成する
class Profile(models.Model):
    # django仕様のメタクラス(クラス自体の設定を記述)(管理画面での表示内容を設定)
    class Meta:
        verbose_name = 'ユーザー情報データ'
        verbose_name_plural = 'ユーザー情報データ'

    # ユーザーの設定。下記のフィールドとの紐づけはビューで行う
    user = models.OneToOneField(User, verbose_name='ユーザー', null=True, blank=True, on_delete=models.CASCADE)

    # フィールドの設定。コード１行がフィールド１列に対応する。
    id = models.CharField(max_length=6, primary_key=True)
    age = models.IntegerField('年齢')
    gender = models.IntegerField('性別', choices=GENDER_LIST)
    residence = models.IntegerField('金沢在住経験', choices=RESIDENCE_LIST)

    # 管理画面で表示される文字列を定義する
    def __str__(self):
        user_str = ''
        if self.user is not None:
            user_str = '(' + self.user.username + ')'

        return self.id + ' ' + str(self.age) + '歳 ' + dict_gender_list.get(self.gender)


class BusStop(models.Model):
    class Meta:
        verbose_name = 'バス停データ'
        verbose_name_plural = 'バス停データ'

    id = models.CharField('バス停ID', max_length=6, primary_key=True)
    name = models.CharField('バス停名', max_length=50)
    latitude = models.FloatField('バス停緯度')
    longitude = models.FloatField('バス停経度')

    def __str__(self):
        return 'ID: ' + self.id + ' ' + self.name


class Spot(models.Model):
    class Meta:
        verbose_name = '観光スポット情報データ'
        verbose_name_plural = '観光スポット情報データ'

    id = models.CharField('観光スポットID', max_length=6, primary_key=True)
    name = models.CharField('観光スポット名', max_length=50)
    genre = models.IntegerField('ジャンル', choices=GENRE_LIST)
    address = models.CharField('住所', max_length=100)
    latitude = models.FloatField('観光スポット緯度')
    longitude = models.FloatField('観光スポット経度')
    time_spent_ave = models.TimeField('平均滞在時間')
    detail = models.TextField('詳細情報')
    nearest_bus_stop = models.ForeignKey(BusStop, '最寄りバス停', null=True)
    dist_to_nearest_bus_stop = models.FloatField('最寄りバス停距離', null=True)

    def __str__(self):
        return 'ID: ' + self.id + ' ' + self.name


class ScoreLog(models.Model):
    class Meta:
        verbose_name = '観光スポット評価データ'
        verbose_name_plural = '観光スポット評価データ'

    profile = models.ForeignKey(Profile, verbose_name='ユーザー情報', on_delete=models.CASCADE)
    spot = models.ForeignKey(Spot, verbose_name='観光スポット', on_delete=models.CASCADE)

    score = models.IntegerField('評価')
    timestamp = models.DateTimeField('日時', auto_now_add=True)


class Route(models.Model):
    class Meta:
        verbose_name = '観光ルートデータ'
        verbose_name_plural = '観光ルートデータ'

    id = models.CharField('観光ルートID', max_length=9, primary_key=True)
    save_num = models.PositiveIntegerField('保存数', default=0)


class RouteMap(models.Model):
    class Meta:
        verbose_name = '観光ルート詳細データ'
        verbose_name_plural = '観光ルート詳細データ'

    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    spot = models.ForeignKey(Spot, verbose_name='観光スポット', on_delete=models.CASCADE, null=True)
    start_point = models.ForeignKey(BusStop, verbose_name='出発地点', on_delete=models.CASCADE, null=True,
                                    related_name='start_point')
    goal_point = models.ForeignKey(BusStop, verbose_name='到着地点', on_delete=models.CASCADE, null=True,
                                   related_name='goal_point')
    order = models.IntegerField('順序')


class SaveRoute(models.Model):
    class Meta:
        verbose_name = '観光ルート保存データ'
        verbose_name_plural = '観光ルート保存データ'

    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='save_user')
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)


class SpotImage(models.Model):
    """イメージモデル"""
    class Meta:
        verbose_name = '観光スポット画像データ'
        verbose_name_plural = '観光スポット画像データ'
        db_table = 'image'
    spot = models.ForeignKey(Spot, verbose_name='観光地', on_delete=models.PROTECT)
    image = models.ImageField(upload_to="image/", verbose_name='イメージ')
    created_at = models.DateTimeField(verbose_name='登録日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    def __str__(self):
        return self.work.name + ":" + str(self.data_datetime)
