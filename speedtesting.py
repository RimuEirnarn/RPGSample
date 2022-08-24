"""Speed testing on projects.

You may want to use snakeviz or something to do stuff with the reports."""

import libchara
import libgame
import libinventory
import libitems
import liblocalisation
import libmagic
import libsavestate
import libshared

from cProfile import Profile
from pstats import SortKey, Stats


def main():
    libchara._main()
    libgame._main()
    libinventory._main()
    libitems._main()
    liblocalisation._main()
    libmagic._main()
    libsavestate._main()
    libshared._main()


with Profile() as pr:
    main()

ps = Stats(pr)
ps.sort_stats(SortKey.TIME)
ps.dump_stats(libshared.Protocol("project://profiler.data")._to_string())
