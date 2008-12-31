from datetime import datetime, timedelta
import bzrlib.branch
import bzrlib.errors
import re

from bzrwc.models import Revision

def get_bzr_stats(chart):
    stats = []
    summary = {}
    if chart.filter:
        filter = re.compile(chart.filter)
    else:
        filter = None
    if chart.exclude:
        exclude = re.compile(chart.exclude)
    else:
        exclude = None
    try:
        branch = bzrlib.branch.Branch.open(chart.repository.url)
    except bzrlib.errors.NotBranchError:
        return # Just use cached data
    for rev_id in branch.revision_history():
        if chart.revision_set.filter(revision_id=rev_id).count():
            continue # Revision is cached
        num_lines, num_words, num_chars, num_bytes = 0, 0, 0, 0
        rev_no = branch.revision_id_to_revno(rev_id)
        rev = branch.repository.get_revision(rev_id)
        timestamp = datetime.fromtimestamp(rev.timestamp)
        revtree = branch.repository.revision_tree(rev_id)
        for file in revtree.list_files():
            file_name = file[0]
            file_id = file[3]
            # Skip file if matching exclude
            if exclude is not None and re.match(exclude, file_name) is not None:
                continue
            # Skip file if not matching filter
            if filter is not None and re.match(filter, file_name) is None:
                continue
            revtree.lock_read()
            try:
                for line in revtree.get_file_lines(file_id):
                    if len(line.strip()) == 0:
                        continue
                    num_lines += 1
                    # Split on all whitespace
                    num_words += len(line.split(None))
                    num_chars += len(line)
            finally:
                revtree.unlock()
            bytes = revtree.get_file_size(file_id)
            if bytes is not None:
                num_bytes += bytes
        stats.append({
            'rev_id': rev_id,
            'rev_no': rev_no,
            'timestamp': timestamp,
            'num_lines': num_lines,
            'num_words': num_words,
            'num_chars': num_chars,
            'num_bytes': num_bytes,
        })
        revision = Revision(
            revision_id=rev_id,
            revision_no=rev_no,
            timestamp=timestamp,
            num_lines=num_lines,
            num_words=num_words,
            num_chars=num_chars,
            num_bytes=num_bytes)
        chart.revision_set.add(revision)
