from collections import defaultdict

from . import *

store = defaultdict()

for hd in [StartHandler, CheckHandler]:
    store[hd.state] = hd
