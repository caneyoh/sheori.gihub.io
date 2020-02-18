from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator
from sheori.models import Spot, ScoreLog

import random

message_rate_created = '評価が登録されました！'
message_rate_updated = '評価が更新されました！'


def list_view(request):
    spot_list = Spot.objects.all().order_by('id')

    paginator = Paginator(spot_list, 10)

    try:
        page = int(request.GET.get('page'))
    except:
        page = 1

    spots = paginator.get_page(page)
    return render(request, 'sheori/spot_list.html', {'spots': spots, 'page': page, 'last_page': paginator.num_pages})


def detail_view(request, spot_id):
    spot = get_object_or_404(Spot, id=spot_id)

    try:
        page = int(request.GET.get('from_page'))
    except:
        page = 1

    try:
        log = ScoreLog.objects.get(profile_id=request.user.profile.id, spot_id=spot_id)
        current_score = log.score
    except:
        current_score = -1

    return render(request, 'sheori/spot_detail.html',
                  {'spot': spot, 'page': page, 'current_score': current_score})


# 追加！
@login_required
def rate(request, spot_id):
    spot = get_object_or_404(Spot, id=spot_id)

    log, created = ScoreLog.objects.update_or_create(
        defaults={'score': request.POST.get('score')},
        profile_id=request.user.profile.id,
        spot_id=spot_id,
    )

    if created:
        messages.success(request, message_rate_created)
    else:
        messages.success(request, message_rate_updated)

    return redirect('sheori:spot_detail', spot_id=spot_id)
