
# Change Log

## [0.9.6] - 2017-02-28

- -d <systemdefaultTime> option added with the following options:
  - TIME.json file will be used as the primary source of for systems response time for the API under test if there is no -t 
  - If TIME.json does not exist or the key is missing in the file, -d arg will be used as system defaults response time 
- if both -t and -d are given, it will be an error 
- Additional Header support added with the ability to send custom headers for each API / Request Type  
- SSL support added  - but not implemented yet

## [0.9.3] - 2016-12-05

- -t <responseTime> option to specify a response delay for responses--to simulate a real system better
- fixed bug where GET /redfish/v1/$metadata was not being returned

## [0.9.2] - 2016-09-07
- added flush to server prints so that buffered stdout on cygwin would work
- added -T option to enable returning fake etags on certain APIs -instead of always doing it
- added -D <dir>  option  where <dir> is the abs or relative path to the mockup.  if no -D option, then CWD is assumed

## [0.9.1] - 2016-09-06
- Initial Public Release
- ​
