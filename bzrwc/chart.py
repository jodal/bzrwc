from bzrwc.canvas import Canvas
from bzrwc.data import LineData, ScatterData

PLOT_CHOICES = (
    ('plain', 'Plain'),
    ('spark', 'Spark'),
    ('scatter', 'Punchcard'),
)

class Plot(object):
    margin = 4
    line_width = 2

    width = 450
    height = 150

    background = 'FFFFFF'

    show_axes = True
    show_grid = True
    show_labels = True
    show_title = True

    antialias = True

    def __init__(self, title=None):
        self.top = self.bottom = self.left = self.right= self.margin
        self.canvas = Canvas(self.width, self.height, antialias=self.antialias)

        self.title = title
        self.x_labels = []
        self.y_labels = []
        self.x_spacing = 10
        self.y_spacing = 10
        self.x_max = 10
        self.y_max = 10
        self.continuous = True

    def write(self, data, file):
        if self.show_labels:
            self.left = 40
            self.bottom = 15
            self._adjust_margins(data.x_labels, data.y_labels)

        self._setup_canvas_scale(data.x_max, data.y_max)
        self._draw_background()

        if self.show_grid:
            self._draw_grid(data.x_spacing, data.y_spacing, data.x_max, data.y_max)

        if self.show_axes:
            self._draw_axes(data.x_max, data.y_max)

        if self.show_labels:
            self._draw_labels(data.x_labels, data.y_labels, data.x_spacing, data.y_spacing)

        self.draw(data, width=self.line_width, continuous=data.continuous)

        if self.show_title:
            self._draw_title(self.title, data.x_max, data.y_max)

        self.canvas.write(file)

    def _draw_background(self):
        self.canvas.move(0,0)
        self.canvas.rectangle(self.width, self.height, fill=self.background)

    def _adjust_margins(self, x_labels, y_labels):
        for label in y_labels:
            width, height = self.canvas.text_size(label)

            if width+2*self.margin > self.left:
                self.left = width+2*self.margin

        width, height = self.canvas.font_size()
        if height+self.margin > self.bottom:
            self.bottom = height+self.margin

    def _setup_canvas_scale(self, x_max, y_max):
        sx = (self.width - self.left - self.right)  / float(x_max)
        sy = (self.height - self.top - self.bottom) / float(y_max)
        tx = self.left
        ty = self.height - self.bottom

        self.canvas.scale(sx, sy, tx, ty)
        self.canvas.restore()

    def _draw_axes(self, x_max, y_max, color='BABDB6'):
        self.canvas.scale()
        self.canvas.move(0, y_max)
        self.canvas.line(0, 0)
        self.canvas.line(x_max, 0)
        self.canvas.restore()

        self.canvas.stroke(width=2, color=color, antialias=False)

    def _draw_grid(self, x_spacing, y_spacing, x_max, y_max, color='EEEEEC'):
        self.canvas.scale()

        y_spacing = int(y_spacing) or 1
        for y in xrange(y_spacing, int(y_max), y_spacing):
            self.canvas.move(0, y)
            self.canvas.line(x_max, y)

        x_spacing = int(x_spacing/2) or 1
        for x in xrange(x_spacing, int(x_max), x_spacing):
            self.canvas.move(x, 0)
            self.canvas.line(x, y_max)

        self.canvas.restore()

        self.canvas.stroke(width=1, dash=[3, 2], color=color, antialias=False)

    def _draw_labels(self, x_labels, y_labels, x_spacing, y_spacing, color='555753'):
        for i, label in enumerate(x_labels):
            self.canvas.scale()
            self.canvas.move(i*x_spacing, 0)
            self.canvas.restore()

            if i == 0:
                align = 'left'
                self.canvas.move(-self.margin, 0, relative=True)
            else:
                align = 'center'

            self.canvas.text(label, align=align, valign='top', color=color)

        for i, label in enumerate(y_labels):
            self.canvas.scale()
            self.canvas.move(0, i*y_spacing)
            self.canvas.restore()

            self.canvas.text(label, align='right', valign='middle', color=color)

    def _draw_title(self, title, x_max, y_max, color='555753'):
        self.canvas.scale()
        self.canvas.move(x_max/2, y_max)
        self.canvas.restore()

        self.canvas.text(title, color=color)

    def draw(self, data, color='3465A4', width=2, continuous=True):
        self.canvas.scale()
        self.canvas.move(0, 0)

        for x, y in data:
            if not continuous:
                self.canvas.move(x, 0)
            self.canvas.line(x, y)

        self.canvas.restore()
        self.canvas.stroke(width=width, color=color)

class SparkPlot(Plot):
    margin = 1
    line_width = 1

    height = 15
    width = 100

    show_grid = False
    show_axes = False
    show_labels = False
    show_title = False

    antialias = 'none'

class ScatterPlot(Plot):
    def draw(self, data, color='3465A4', width=2, continuous=True):
        self.canvas.scale()

        for y, row in enumerate(data):
            for x, d in enumerate(row):
                self.canvas.circle(x+1, y+1, d*0.65)

        self.canvas.restore()
