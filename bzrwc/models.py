from django.db import models

from django.contrib.auth.models import User

class Repository(models.Model):
    name = models.CharField(max_length=100,
        help_text='Name of the repository.')
    slug = models.SlugField(help_text='Short name for URLs, etc.')
    url = models.CharField(max_length=200, verbose_name='URL',
        help_text='URL (e.g., file://, http://, sftp://) to the repository.')
    owner = models.ForeignKey(User,
        help_text='Owner of the repository.')

    class Meta:
        verbose_name_plural = 'repositories'
        ordering = ('name',)

    def __unicode__(self):
        return u'%s: %s' % (self.owner, self.slug)

class Chart(models.Model):
    CHART_UNIT_LINES = 'l'
    CHART_UNIT_WORDS = 'w'
    CHART_UNIT_CHARS = 'c'
    CHART_UNIT_BYTES = 'b'
    CHART_UNIT_CHOICES = (
        (CHART_UNIT_LINES, 'Lines'),
        (CHART_UNIT_WORDS, 'Words'),
        (CHART_UNIT_CHARS, 'Chars'),
        (CHART_UNIT_BYTES, 'Bytes'),
    )

    repository = models.ForeignKey(Repository,
        help_text='What repository to get chart data from.')
    name = models.CharField(max_length=100, help_text='Name of the chart.')
    slug = models.SlugField(help_text='Short name for URLs, etc.')
    filter = models.CharField(max_length=100, blank=True,
        help_text='Regexp the filepath must match.')
    exclude = models.CharField(max_length=100, blank=True,
        help_text='Regexp the filepath must not match.')

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return u'%s: %s' % (self.repository, self.name)

    def save(self):
        self.revision_set.all().delete()
        super(Chart, self).save()

    def get_first_revision(self):
        return self.revision_set.all().order_by('timestamp')[0]

    def get_last_revision(self):
        return self.revision_set.all().order_by('-timestamp')[0]

    def get_number_of_days(self):
        return (self.get_last_revision().timestamp
            - self.get_first_revision().timestamp).days + 1

    def get_max_num_lines(self):
        return self.revision_set.all().order_by('-num_lines')[0].num_lines

    def get_max_num_words(self):
        return self.revision_set.all().order_by('-num_words')[0].num_words

    def get_max_num_chars(self):
        return self.revision_set.all().order_by('-num_chars')[0].num_chars

    def get_max_num_bytes(self):
        return self.revision_set.all().order_by('-num_bytes')[0].num_bytes

    def get_max_num(self, key):
        if key in Chart.CHART_UNIT_DICT:
            unit = Chart.CHART_UNIT_DICT[key].lower()
            return eval('self.get_max_num_%s()' % unit)
        else:
            return self.get_max_num_lines()

class Revision(models.Model):
    chart = models.ForeignKey(Chart)
    revision_id = models.CharField(max_length=100)
    revision_no = models.CharField(max_length=100)
    timestamp = models.DateTimeField()
    num_lines = models.IntegerField()
    num_words = models.IntegerField()
    num_chars = models.IntegerField()
    num_bytes = models.IntegerField()

    class Meta:
        ordering = ('timestamp',)

    def __unicode__(self):
        return u'%s: r%s' % (self.chart, self.revision_no)

    def get_num(self, key):
        if key in Chart.CHART_UNIT_DICT:
            unit = Chart.CHART_UNIT_DICT[key].lower()
            return eval('self.num_%s' % unit)
        else:
            return self.num_lines
        
