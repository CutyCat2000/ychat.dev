from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from dm.models import DM
from django.contrib.auth.models import User


def home(request):
    if request.user.is_authenticated:
        user = get_object_or_404(User, pk=request.user.id)
        dms = DM.objects.filter(user_1=user) | DM.objects.filter(user_2=user)
        return render(request, "index.html", {"dms": dms})
    return redirect("user/login")
