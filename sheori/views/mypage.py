from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

import json
from sheori.models import ScoreLog, Route, SaveRoute


@login_required
def mypage_top(request):
    user = request.user
    profile = user.profile
    mylogs = ScoreLog.objects.filter(profile_id=profile.id)
    myroutes = SaveRoute.objects.filter(user_id=profile.id)
    myroute_list = []
    for myroute in myroutes:
        myroute_saved = Route.objects.filter(id=myroute.route.id)
        myroute_list.append(myroute_saved[0])

    mypage_data = {
        'profile': profile,
        'logs': mylogs,
        'saved_routes': myroute_list,
    }

    return render(request, 'sheori/mypage.html', mypage_data)
