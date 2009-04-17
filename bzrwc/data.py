import datetime

from bzrwc.utils import pretty_max_number, get_spacing

class LineData(list):
    def __init__(self, chart, unit=None, pretty=True):
        self.continuous = unit in chart.CHART_UNIT_CONTINUOUS

        first_revision = chart.get_first_revision().timestamp
        last_revision = chart.get_last_revision().timestamp

        total_days = (last_revision - first_revision).days

        for rev in chart.revision_set.all():
            x = (rev.timestamp - first_revision).days
            y = rev.get_num(unit)

            self.append([x,y])

        if pretty:
            self.x_max = pretty_max_number((last_revision - first_revision).days)
            self.y_max = pretty_max_number(chart.get_max_num(unit))
        else:
            self.x_max = (last_revision - first_revision).days
            self.y_max = chart.get_max_num(unit)

        self.x_spacing = total_days / 3.0
        self.y_spacing = get_spacing(self.y_max)

        self.x_labels = []
        self.y_labels = xrange(0, int(self.y_max+1), int(self.y_spacing) or 1)

        for i in xrange(0, int(self.x_max+1), int(self.x_spacing)):
            self.x_labels.append((first_revision + datetime.timedelta(days=i)).date())

class ScatterData(LineData):
    def __init__(self, chart, unit=None):
        self.continuous = unit in chart.CHART_UNIT_CONTINUOUS

        self.x_max = 25
        self.y_max = 8

        self.x_spacing = 1
        self.y_spacing = 1

        self.x_labels = ['', '00', '', '02', '', '04', '', '06', '', '08', '', '10',
            '', '12', '', '14', '', '16', '', '18', '', '20', '', '22', '']
        self.y_labels = ['', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun', '']

        for a in xrange(7):
            self.append([0 for b in xrange(24)])

        max = 1
        for rev in chart.revision_set.all():
            hour = rev.timestamp.hour
            day  = rev.timestamp.weekday()

            # FIXME
            if unit != 'r':
                self[day][hour] += rev.get_num(unit)
            else:
                self[day][hour] += 1

            if self[day][hour] > max:
                max = self[day][hour]

        max = float(max)
        for a in xrange(7):
            for b in xrange(24):
                self[a][b] /= max
