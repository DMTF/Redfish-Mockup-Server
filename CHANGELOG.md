# Change Log

## [1.0.1] - 2018-04-13
- Made fixes for how POST and DELETE are handled with the Event Destination Collection
- Made fixes to the Submit Test Event action

## [1.0.0] - 2018-02-02
- Added support for HTTPS
- Added support for using "short" mockups (ones without the /redfish/v1 resource)
- Added support for submitting test events
- Added support for PATCH and PUT

## [0.9.7] - 2017-03-10
- Added support to delay time from json for GET and HEAD API  
    - "-T" option to include delay in time. If option not specified, there is no delay in response. Checks for time.json.
    - "-t <time_in_seconds>" to specify default time if time.json is not present.
- Added Response Header support for GETs: 
    - Checks for headers.json and includes required headers from it.
    - Certain headers like ("Connection", "Keep-Alive", "Content-Length") are not included in GET request.
- Added Support for HEAD Method
    - Checks for headers.json and includes required headers from it.
- Changed TestETag option to "-E" from "-T" 

## [0.9.3] - 2016-12-05
- -t <responseTime> option to specify a response delay for responses--to simulate a real system better
- fixed bug where GET /redfish/v1/$metadata was not being returned

## [0.9.2] - 2016-09-07
- added flush to server prints so that buffered stdout on cygwin would work
- added -T option to enable returning fake etags on certain APIs -instead of always doing it
- added -D <dir>  option  where <dir> is the abs or relative path to the mockup.  if no -D option, then CWD is assumed

## [0.9.1] - 2016-09-06
- Initial Public Release
