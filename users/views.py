# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import *
from .models import *
from django.contrib.auth import logout, login as auth_login
from django.urls import reverse


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        if user_form.is_valid():
            user = user_form.save(commit=False)

            # Autogenerate username from email (e.g., "john.doe")
            base_username = user_form.cleaned_data.get('email').split('@')[0]
            username = base_username
            counter = 1

            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            user.username = username
            user.save()

            messages.success(request, 'Your account has been created!')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserRegisterForm()

    context = {
        'user_form': user_form,
    }
    return render(request, 'users/signup.html', context)



def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomAuthForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)

            try:
                profile = CareerProfile.objects.get(user=user)
                if not profile.is_completed:
                    return redirect('career_profile_onboarding')  # Onboarding
            except CareerProfile.DoesNotExist:
                return redirect('career_profile_onboarding')

            messages.success(request, 'Login successful!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    else:
        form = CustomAuthForm()

    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Logged out successfully!')
    return redirect('home')

@login_required
def dashboard(request):
    profile = None
    profile_complete = False

    if request.user.is_authenticated:
        try:
            profile = CareerProfile.objects.get(user=request.user)
            # Check essential fields
            required_fields = [profile.highest_education, profile.skills, profile.interests]
            profile_complete = all(field.strip() for field in required_fields)
        except CareerProfile.DoesNotExist:
            profile_complete = False

    context = {
        "profile": profile,
        "profile_complete": profile_complete,
        'sidebar_mode': 'dashboard',
    }
    return render(request, "users/dashboard.html", context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('dashboard')  
        
        messages.error(request, "Please correct the errors below.")
    else:
        form = UserUpdateForm(instance=request.user)
        
    
    return render(request, 'users/edit_profile.html', {'form': form})

@login_required
def create_career_profile(request):
    step = request.GET.get('step', '1')

    if step == '1':
        form = EducationForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            request.session['career_profile_step1'] = form.cleaned_data
            return redirect(f"{reverse('career_profile_onboarding')}?step=2")
        template = 'users/onboarding_step1.html'

    elif step == '2':
        post_data = request.POST.copy()
        if 'interests' in post_data:
            post_data.setlist('interests', post_data.get('interests', '').split(',') if post_data.get('interests') else [])
        if 'skills' in post_data:
            post_data.setlist('skills', post_data.get('skills', '').split(',') if post_data.get('skills') else [])

        form = BackgroundForm(post_data or None)
        if request.method == 'POST' and form.is_valid():
            request.session['career_profile_step2'] = form.cleaned_data
            return redirect(f"{reverse('career_profile_onboarding')}?step=3")
        template = 'users/onboarding_step2.html'

    elif step == '3':
        form = GoalsForm(request.POST or None, request.FILES or None)
        if request.method == 'POST' and form.is_valid():
            step1 = request.session.get('career_profile_step1', {})
            step2 = request.session.get('career_profile_step2', {})
            profile_data = {**step1, **step2, **form.cleaned_data}

            profile, created = CareerProfile.objects.get_or_create(user=request.user)
            for key, value in profile_data.items():
                setattr(profile, key, value)
            profile.is_completed = True
            profile.save()

            request.session.pop('career_profile_step1', None)
            request.session.pop('career_profile_step2', None)

            # ✅ Flash success message
            messages.success(request, "🎉 You’ve successfully completed your career profile! Welcome aboard.")

            return redirect('dashboard')
        template = 'users/onboarding_step3.html'

    else:
        return redirect(f"{reverse('career_profile_onboarding')}?step=1")

    progress_map = {'1': 33, '2': 66, '3': 100}
    context = {
        'form': form,
        'step': int(step),
        'progress': progress_map.get(step, 33)
    }
    return render(request, template, context)


from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Count
from .models import IncompleteProfileAccessLog

@staff_member_required
def access_log_dashboard(request):
    logs = IncompleteProfileAccessLog.objects.select_related('user').order_by('-timestamp')[:50]

    top_users = (
        IncompleteProfileAccessLog.objects
        .values('user__username')
        .annotate(attempts=Count('id'))
        .order_by('-attempts')[:5]
    )

    top_paths = (
        IncompleteProfileAccessLog.objects
        .values('attempted_path')
        .annotate(times=Count('id'))
        .order_by('-times')[:5]
    )

    return render(request, "users/access_log_dashboard.html", {
        "logs": logs,
        "top_users": top_users,
        "top_paths": top_paths,
    })
