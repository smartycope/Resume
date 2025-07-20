import re
from pathlib import Path

class SemVer:
    """ Semantic Versioning """
    def __init__(self, text):
        s = text.split('.')
        self.major, self.minor, self.patch = int(s[0]), int(s[1]), int(s[2])
    def __gt__(self, other):
        if self.major > other.major:
            return True
        elif self.major == other.major and self.minor > other.minor:
            return True
        elif self.major == other.major and self.minor == other.minor and self.patch > other.patch:
            return True
        return False
    def __eq__(self, other):
        return self.major == other.major and self.minor == other.minor and self.patch == other.patch
    def __str__(self):
        return f'{self.major}.{self.minor}.{self.patch}'
    def __hash__(self):
        return hash((self.major, self.minor, self.patch))
    __repr__ = __str__

    @staticmethod
    def extract(text):
        match = re.search(r'.*(\d+\.\d+\.\d+).*', text)
        if match:
            return SemVer(match.group(1))
        return None

    def increment(self, amt=1):
        self.patch += amt
        return self

def get_last_version(folder):
    versions = [SemVer.extract(pdf.name) for pdf in Path(folder).expanduser().glob('*.pdf')]
    versions = [v for v in versions if v is not None]
    return max(versions, default=SemVer('0.0.0'))
