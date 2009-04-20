import os
from time import time
from datetime import datetime

import bzrlib.branch
import bzrlib.errors
from bzrlib.diff import show_diff_trees
from bzrlib.builtins import cmd_checkout, cmd_remove_tree, cmd_update

checkout = cmd_checkout().run
remove_tree = cmd_remove_tree().run
update = cmd_update().run

MAX_REMOTE_AGE = 60

_last_updated = {}

class Branch(object):
    def __init__(self, url):
        self.url = url

        if not url.startswith('file'):
            print "Handle remote branch"

            self.url = '/var/tmp/bzrwc/%s' %  url.rstrip('/').replace('://', '-').replace('/', '_')

            if _last_updated.get(url, 0) + MAX_REMOTE_AGE > time():
                # FIXME proper logging
                print "Updatet within last minute"
            else:
                if not os.path.exists(self.url):
                    checkout(branch_location=url, to_location=self.url)
                    print "Imported branch"
                else:
                    update(self.url)
                    print "Updated branch"

                _last_updated[url] = time()

        try:
            self.branch = bzrlib.branch.Branch.open(self.url)
        except bzrlib.errors.NotBranchError:
            self.branch = None

    def __repr__(self):
        return "<%s.%s object '%s'>" % (self.__class__.__module__, self.__class__.__name__, self.url)

    def __bool__(self):
        return bool(getattr(self, 'branch', False))

    @property
    def history(self):
        prev_id = None
        for rev_id in self.branch.revision_history():
            yield Revision(self.branch, rev_id, prev_id)
            prev_id = rev_id

class Revision(object):
    def __init__(self, branch, rev_id, prev_id):
        self.branch = branch
        self.rev_id = rev_id
        self.prev_id = prev_id
        self._revtree = None
        self._prev_revtree = None
        self._stats = None

    def __repr__(self):
        return "<%s.%s object '%s'>" % (self.__class__.__module__, self.__class__.__name__, self.id)

    @property
    def revtree(self):
        if not self._revtree:
            self._revtree = self._get_revtree(self.rev_id)
        return self._revtree

    @property
    def id(self):
        return self.rev_id

    @property
    def no(self):
        return self.branch.revision_id_to_revno(self.rev_id)

    @property
    def timestamp(self):
        rev = self.branch.repository.get_revision(self.id)
        return datetime.utcfromtimestamp(rev.timestamp+rev.timezone)

    @property
    def author(self):
        rev = self.branch.repository.get_revision(self.id)
        return rev.get_apparent_author()

    @property
    def files(self):
        for file in self.revtree.list_files():
            file_type = file[2]
    
            if file_type != 'file':
                continue

            file_name = file[0]
            file_id = file[3]

            yield File(self.revtree, file_name, file_id)

    @property
    def stats(self):
        if not self._stats:
            s = DiffStat()
            prev_revtree = self._get_revtree(self.prev_id)
            show_diff_trees(prev_revtree, self.revtree, s)

            self._stats = s

        return self._stats

    def get_stats_for(self, files=[]):
        s = DiffStat()
        prev_revtree = self._get_revtree(self.prev_id)
        show_diff_trees(prev_revtree, self.revtree, s, files)
        return s

    def _get_revtree(self, rev_id):
        return self.branch.repository.revision_tree(rev_id)

class File(object):
    def __init__(self, revtree, file_name, file_id):
        self.name = file_name
        self.lines = 0
        self.words = 0
        self.chars = 0

        self.revtree = revtree
        self.file_id = file_id

        self.count()

    def __repr__(self):
        return "<%s.%s object '%s'>" % (self.__class__.__module__, self.__class__.__name__, self.name)

    @property
    def bytes(self):
        return self.revtree.get_file_size(self.file_id) or 0

    def count(self):
        for line in self.get_lines():
            if not line.strip():
                continue

            self.lines += 1
            self.words += len(line.split())
            self.chars += len(line)

    def get_lines(self):
        self.revtree.lock_read()
        try:
            lines = self.revtree.get_file_lines(self.file_id)
        finally:
            self.revtree.unlock()

        return lines

class DiffStat:
    def __init__(self):
        self.additions = 0
        self.deletions = 0
        self.files_changed = 0

    def write(self, diff_string):
        for line in diff_string.split('\n'):
            if line.startswith('+') and not line.startswith('+++'):
                self.additions += 1
            if line.startswith('-') and not line.startswith('---'):
                self.deletions += 1
            elif line.startswith('---'):
                self.files_changed += 1

