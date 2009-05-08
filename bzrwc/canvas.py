import math
import cairo

class Canvas(object):
    def __init__(self, width, height, antialias=None):
        self.surface = self._get_surface(width, height)
        self.context = self._get_context(self.surface, antialias)

        self.width = width
        self.height = height

        self.matrix = self.context.get_matrix()
        self.scale_matrix = self.matrix

    def scale(self, sx=None, sy=None, tx=None, ty=None):
        if (sx and sy and tx and ty):
            self.context.translate(tx, ty)
            self.context.scale(sx, -sy)
            self.scale_matrix = self.context.get_matrix()
        else:
            self.context.set_matrix(self.scale_matrix)

    def restore(self):
        self.context.set_matrix(self.matrix)

    def move(self, x, y, relative=False):
        if relative:
            self.context.rel_move_to(x,y)
        else:
            self.context.move_to(x,y)

    def line(self, x, y, relative=False):
        if relative:
            self.context.rel_line_to(x,y)
        else:
            self.context.line_to(x,y)

    def text(self, string, color='000000', width=1, align='center',
            valign=None, padding=4):

        string = unicode(string)

        width, height = self.text_size(string)

        self.text_align(align, width, height, padding)
        self.text_valign(valign, width, height, padding)

        self.keep_on_canvas(width, height, padding)

        self.color(color)
        self.context.set_line_width(width)
        self.context.show_text(string)

    def text_size(self, string):
        string = unicode(string)
        return self.context.text_extents(string)[2:4]

    def text_align(self, align, width, height, padding=4):
        if align == 'center':
            self.move(-width/2.0, 0, relative=True)
        elif align == 'right':
            self.move(-width-padding, 0, relative=True)
        else:
            self.move(padding, 0, relative=True)

    def text_valign(self, valign, width, height, padding=4):
        if valign == 'top':
            self.move(0, height + padding, relative=True)
        elif valign == 'middle':
            self.move(0, height/2, relative=True)
        elif valign == 'baseline':
            self.move(0, 0, relative=True)
        else:
            self.move(0, height, relative=True)

    def keep_on_canvas(self, width, height, padding=4):
        x, y = self.context.get_current_point()

        if x-padding < 0:
            self.move(padding-x, 0, relative=True)
        elif x+width+padding > self.width:
            self.move(self.width - (x+width+padding), 0, relative=True)

        if y-padding-height < 0:
            self.move(0, padding+height-y, relative=True)
        elif y+padding > self.height:
            self.move(0, self.height - (y+padding), relative=True)

    def font_size(self):
        return self.context.font_extents()[2:4]

    def rectangle(self, w, h, fill='FFFFFF'):
        self.color(fill)
        self.line(0, h, relative=True)
        self.line(w, 0, relative=True)
        self.line(0, -h, relative=True)
        self.context.fill()

    def circle(self, x, y, r, fill='3465A4C0'):
        self.color(fill)
        self.context.arc(x, y, r, 0, 2*math.pi)
        self.context.fill()

    def stroke(self, color='000000', width=1, dash=[], antialias=True):
        self.context.set_dash(dash)
        self.context.set_line_width(width)
        self.color(color)

        if not antialias:
            self.disable_antialias()

        self.context.stroke()

        if not antialias:
            self.restore_antialias()

    def color(self, color='000000', alpha=1.0):
        color += 'F' * (8-len(color))

        self.context.set_source_rgba(
            int(color[0:2], 16) / 255.0,
            int(color[2:4], 16) / 255.0,
            int(color[4:6], 16) / 255.0,
            int(color[6:8], 16) / 255.0,
        )

    def write(self, file):
        self.surface.write_to_png(file)

    def disable_antialias(self):
        self.antialias = self.context.get_antialias()
        self.context.set_antialias(cairo.ANTIALIAS_NONE)

    def restore_antialias(self):
        self.context.set_antialias(self.antialias)

    def _get_surface(self, width, height):
        return cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)

    def _get_context(self, surface, antialias=False):
        context = cairo.Context(surface)
        context.set_line_join(cairo.LINE_JOIN_ROUND)
        context.set_line_cap(cairo.LINE_CAP_ROUND)

        if antialias == 'none':
            context.set_antialias(cairo.ANTIALIAS_NONE)
        else:
            context.set_antialias(cairo.ANTIALIAS_DEFAULT)

        return context

