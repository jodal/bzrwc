from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list, object_detail

from bzrwc.bzrstats import get_bzr_stats
from bzrwc.gchart import get_gchart
from bzrwc.models import Repository, Chart

def repository_list(request, username=None):
    if username is not None:
        users = User.objects.filter(username=username)
    else:
        users = User.objects.all()
    return object_list(request, users,
        template_name='bzrwc/repository_list.html')

def repository_details(request, username, repository_slug):
    user = get_object_or_404(User, username=username)
    repository = get_object_or_404(Repository, owner=user, slug=repository_slug)

    unit = request.GET.get('unit', Chart.CHART_UNIT_LINES)
    if unit not in dict(Chart.CHART_UNIT_CHOICES).keys():
        raise Http404

    charts = []
    for chart in repository.chart_set.all().select_related():
        get_bzr_stats(chart)
        gchart = get_gchart(chart, unit)
        setattr(chart, 'image_url', gchart.get_url())
        charts.append(chart)

    return object_detail(request, Repository.objects.all(),
        slug=repository_slug,
        extra_context={
            'charts': charts,
        },
        template_name='bzrwc/repository_details.html')

