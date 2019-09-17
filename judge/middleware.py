from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse, resolve, Resolver404
from django.utils.http import urlquote

from django.utils import timezone
from judge.models import Contest, ContestParticipation

def join_contest_helper(request, profile):
    if profile.current_contest is not None:
        return False

    # !CONTEST
    contest = Contest.objects.all()[0]

    if not contest.can_join and not request.user.is_superuser:
        return False

    if not request.user.is_superuser and contest.banned_users.filter(id=profile.id).exists():
        return False

    if contest.ended:
        return False
    else:
        participation = ContestParticipation.objects.get_or_create(
            contest=contest, user=profile, virtual=(-1 if request.user.is_superuser else 0),
            defaults={
                'real_start': timezone.now()
            }
        )[0]

    profile.current_contest = participation
    profile.save()

    contest._updating_stats_only = True
    contest.update_user_count()

    return True


class ShortCircuitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            callback, args, kwargs = resolve(request.path_info, getattr(request, 'urlconf', None))
        except Resolver404:
            callback, args, kwargs = None, None, None

        if getattr(callback, 'short_circuit_middleware', False):
            return callback(request, *args, **kwargs)
        return self.get_response(request)


class DMOJLoginMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            profile = request.profile = request.user.profile
        else:
            request.profile = None
        return self.get_response(request)


class DMOJImpersonationMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_impersonate:
            request.profile = request.user.profile
        return self.get_response(request)


class ContestMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        profile = request.profile
        if profile:
            join_contest_helper(request, profile)

            profile.update_contest()
            request.participation = profile.current_contest
            request.in_contest = request.participation is not None
        else:
            request.in_contest = False
            request.participation = None
        return self.get_response(request)
