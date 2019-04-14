from django.http import HttpResponse
from judge.models import Contest
from judge.utils.views import generic_message
from django.contrib.auth import logout

class ContestMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            profile = request.user.profile
            profile.update_contest()
            request.participation = profile.current_contest
            request.in_contest = request.participation is not None
        else:
            request.in_contest = False
            request.participation = None
        return self.get_response(request)

class NoLoginUntilContestMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.get_full_path().startswith('/admin') or request.get_full_path() == '/' or (request.user is not None and request.user.is_superuser):
            return self.get_response(request)
        elif Contest.objects.count() > 0:
            contest = Contest.objects.all()[0]

            if contest.can_join:
                return self.get_response(request)

        if request.user is not None:
            logout(request)

        return generic_message(request, u"Contest has not started yet.", "")