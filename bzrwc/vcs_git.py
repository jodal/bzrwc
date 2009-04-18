import git

class Branch(object):
    def __init__(self, url):
        self.repo = git.Repo(url)

    def __bool__(self):
        return bool(getattr(self, 'repo', False))

    @property
    def history(self):
        for commit in self.repo.commits():
            yield Revision(commit)

class Revision(object):
    def __init__(self, commit):
        self.commit = commit

    @property
    def id(self):
        return self.commit.id

    @property
    def no(self):
        return self.commit.id_abbrev

    @property
    def timestamp(self):
        return self.commit.committed_date # FIXME convert to datetime

    @property
    def author(self):
        return self.commit.author.name

    @property
    def stats(self):
        # FIXME should be attributes not a dict...
        return {'additions': self.commit.stats.total['insertions'],
                'deleteions': self.commit.stats.total['deletions'],
                'changed_files': self.commit.stats.total['files'],
            }

    @property
    def files(self):
        return self._flatten(self.commit.tree)

    def _flatten(self, tree):
        for leaf in tree.values():
            if isinstance(leaf, git.Blob):
                yield File(leaf)
            else:
                for inner_leaf in self._flatten(leaf):
                    yield inner_leaf

class File(object):
    # FIXME decide what to keep track of
    def __init__(self, blob):
        self.blob = blob

        self.name = blob.name
        self.lines = 0
        self.words = 0
        self.chars = 0

        self.count()

    @property
    def bytes(self):
        return self.blob.size

    def count(self):
        for line in self.blob.data.split('\n'):
            if not line.strip():
                continue

            self.lines += 1
            self.words += len(line.split())
            self.chars += len(line)
