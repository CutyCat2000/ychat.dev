from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from dm.models import DM
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import config


@login_required
def home(request):
    if request.user.is_authenticated:
        user = get_object_or_404(User, pk=request.user.id)
        dms = DM.objects.filter(user_1=user) | DM.objects.filter(user_2=user)
        return render(request, "index.html", {"dms": dms, "theme": config.DEFAULT_THEME})
    return redirect("user/login/")


def redirecthome(request, exception=301):
    return redirect("home")
