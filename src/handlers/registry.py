from collections import defaultdict

from . import *

store = defaultdict()

for hd in [StartHandler, ResolveHandler, CommitHandler, CheckHandler]:
    store[hd.state] = hd
