from collections import defaultdict

from . import StartHandler

store = defaultdict()

for hd in [StartHandler]:
    store[hd.state] = hd
