import re
import collections

from pygccxml.declarations.matchers import custom_matcher_t

def rename(ns):
    return Renamer.run(ns)

class Renamer(object):
    _containers = {
        'bitset': re.compile(r'bitset<(\d* )\w*>'),
        'array': re.compile(r'array<[^>]*>'),
        'vector': re.compile(r'vector<[^>]*>'),
    }

    @classmethod
    def find(cls, ns):
        containers = collections.defaultdict(list)
        for name, regex in cls._containers.items():
            f = custom_matcher_t(lambda decl: regex.match(decl.name))
            containers[name].extend(ns.classes(f, allow_empty=True))
        return containers

    @classmethod
    def run(cls, ns):
        for name, containers in cls.find(ns).items():
            renamer = getattr(cls, 'rename_' + name, cls.rename)
            for c in containers:
                renamer(c)

    @classmethod
    def rename(cls, c):
        n = c.name
        n = n.replace('unsigned', 'u')
        # uppercase each word
        n = re.sub(r'\b(\w)', lambda m: m.group(1).upper(), n)
        # remove namespaces
        n = re.sub(r'\w+::', '', n)
        # isolate numbers
        n = re.sub(r'\b(\d+)\w*', r'\1', n)
        # remove spaces
        n = re.sub(r'\s+', '', n)
        # remove allocator<...> if same type
        n = re.sub(r'(?i)([^_]+)<([^_]+),allocator<\2>', r'\1<\2', n)
        # replace template chars
        n = re.sub(r'[<>,]+', '_', n)
        # remove duplicates
        n = re.sub(r'([^_]+_)\1', r'\1', n)
        c.rename(re.sub(r'^_+|_+$', '', n))

    @classmethod
    def rename_bitset(cls, c):
        match = cls._containers['bitset'].search(c.name)
        c.rename("Bitset" + match.group(1))
