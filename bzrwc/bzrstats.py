import re

from bzrwc.models import Revision
from bzrwc.vcs import Branch

def get_bzr_stats(chart):
    branch = Branch(chart.repository.url)

    if not branch:
        return # Just use cached data

    filter_re = re.compile(chart.filter or r'.')
    exclude_re = re.compile(chart.exclude or r'^$')

    file_filter = lambda file: (re.search(filter_re, file.name) and
        not re.search(exclude_re, file.name))

    know_revisions = set(chart.revision_set.values_list('revision_id', flat=True))
    revisions = []

    for i, rev in enumerate(branch.history):
        if rev.id in know_revisions:
            continue

        revision = get_revision_stats(rev, file_filter)
        revision.num_revisions = i

        revisions.append(revision)

    chart.revision_set.add(*revisions)

def get_revision_stats(rev, filter_function):
    num_lines, num_words, num_chars, num_bytes = 0, 0, 0, 0

    for file in filter(filter_function, rev.files):
        num_lines += file.lines
        num_words += file.words
        num_chars += file.chars
        num_bytes += file.chars

    return Revision(
        revision_id=rev.id,
        revision_no=rev.no,
        timestamp=rev.timestamp,
        num_lines=num_lines,
        num_words=num_words,
        num_chars=num_chars,
        num_bytes=num_bytes)
