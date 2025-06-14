from users.models import CareerProfile, IncompleteProfileAccessLog
from django.urls import reverse
from django.shortcuts import redirect


class AttachCareerProfileMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        if not request.user.is_authenticated:
            return self.get_response(request)

        if not hasattr(request, 'career_profile'):
            try:
                request.career_profile = CareerProfile.objects.get(user=request.user)
            except CareerProfile.DoesNotExist:
                request.career_profile = None

        safe_paths = [
            reverse('edit_profile'),
            reverse('logout'),
            reverse('login'),
            reverse('register'),
            '/',
        ]

        protected_paths = [
            '/chat',
            '/dashboard',
            '/search',
            '/recommendations',
            '/courses',
            '/career-advice',
        ]

        if path.startswith('/admin/') or path in safe_paths:
            return self.get_response(request)

        for protected in protected_paths:
            if path.startswith(protected):
                profile = request.career_profile
                if not profile or not (
                    profile.highest_education and profile.skills and profile.interests
                ):
                    # ✅ LOG THE ATTEMPT
                    ip = self.get_client_ip(request)
                    agent = request.META.get('HTTP_USER_AGENT', '')

                    IncompleteProfileAccessLog.objects.create(
                        user=request.user,
                        attempted_path=path,
                        ip_address=ip,
                        user_agent=agent
                    )

                    from django.contrib import messages
                    messages.warning(request, "Complete your career profile to access this page.")
                    return redirect('edit_profile')

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
