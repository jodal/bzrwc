import re
from time import time

from bzrwc.models import Revision
from bzrwc.vcs import Branch

MAX_STATS_AGE = 60
_last_updated = {}

def get_bzr_stats(chart):
    if _last_updated.get(chart.id, 0) + MAX_STATS_AGE > time():
        #print "Using cache"
        return

    branch = Branch(chart.repository.url)

    if not branch:
        return # Just use cached data

    filter_re = re.compile(chart.filter or r'.')
    exclude_re = re.compile(chart.exclude or r'^$')

    file_filter = lambda file: (re.search(filter_re, file.name) and
        not re.search(exclude_re, file.name))

    known_revisions = set(chart.revision_set.values_list('revision_id', flat=True))
    revisions = []

    start = time()
    for rev in branch.history:

        if rev.id in known_revisions:
            continue

        revision = get_revision_stats(rev, file_filter)

        revisions.append(revision)

        if len(revisions) > 20:
            print '%f revs/second. Currently at %s' % (20 / float(time() - start), rev.no)
            chart.revision_set.add(*revisions)
            start = time()
            revisions = []

    _last_updated[chart.id] = time()

def get_revision_stats(rev, filter_function):
    num_lines, num_words, num_chars, num_bytes = 0, 0, 0, 0
    files = []

    for file in filter(filter_function, rev.files):
        num_lines += file.lines
        num_words += file.words
        num_chars += file.chars
        num_bytes += file.chars

        files.append(file.name)

    stats = rev.get_stats_for(files)

    return Revision(
        revision_id=rev.id,
        revision_no=rev.no,
        timestamp=rev.timestamp,
        num_lines=num_lines,
        num_words=num_words,
        num_chars=num_chars,
        num_bytes=num_bytes,
        num_files_changed=stats.files_changed, # FIXME only number of matching files changed
        num_additions=stats.additions,
        num_deletions=stats.deletions,)

