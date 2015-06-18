# wig - WebApp Information Gatherer


wig is a web application information gathering tool, which can identify numerous Content Management Systems and other administrative applications.

The application fingerprinting is based on checksums and string matching of known files for different versions of CMSes. This results in a score being calculated for each detected CMS and its versions. Each detected CMS is displayed along with the most probable version(s) of it. The score calculation is based on weights and the amount of "hits" for a given checksum.

wig also tries to guess the operating system on the server based on the 'server' and 'x-powered-by' headers. A database containing known header values for different operating systems is included in wig, which allows wig to guess Microsoft Windows versions and Linux distribution and version. 


## Requirements


wig is built with **Python 3**, and is therefore not compatible with Python 2. 



## How it works


The default behavior of wig is to identify a CMS, and exit after version detection of the CMS. This is done to limit the amount of traffic sent to the target server.
This behavior can be overwritten by setting the '-a' flag, in which case wig will test all the known fingerprints.
As some configurations of applications do not use the default location for files and resources, it is possible to have wig fetch all the static resources it encounters during its scan. This is done with the '-c' option.
The '-m' option tests all fingerprints against all fetched URLs, which is helpful if the default location has been changed.



## Help Screen

```
usage: wig.py [-h] [-l INPUT_FILE] [-q] [-n STOP_AFTER] [-a] [-m] [-u] [-d]
              [-t THREADS] [--no_cache_load] [--no_cache_save] [-N]
              [--verbosity] [--proxy PROXY] [-w OUTPUT_FILE]
              [url]

WebApp Information Gatherer

positional arguments:
  url              The url to scan e.g. http://example.com

optional arguments:
  -h, --help       show this help message and exit
  -l INPUT_FILE    File with urls, one per line.
  -q               Set wig to not prompt for user input during run
  -n STOP_AFTER    Stop after this amount of CMSs have been detected. Default:
                   1
  -a               Do not stop after the first CMS is detected
  -m               Try harder to find a match without making more requests
  -u               User-agent to use in the requests
  -d               Disable the search for subdomains
  -t THREADS       Number of threads to use
  --no_cache_load  Do not load cached responses
  --no_cache_save  Do not save the cache for later use
  -N               Shortcut for --no_cache_load and --no_cache_save
  --verbosity, -v  Increase verbosity. Use multiple times for more info
  --proxy PROXY    Tunnel through a proxy (format: localhost:8080)
  -w OUTPUT_FILE   File to dump results into (JSON)
```


## Example of run:

```
$ ./wig.py example.com

wig - WebApp Information Gatherer

Redirected to http://www.example.com. Continue? [Y|n]:

TITLE
--- HTML TITLE ---

IP
255.255.255.256


SOFTWARE                         VERSION                           CATEGORY
Drupal                           7.28 | 7.29 | 7.30 | 7.31 | 7.32  CMS
ASP.NET                          4.0.30319.18067                   Platform
Microsoft-HTTPAPI                2.0                               Platform
Microsoft-IIS                    6.0 | 7.0 | 7.5 | 8.0             Platform
Microsoft Windows Server         2003 SP2 | 2008 | 2008 R2 | 2012  Operating System
       
SOFTWARE                         VULNERABILITIES                   LINK
Drupal 7.28                      7                                 http://cvedetails.com/version/169265
Drupal 7.29                      3                                 http://cvedetails.com/version/169917
Drupal 7.30                      3                                 http://cvedetails.com/version/169916
       
DOMAIN                           TITLE                             IP
http://m.example.com:80          mobile site                       255.255.255.257
http://download.example.com:443  other site                        255.255.255.257
       
TOOL                             SOFTWARE                          LINK
CMSmap                           Drupal                            https://github.com/Dionach/CMSmap
droopescan                       Drupal                            https://github.com/droope/droopescan
       
URL                              NOTE                              CATEGORY
/login/                          Test directory                    Interesting URL
/login/index_form.html           ASP.NET detailed error            Interesting URL
/robots.txt                      robots.txt index                  Interesting URL
/test/                           Test directory                    Interesting URL
_______________________________________________________________________________
Time: 15.7 sec            Urls: 351                         Fingerprints: 30560
```


## Call wig as a function
```
>>>> from wig import wig
>>>> w = wig(url='example.com')
>>>> w.run()
>>>> results = w.get_results()
```