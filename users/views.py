from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import RoomAssignmentLog
from django.http import JsonResponse
from review.models import Room


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created. You are now able to login.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            # Get previous room before saving
            previous_room = request.user.profile.assigned_room

            # Save the forms
            u_form.save()
            p_form.save()  # This now works because we set queryset to all rooms

            # Get the selected new room
            new_room = request.user.profile.assigned_room

            # Log room changes if room was changed
            if previous_room != new_room:
                RoomAssignmentLog.objects.create(
                    user=request.user,
                    previous_room=previous_room,
                    new_room=new_room
                )

                # Create a message about the room change
                if new_room:
                    room_msg = f" Your assigned room is now: {new_room}."
                else:
                    room_msg = " Your room assignment has been removed."

                messages.success(request, f'Your account has been updated.{room_msg}')
            else:
                messages.success(request, f'Your account has been updated.')

            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
    }

    return render(request, 'users/profile.html', context)


def get_rooms(request):
    """API endpoint to fetch rooms for a specific dorm"""
    dorm_id = request.GET.get('dorm_id')
    if not dorm_id:
        return JsonResponse({'rooms': []})

    rooms = Room.objects.filter(dorm_id=dorm_id).order_by('room_number')
    room_data = [{'id': room.id, 'room_number': room.room_number, 'floor': room.floor} for room in rooms]

    return JsonResponse({'rooms': room_data})
