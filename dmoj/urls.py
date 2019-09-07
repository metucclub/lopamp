# coding: utf-8
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from django.core.urlresolvers import reverse
from django.http import HttpResponsePermanentRedirect
from django.utils.translation import ugettext_lazy as _
from social_django.urls import urlpatterns as social_auth_patterns

from judge.feed import CommentFeed, AtomCommentFeed, BlogFeed, AtomBlogFeed, ProblemFeed, AtomProblemFeed
from judge.forms import CustomAuthenticationForm
from judge.sitemap import ProblemSitemap, UserSitemap, HomePageSitemap, UrlSitemap, ContestSitemap, OrganizationSitemap, \
    BlogPostSitemap, SolutionSitemap
from judge.views import TitledTemplateView
from judge.views import organization, language, status, blog, problem, mailgun, license, register, user, \
    submission, widgets, comment, contests, api, ranked_submission, stats, preview, ticket
from judge.views.problem_data import ProblemDataView, ProblemSubmissionDiff, \
    problem_data_file, problem_init_view
from judge.views.register import RegistrationView, ActivationView
from judge.views.select2 import UserSelect2View, OrganizationSelect2View, ProblemSelect2View, CommentSelect2View, \
    ContestSelect2View, UserSearchSelect2View, ContestUserSearchSelect2View, TicketUserSelect2View, AssigneeSelect2View

admin.autodiscover()

register_patterns = [
    url(r'^login/$', contests.LoginContestJoin.as_view(
        template_name='registration/login.html',
        extra_context={'title': ""},
        authentication_form=CustomAuthenticationForm,
    ), name='auth_login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='auth_logout'),
]

def exception(request):
    raise RuntimeError('@Xyene asked me to cause this')

def paged_list_view(view, name):
    return include([
        url(r'^$', view.as_view(), name=name),
        url(r'^(?P<page>\d+)$', view.as_view(), name=name),
    ])

urlpatterns = [
    url(r'^$', contests.ContestDetail.as_view(), name='contest_view'),
    url(r'^scoreboard/$', contests.contest_ranking, name='contest_ranking'),
    url(r'^scoreboard/ajax$', contests.contest_ranking_ajax, name='contest_ranking_ajax'),
    url(r'^join$', contests.ContestJoin.as_view(), name='contest_join'),

    url(r'^submissions/', paged_list_view(submission.AllSubmissions, 'all_submissions')),
    url(r'^submissions/user/(?P<team_slug>[-\w]+)/', paged_list_view(submission.AllUserSubmissions, 'all_user_submissions')),

    url(r'^/$', lambda _, contest: HttpResponsePermanentRedirect(reverse('contest_view', args=[contest]))),

    url(r'^500/$', exception),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include(register_patterns)),

    url(r'^problem/(?P<problem>[^/]+)', include([
        url(r'^$', problem.ProblemDetail.as_view(), name='problem_detail'),
        url(r'^/submit$', problem.problem_submit, name='problem_submit'),
        url(r'^/resubmit/(?P<submission>\d+)$', problem.problem_submit, name='problem_submit'),

        url(r'^/submissions/', paged_list_view(submission.ProblemSubmissions, 'chronological_submissions')),
        url(r'^/submissions/(?P<team_slug>[-\w]+)/', paged_list_view(submission.UserProblemSubmissions, 'user_submissions')),
        url(r'^/$', lambda _, problem: HttpResponsePermanentRedirect(reverse('problem_detail', args=[problem]))),

        url(r'^/test_data$', ProblemDataView.as_view(), name='problem_data'),
        url(r'^/test_data/init$', problem_init_view, name='problem_data_init'),
        url(r'^/test_data/diff$', ProblemSubmissionDiff.as_view(), name='problem_submission_diff'),
        url(r'^/data/(?P<path>.+)$', problem_data_file, name='problem_data_file'),
    ])),

    url(r'^src/(?P<submission>\d+)$', submission.SubmissionSource.as_view(), name='submission_source'),
    url(r'^src/(?P<submission>\d+)/raw$', submission.SubmissionSourceRaw.as_view(), name='submission_source_raw'),

    url(r'^submission/(?P<submission>\d+)', include([
        url(r'^$', submission.SubmissionStatus.as_view(), name='submission_status'),
        url(r'^/abort$', submission.abort_submission, name='submission_abort'),
        url(r'^/html$', submission.single_submission),
    ])),

    url(r'^user/(?P<team_slug>[-\w]+)', include([
        url(r'^/submissions/', paged_list_view(submission.AllUserSubmissions, 'all_user_submissions_old')),
        url(r'^/submissions/', lambda _, user: HttpResponsePermanentRedirect(reverse('all_user_submissions', args=[user]))),
    ])),

    url(r'^widgets/', include([
        url(r'^rejudge$', widgets.rejudge_submission, name='submission_rejudge'),
        url(r'^single_submission$', submission.single_submission_query, name='submission_single_query'),
        url(r'^submission_testcases$', submission.SubmissionTestCaseQuery.as_view(), name='submission_testcases_query'),
        url(r'^detect_timezone$', widgets.DetectTimezone.as_view(), name='detect_timezone'),
        url(r'^status-table$', status.status_table, name='status_table'),

        url(r'^template$', problem.LanguageTemplateAjax.as_view(), name='language_template_ajax'),

        url(r'^preview/', include([
            url(r'^problem$', preview.ProblemMarkdownPreviewView.as_view(), name='problem_preview'),
            url(r'^blog$', preview.BlogMarkdownPreviewView.as_view(), name='blog_preview'),
            url(r'^contest$', preview.ContestMarkdownPreviewView.as_view(), name='contest_preview'),
            url(r'^comment$', preview.CommentMarkdownPreviewView.as_view(), name='comment_preview'),
            url(r'^profile$', preview.ProfileMarkdownPreviewView.as_view(), name='profile_preview'),
            url(r'^organization$', preview.OrganizationMarkdownPreviewView.as_view(), name='organization_preview'),
            url(r'^solution$', preview.SolutionMarkdownPreviewView.as_view(), name='solution_preview'),
            url(r'^license$', preview.LicenseMarkdownPreviewView.as_view(), name='license_preview'),
            url(r'^ticket$', preview.TicketMarkdownPreviewView.as_view(), name='ticket_preview'),
        ])),
    ])),

    url(r'^runtimes/$', language.LanguageList.as_view(), name='runtime_list'),
    url(r'^runtimes/matrix/$', status.version_matrix, name='version_matrix'),
    url(r'^status/$', status.status_all, name='status_all'),

    url(r'^sitemap\.xml$', sitemap, {'sitemaps': {
        'problem': ProblemSitemap,
        'user': UserSitemap,
        'home': HomePageSitemap,
        'contest': ContestSitemap,
        'organization': OrganizationSitemap,
        'blog': BlogPostSitemap,
        'solutions': SolutionSitemap,
        'pages': UrlSitemap([
            {'location': '/about/', 'priority': 0.9},
        ]),
    }}),

    url(r'^judge-select2/', include([
        url(r'^profile/$', UserSelect2View.as_view(), name='profile_select2'),
        url(r'^organization/$', OrganizationSelect2View.as_view(), name='organization_select2'),
        url(r'^problem/$', ProblemSelect2View.as_view(), name='problem_select2'),
        url(r'^contest/$', ContestSelect2View.as_view(), name='contest_select2'),
        url(r'^comment/$', CommentSelect2View.as_view(), name='comment_select2'),
    ])),
]

favicon_paths = ['apple-touch-icon-180x180.png', 'apple-touch-icon-114x114.png', 'android-chrome-72x72.png',
                 'apple-touch-icon-57x57.png', 'apple-touch-icon-72x72.png', 'apple-touch-icon.png', 'mstile-70x70.png',
                 'android-chrome-36x36.png', 'apple-touch-icon-precomposed.png', 'apple-touch-icon-76x76.png',
                 'apple-touch-icon-60x60.png', 'android-chrome-96x96.png', 'mstile-144x144.png', 'mstile-150x150.png',
                 'safari-pinned-tab.svg', 'android-chrome-144x144.png', 'apple-touch-icon-152x152.png',
                 'favicon-96x96.png',
                 'favicon-32x32.png', 'favicon-16x16.png', 'android-chrome-192x192.png', 'android-chrome-48x48.png',
                 'mstile-310x150.png', 'apple-touch-icon-144x144.png', 'browserconfig.xml', 'manifest.json',
                 'apple-touch-icon-120x120.png', 'mstile-310x310.png']


from django.templatetags.static import static
from django.utils.functional import lazystr
from django.views.generic import RedirectView

for favicon in favicon_paths:
    urlpatterns.append(url(r'^%s$' % favicon, RedirectView.as_view(
        url=lazystr(lambda: static('icons/' + favicon))
    )))

handler404 = 'judge.views.error.error404'
handler403 = 'judge.views.error.error403'
handler500 = 'judge.views.error.error500'

if 'newsletter' in settings.INSTALLED_APPS:
    urlpatterns.append(url(r'^newsletter/', include('newsletter.urls')))
if 'impersonate' in settings.INSTALLED_APPS:
    urlpatterns.append(url(r'^impersonate/', include('impersonate.urls')))
