This script is designed to be used either interactively or within the context of a cron script (e.g., referenced from job-description within `/etc/cron.monthly`, `/etc/cron.d`, etc.).

** Usage: **

~~~
Usage: ./watchmaker_sync.sh [GNU long option] [option] ...
  Options:
        -h  Print this message
        -P  HTTPS proxy information
        -p  HTTP proxy information
        -r  Repository root-folder
        -u  URL to download watchmaker stadalone binaries from
  GNU long options:
        --help              See "-h" short-option
        --http-proxy        See "-p" short-option
        --https-proxy       See "-P" short-option
        --repo-dir          See "-r" short-option
        --wam-url           See "-u" short-option
~~~

** Legacy Cron: **
When invoked from a con job, it is expected that such invocation might look like

~~~
0 0 * * 0 /usr/local/sbin/watchmaker_sync.sh \
   -p <PROXY_SERVER_URL> \
   -r <FULLY_QUALIFIED_FILESYSTEM_PATH>
~~~ 

The above would cause the sync-task to run every Sunday at 00:00 system-time

** Cron file in `/etc/cron.d/`: **

~~~ 
SHELL=/bin/bash
PATH=/usr/local/sbin:/sbin:/bin:/usr/sbin:/usr/bin
HTTP_PROXY=<PROXY_SERVER_URL>
REPO_DIR=<FULLY_QUALIFIED_FILESYSTEM_PATH>

0 0 * * 0 root watchmaker_sync.sh
~~~ 


** File in `/etc/cron.monthly`: **

~~~ 
/usr/local/sbin/watchmaker_sync.sh \
   -p <PROXY_SERVER_URL> \
   -r <FULLY_QUALIFIED_FILESYSTEM_PATH>
~~~ 
