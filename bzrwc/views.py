from django.contrib.auth.models import User
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_page
from django.views.generic.list_detail import object_list, object_detail

from bzrwc.bzrstats import get_bzr_stats
from bzrwc.chart import Plot, SparkPlot, ScatterPlot, PLOT_CHOICES
from bzrwc.data import LineData, ScatterData
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

    plot_type = request.GET.get('plot', 'plain')

    return object_detail(request, Repository.objects.all(),
        slug=repository_slug,
        extra_context={
            'charts': repository.chart_set.select_related(),
            'plot': plot_type,
            'plot_choices': PLOT_CHOICES,
            'unit': unit,
            'unit_choices': Chart.CHART_UNIT_CHOICES,
            'unit_name': Chart.CHART_UNIT_DICT[unit],
        },
        template_name='bzrwc/repository_details.html')

def chart(request, username, repository_slug, chart_slug):
    chart = get_object_or_404(Chart,
        slug=chart_slug,
        repository__slug=repository_slug,
        repository__owner__username=username)

    unit = request.GET.get('unit', Chart.CHART_UNIT_LINES)
    plot_type = request.GET.get('plot', 'plain')

    get_bzr_stats(chart)

    response = HttpResponse(mimetype='image/png')

    if plot_type == 'scatter':
        data = ScatterData(chart, unit)
    else:
        data = LineData(chart, unit)

    title = '%s - %s' % (chart.name, Chart.CHART_UNIT_DICT[unit])

    if plot_type == 'scatter':
        plot = ScatterPlot(title)
    elif plot_type == 'spark':
        plot = SparkPlot(title)
    else:
        plot = Plot(title)

    plot.write(data, response)

    return response
