# femmanMemberSystem

(depricated) member system for Ett fritt Kulturhus i Uppsala


------------------------
# auth example
    [gmail]
    user = website.khusuppsalaEmailAdr
    pw = strongPW

    [moosend]
    apiKey = 
    thisYear = 
    nextYear = 


# exec
    ./src/main.py all #or
    ./src/main.py unread


# todo
* write proper documentation
* build framework for dealing with banned members
* build accessible framework (=web portal?) to interact with database.
  see 'server'-branch.
* ~~if possible create nextYear's moosend list automatically~~
* ~~when reading _all_ emails inbox ignore all older than current year~~
* ~~clean up code~~
