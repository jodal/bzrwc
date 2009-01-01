import locale
from pygooglechart import XYLineChart, Axis

MIN_VALUE = 0
MAX_VALUE = 61

def get_gchart(chart, unit):
    # Unit
    unit_name = dict(chart.CHART_UNIT_CHOICES).get(unit, 'none').lower()

    # Chart
    gchart = XYLineChart(800, 375)
    gchart.set_colours(('3465a4', '73d216', 'fb7900', 'edd400', 'cc0000',
        'c17d11', '75507b'))
    gchart.set_line_style(0, 2)

    # X axis
    gchart.set_axis_range(Axis.BOTTOM, 0, chart.get_number_of_days())
    axis_label = 'Days (%s - %s)' % (
        chart.get_first_revision().timestamp.strftime('%Y-%m-%d'),
        chart.get_last_revision().timestamp.strftime('%Y-%m-%d'))
    axis_index = gchart.set_axis_labels(Axis.BOTTOM, (axis_label,))
    gchart.set_axis_positions(axis_index, (50,))

    # Y axis
    gchart.set_axis_range(Axis.LEFT, 0, 100)
    axis_index = gchart.set_axis_labels(Axis.LEFT, ('%',))
    gchart.set_axis_positions(axis_index, (100,))
    gchart.set_grid(0, 20, 1, 5)

    # Data
    days_max = chart.get_number_of_days()
    days_data = []
    curve_max = eval('chart.get_max_num_%s()' % unit_name)
    if curve_max == 0:
        curve_max = 1
    curve_data = []
    for rev in chart.revision_set.all():
        # Time/date data
        diff = (rev.timestamp - chart.get_first_revision().timestamp)
        diff_days = int((diff.days + diff.seconds / 86000.0) * 100)
        diff_scaled = diff_days * MAX_VALUE // (days_max * 100)
        days_data.append(diff_scaled)
        # Curve data
        curve = eval('rev.num_%s' % unit_name)
        curve_scaled = curve * MAX_VALUE // curve_max
        curve_data.append(curve_scaled)
    gchart.add_data(days_data)
    gchart.add_data(curve_data)

    # Title
    locale.setlocale(locale.LC_ALL, 'en_DK.UTF-8')
    curve_max = locale.format('%d', curve_max, grouping=True)
    gchart.set_title('%s (100%% is %s %s)' %
        (chart.name, curve_max, unit_name))

    return gchart
