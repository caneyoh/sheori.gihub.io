# Generated by Django 2.2.1 on 2020-02-06 05:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BusStop',
            fields=[
                ('id', models.CharField(max_length=6, primary_key=True, serialize=False, verbose_name='バス停ID')),
                ('name', models.CharField(max_length=50, verbose_name='バス停名')),
                ('latitude', models.FloatField(verbose_name='バス停緯度')),
                ('longitude', models.FloatField(verbose_name='バス停経度')),
            ],
            options={
                'verbose_name': 'バス停データ',
                'verbose_name_plural': 'バス停データ',
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.CharField(max_length=6, primary_key=True, serialize=False)),
                ('age', models.IntegerField(verbose_name='年齢')),
                ('gender', models.IntegerField(choices=[(0, '男性'), (1, '女性'), (2, '無回答')], verbose_name='性別')),
                ('residence', models.IntegerField(choices=[(0, '有'), (1, '無')], verbose_name='金沢在住経験')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='ユーザー')),
            ],
            options={
                'verbose_name': 'ユーザー情報データ',
                'verbose_name_plural': 'ユーザー情報データ',
            },
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.CharField(max_length=9, primary_key=True, serialize=False, verbose_name='観光ルートID')),
                ('save_num', models.PositiveIntegerField(default=0, verbose_name='保存数')),
            ],
            options={
                'verbose_name': '観光ルートデータ',
                'verbose_name_plural': '観光ルートデータ',
            },
        ),
        migrations.CreateModel(
            name='Spot',
            fields=[
                ('id', models.CharField(max_length=6, primary_key=True, serialize=False, verbose_name='観光スポットID')),
                ('name', models.CharField(max_length=50, verbose_name='観光スポット名')),
                ('genre', models.IntegerField(choices=[(0, '歴史・文化施設'), (1, '美術館・博物館'), (2, '寺社'), (3, '娯楽'), (4, '温泉・銭湯'), (5, 'グルメ'), (6, 'その他')], verbose_name='ジャンル')),
                ('address', models.CharField(max_length=100, verbose_name='住所')),
                ('latitude', models.FloatField(verbose_name='観光スポット緯度')),
                ('longitude', models.FloatField(verbose_name='観光スポット経度')),
                ('time_spent_ave', models.TimeField(verbose_name='平均滞在時間')),
                ('detail', models.TextField(verbose_name='詳細情報')),
                ('dist_to_nearest_bus_stop', models.FloatField(null=True, verbose_name='最寄りバス停距離')),
                ('nearest_bus_stop', models.ForeignKey(null=True, on_delete='最寄りバス停', to='sheori.BusStop')),
            ],
            options={
                'verbose_name': '観光スポット情報データ',
                'verbose_name_plural': '観光スポット情報データ',
            },
        ),
        migrations.CreateModel(
            name='SpotImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='image/', verbose_name='イメージ')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='登録日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
                ('spot', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='sheori.Spot', verbose_name='観光地')),
            ],
            options={
                'db_table': 'image',
            },
        ),
        migrations.CreateModel(
            name='ScoreLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField(verbose_name='評価')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='日時')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sheori.Profile', verbose_name='ユーザー情報')),
                ('spot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sheori.Spot', verbose_name='観光スポット')),
            ],
            options={
                'verbose_name': '観光スポット評価データ',
                'verbose_name_plural': '観光スポット評価データ',
            },
        ),
        migrations.CreateModel(
            name='SaveRoute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sheori.Route')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='save_user', to='sheori.Profile')),
            ],
            options={
                'verbose_name': '観光ルート保存データ',
                'verbose_name_plural': '観光ルート保存データ',
            },
        ),
        migrations.CreateModel(
            name='RouteMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(verbose_name='順序')),
                ('goal_point', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='goal_point', to='sheori.BusStop', verbose_name='到着地点')),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sheori.Route')),
                ('spot', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='sheori.Spot', verbose_name='観光スポット')),
                ('start_point', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='start_point', to='sheori.BusStop', verbose_name='出発地点')),
            ],
            options={
                'verbose_name': '観光ルート詳細データ',
                'verbose_name_plural': '観光ルート詳細データ',
            },
        ),
    ]
