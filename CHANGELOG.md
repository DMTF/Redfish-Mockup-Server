
# Change Log

## [0.9.7] - 2017-030-10

- **T1.1** TIME.json  Added   support-getting Time for each API  

- - new      option/targ -d <dfltTime> to specify using the time value      in the TIME.json at each API directory if it exists

  - if      TIME.json does not exist at that API dir, use the time that was passed in      with -d

  - if      TIME.json does exist at the API dir, read TIME.json, and get the      "exeTime" property value out of it, and use that

  - if -t <time> is specified, use <time> and      ignore TIME.json files 

  - - if both       -t and -d are entered, give error and exit.

- **T1.2**  Added Response Header support for  GETs: 

  -1st: if      there is a DFLT_RESPONSE_HEADERS.json file at the top of the mockup      return those values  - DONE
  - 2nd-merge      Generated headers  - DONE
  - 3rd: if there is a file      GET_RESPONSE_HEADERS.json in the uri directory - merge, - DONE 

- **T1.3** Added  Support HEAD Method with same headers as GET,

- **T1.4** Added JSON Checking option (-J for     load json) – Done

- **T1.5** Added option -C to strip Copyright     property from output if -J json loading option is selected and -C is     selected  - DONE
- **LogFile**-  added -l Logfile option to save the     input request in a log file (this is the same thing this is printed out on     the console) - DONE

- **T1.6** Added https support 

- **T1.8** Added Authentication support   - BASIC Authentication support  Done





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
