#!/usr/bin/env python3

from collections import Counter
import re
import argparse
import sys

# INFO  - 2018-11-12 08:42:22.162; org.apache.solr.core.SolrCore; [core1]
LINE_RE = re.compile("INFO.*?\[(?P<core>\w+)\]\s+webapp=/\w+\s+path=(?P<path>/\w+)\s+params={(?P<search>.*)}\s+(hits=(?P<hits>\w+)\s+)?status=\w+\s+QTime=(?P<qtime>\w+).*")
"""
lines we want:
INFO  2018-11-12 08:42:22.162; org.apache.solr.core.SolrCore; [arstechnicacogtree] webapp=/solr path=/mlt params={mlt.count=16&fl=link,title,author,pub_date,thumb_url_medium,metadata,section&start=0&q=link_aliases:http\://arstechnica.com/apple/news/2009/02/the\-case\-of\-the\-app\-store\-ripoff.ars&wt=json&fq=pub_date:[NOW/DAY-14DAYS+TO+NOW/DAY%2B1DAY]&rows=16} status=0 QTime=2
INFO: [places] webapp=/solr path=/select/ params={pf=*&sort=geodist()+asc&fl=*,_dist_:geodist()&q=*&sfield=location&pt=-1.260326940083812,51.759690475011105&wt=json&spellcheck.collate=true&defType=edismax} hits=9830 status=0 QTime=11
"""

class CoreCounter(object):
    def __init__(self, corename):
        self.corename = corename
        self.endpoints = Counter()
        self.urls = Counter()
        self.linesread = 0
        self.qtimes = Counter()
        self.qtimes_sum = Counter()

    def __repr__(self):
        return "<Core '%s' with %i endpoints %i search urls>" % (self.corename, len(self.endpoints), len(self.urls))

    def timestats(self):
        sqtimes = sorted(self.qtimes.values())
        numitems = len(sqtimes)
        percent_50 = sqtimes[int(numitems / 2)]
        percent_75 = sqtimes[int(numitems * .75)]
        percent_90 = sqtimes[int(numitems * .90)]
        percent_99 = sqtimes[int(numitems * .99)]
        return (("Median", percent_50),
                ("75%", percent_75),
                ("90%", percent_90),
                ("99%", percent_99))

    def _pprint_topn(self, n, counter, title, unit):
        """Print the top N entries of a counter with its title.
        """
        s = "{0}\n{1}\n".format(title, "=" * 40)
        top = counter.most_common(n)
        for index, item in enumerate(top):
            label, cnt = item
            s += 'QUERY %i: "%s" %i %s\n\n' % (index + 1, label, cnt, unit)
        return s

    def pprint_stats(self):
        """Print statistics for a core
        """
        print(self._pprint_topn(args.max, self.endpoints, "Top Endpoints for {0}".format(self.corename), "times"))
        print(self._pprint_topn(args.max, self.urls, "Top Search URLs for {0}".format(self.corename), "times"))
        print(self._pprint_topn(args.max, self.qtimes, "Slowest Searches for {0}".format(self.corename), "ms"))
        # qtimes
        print("Search Time for {0}\n{1}\n".format(self.corename, '=' * 40))
        stats = self.timestats()
        for st in stats:
            print("%-10s %sms" % (st[0], st[1]))
        return ""


class StatCounter(object):
    def __init__(self, debug=False):
        self.corecounters = {}
        self.queries = 0
        self.lines = 0
        self.debug = debug

    def process(self, iterinput):
        for line in iterinput:
            self.lines += 1

            matches = LINE_RE.match(line)
            if not matches:
                if self.debug:
                    print("not matched: >>>{0}<<<".format(line))
                continue

            core = matches.group("core")
            path = matches.group("path")
            search = matches.group("search")
            qtime = matches.group("qtime")
            hits = matches.group("hits")


            corecounter = self.corecounters.get(core, CoreCounter(core))
            corecounter.endpoints[path] += 1
            corecounter.urls[search] += 1
            corecounter.linesread += 1
            corecounter.qtimes[search] = int(qtime)
            corecounter.qtimes_sum[search] = corecounter.qtimes_sum[search] + int(qtime)

            self.corecounters[core] = corecounter
            self.queries += 1

    def allcounterstats(self):
        for cc in self.corecounters.values():
            print(cc.pprint_stats())
            print("*" * 100)
            print()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--max',
        type=int,
        default=10,
        nargs='?',
        help='number of top queries')

    parser.add_argument(
        '--debug',
        help='Output debug information',
        action='store_true',
    )

    args, remaining_args = parser.parse_known_args()

    sc = StatCounter(debug=args.debug)

    if len(remaining_args) <= 0:
        sc.process(sys.stdin)
    else:
        for filename in remaining_args:
            print("parsing %s" % filename)
            with open(filename, "r") as fd:
                sc.process(fd)

    sc.allcounterstats()

    print("parsed %s lines with %s queries" % (sc.lines, sc.queries))

