``backup_twitter_timeline.py`` downloads a Twitter timeline and stores individual tweets in a sqlite database. 

For easy browsing, ``timeline_to_html.py`` converts the database in a single html file.

Requirements
------------

``backup_twitter_timeline.py`` and ``timeline_to_html.py`` require Python 2.7. Due to the use of the module ``argparse``, older Python versions are not supported.

``backup_twitter_timeline.py`` uses the very handy external library `python-twitter <https://github.com/bear/python-twitter>`_

Usages
------

::

    usage: backup_twitter_timeline.py [-h] [--count COUNT] [--version] user
    
    backup_twitter_timeline.py: Downloads and stores full Twitter timeline. Can
    resume previous attempts.
    
    positional arguments:
      user           Twitter username. Required.
    
    optional arguments:
      -h, --help     show this help message and exit
      --count COUNT  Number of tweets fetched at once. Should be between 1 and
                     100.
      --version      show program's version number and exit

Sqlite database is named upon Twitter username. For instance, ``twitter_timeline_pierrepo.sqlite`` for user ``pierrepo``.

For high speed internet connection, use the ``--count`` option set to 100. `Twitter API <https://dev.twitter.com/>`_ only allows the retrieval of maximum 100 tweets at once.


::

    usage: timeline_to_html.py [-h] [--picture] [--version] database

    timeline_to_html.py: Convert a Twitter timeline into a html file. Twitter
    timeline has been dowloaded by backup_twitter_timeline.py and stored in a
    sqlite database. Can download user profile picture.

    positional arguments:
      database    timeline database (sqlite) -- required

    optional arguments:
      -h, --help  show this help message and exit
      --picture   download profile picture of users
      --version   show program's version number and exit

Html file is named ``index.html``. Profile pictures and stylesheet are in the ``data`` directory.

License
-------

This program is free software: you can redistribute it and/or modify  
it under the terms of the GNU General Public License as published by   
the Free Software Foundation, either version 3 of the License, or      
(at your option) any later version.                                    
                                                                      
This program is distributed in the hope that it will be useful,        
but WITHOUT ANY WARRANTY; without even the implied warranty of         
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          
GNU General Public License for more details.                           
                                                                          
A copy of the GNU General Public License is available at
http://www.gnu.org/licenses/gpl-3.0.html.

