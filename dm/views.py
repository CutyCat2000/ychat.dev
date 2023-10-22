from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import DM
from django.contrib.auth.models import User
import config
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

# Create your views here.


@login_required
def dm_view(request, dm_id):
    # Retrieve the DM object from the database based on dm_id
    dm = get_object_or_404(DM, pk=dm_id)

    # Retrieve the current authenticated user and their associated DMs
    user = get_object_or_404(User, pk=request.user.id)
    dms = DM.objects.filter(user_1=user) | DM.objects.filter(user_2=user)

    # Check if the current user has access to the requested DM
    if dm not in dms:
        return HttpResponseForbidden("Access to this DM is denied.")

    messages = dm.messages.order_by('-timestamp')[:250]
    return render(request, "index.html", {
        "dm": dm,
        "dms": dms,
        "dm_messages": messages,
        "theme": config.DEFAULT_THEME,
    })


@login_required
def dm_create(request, user_id):
    # Retrieve the user objects from the database
    try:
        user_1 = User.objects.get(
            pk=request.user.id)  # The current authenticated user
        user_2 = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        # Handle the case where the user does not exist
        return JsonResponse({"error": "User not found."}, status=404)

    # Check if user_1 is the same as user_2 (DM to self)
    if user_1 == user_2:
        return JsonResponse({"error": "Creating DM to self is not allowed."},
                            status=400)

    # Check if a DM already exists between the users
    existing_dm = DM.objects.filter(user_1=user_1, user_2=user_2).first()
    if existing_dm:
        # Redirect to the existing DM view
        return redirect("dm_view", dm_id=existing_dm.id)

    # Create the DM object
    dm = DM.objects.create(user_1=user_1, user_2=user_2)

    # Redirect to the newly created DM view
    return redirect("dm_view", dm_id=dm.id)
