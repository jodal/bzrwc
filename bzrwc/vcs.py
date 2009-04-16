from datetime import datetime
import bzrlib.branch
import bzrlib.errors

class Branch(object):
    def __init__(self, url):
        try:
            self.branch = bzrlib.branch.Branch.open(url)
        except bzrlib.errors.NotBranchError:
            self.branch = None

    def __bool__(self):
        return bool(getattr(self, 'branch', False))

    @property
    def history(self):
        for rev_id in self.branch.revision_history():
            yield Revision(self.branch, rev_id)

class Revision(object):
    def __init__(self, branch, rev_id):
        self.branch = branch
        self.rev_id = rev_id
        self.revtree = branch.repository.revision_tree(rev_id)

    @property
    def id(self):
        return self.rev_id

    @property
    def no(self):
        return self.branch.revision_id_to_revno(self.rev_id)

    @property
    def timestamp(self):
        rev = self.branch.repository.get_revision(self.id)
        return datetime.fromtimestamp(rev.timestamp+rev.timezone)

    @property
    def author(self):
        rev = self.branch.repository.get_revision(self.id)
        return rev.get_apparent_author()

    @property
    def files(self):
        for file in self.revtree.list_files():
            file_name = file[0]
            file_id = file[3]

            yield File(self.revtree, file_name, file_id)

class File(object):
    def __init__(self, revtree, file_name, file_id):
        self.name = file_name
        self.lines = 0
        self.words = 0
        self.chars = 0

        self.revtree = revtree
        self.file_id = file_id

        self.count()

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
