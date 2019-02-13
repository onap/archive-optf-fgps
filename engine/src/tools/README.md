### Valet Tools for development, test, and production support

|File| Description |
|---|---|
|crim.py|Commandline Rest Interface for Music<br>*read, add, delete from the music database*|
|lock.py|Manual (Un)Locking Of Valet Regions<br>*from the regions (locking) table*|
|ppdb.py|pretty print database<br>*try to make the database data readable*|
|lib/common|collection of functions<br>- **set_argument** - *Get arg from file, cmdline, a pipe or prompt user*<br>- **list2string** - *join list and return as a string*<br>- **chop** - *like perl*|
|lib/hosts.json|*contains all the currently known (by me) hosts for music and valet*|
|lib/logger.py|*like the official logger but allows logger to point to file and or console*|
|lib/tables.py|*Tables object, that handles each valet table as small subclass (could replace db_handler.py)*|
|lib/song.py|*Song is music for scripts, a subclass of music.py, with script helpers*|

#### Examples
`$ crim.py -?`

Show help message and exit (a lot more options than I am showing here...)

`$ crim.py -names -read requests -read results`

Show the contents of the requests and results tables in the default keyspace

`$ crim.py -n -r q -r u`

Same as above, but with using [watch](https://linux.die.net/man/1/watch "watch(1) - Linux man page") to execute the script repeatadly displaying the output
Also this is an example of using shortcuts for arguments

`$ watch crim.py -n -r q -r u`

Show the contents of the regions tables (locking) in the all the known keyspaces

`$ crim.py -K all -r regions`

Delete the cw keyspace - this is used for testing to "clean" the database

`$ crim.py -sD cw`

Show the database stuff for the pn2 keyspace

`$ crim.py -show -K pn`

Show the config stuff for the pn2 keyspace

`$ crim.py -ShowConfig -K pn`

Show the database tables and definitions (hardcoded, not a query from the database)

`$ crim.py -viewSchema`

Show the requests record with id create-0000-0003 

`$ crim.py -i create-0000-0003 -r q`

Show the resources record in the pk2 keyspace with id "reg6:alan_stack_N003"

`$ crim.py -r s -K pk2 -i "reg6:alan_stack_N003"`

##### Testing Example

Here we are going to copy a record from one environment to another

Get a record from the request table, into a file; *Note:* Not the default config file...

`$ crim.py -config ../test/solver.json -r q -K ist -id "create-abc-10099" > z`

Put that record from the file into the request table of another keyspace 

`$ crim.py -c ../test/solver.json -t q -K pk2 -a i -f z`

