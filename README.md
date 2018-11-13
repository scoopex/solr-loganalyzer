solr-loganalyzer
=================

A query analyzer that parses Solr's log file to get some basic query statistics 

Note that you need to enable logging at the INFO level for this to
work and you need to have cores enabled. You also need python3 installed.

Usage:
```
# reading from stdin
cat file1 file2 | ./loganalyzer.py --max 20
tail -1000 | ./loganalyzer.py --max

# reading a file
./loganalyzer.py so solr.log solr.log.1 solr.log.2
```

The analyzer outputs statistics grouped by Solr core. Here is an example:

```
Top Endpoints for core1
========================================
1) "/mlt" 3 times
   
Top Searh URLs for core1
========================================
1) "mlt.count=16&&q=qrows=16" 1 times
2) "mlt.count=16&start=0&q=&rows=16" 1 times
   
Slowest Searches for core1
========================================
1) "mlt.count=16&&q=qrows=16" 30 times
2) "mlt.count=16&start=0&q=&rows=16" 11 times
   
Search Time for core1
========================================
Median     2
75%       11
90%       11
99%       30

****************************************************************************************************

Top Endpoints for core2
========================================
1) "/mlt" 3 times
   
Top Searh URLs for core2
========================================
1) "mlt.count=5&&q=qrows=16" 1 times
2) "mlt.count=5&start=0&q=&rows=16" 1 times
   
Slowest Searches for core2
========================================
1) "mlt.count=5&&q=qrows=16" 30 ms
2) "mlt.count=5&start=0&q=&rows=16" 11 ms
   
Search Time for core2
========================================
Median     2
75%       11
90%       11
99%       30
```

This tool is inspired by [redis-faina](https://github.com/Instagram/redis-faina)
