#! /usr/bin/env python
# -*- coding: utf-8 -*-

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of the GNU General Public License is available at
#    http://www.gnu.org/licenses/gpl-3.0.html

"""
timeline_to_html.py: 

Convert a Twitter timeline into a html file.
Twitter timeline has been dowloaded by backup_twitter_timeline.py
and stored in a sqlite database.
Can download user profile picture.
"""

__author__ =  "Pierre Poulain"
__email__ = "pierre.poulain@cupnet.net"
__license__ = "GPL"
__version__ = 1.0

#==============================================================================
# modules
#==============================================================================
import time
import sqlite3
import re
import os
import sys
import shutil
import urllib 
import argparse
from dateutil.parser import parse

#==============================================================================
# options
#==============================================================================
parser = argparse.ArgumentParser(description=__doc__)

parser.add_argument(
    'database', 
    type=str,
    help='timeline database (sqlite) -- required')
parser.add_argument(
    '--picture', 
    action='store_true', 
    default=False, 
    help='download profile picture of users')
parser.add_argument(
    '--version', 
    action='version', 
    version="%(prog)s "+str(__version__))

args = parser.parse_args()

DATABASE = args.database
PICTURE = args.picture


#==============================================================================
# data
#==============================================================================
project_dir = os.path.abspath(__file__).rpartition(os.sep)[0]
user_img_default = project_dir + os.sep + 'Monster_Iconshock.png'
style_name = project_dir + os.sep + 'style.css'
out_name = 'index.html'
data_dir = 'twt-data'
#==============================================================================
# functions
#==============================================================================
def extract_tweet_date(raw_date):
    """extract day dans time from tweet
    """
    date = parse(raw_date)
    day  = "%02i/%02i/%02i" % (date.day, date.month, date.year)
    time = "%02i:%02i" % (date.hour, date.minute)
    return day, time
    
def extract_tweet_content(tweet):
    """extract content from tweet
    """
    return tweet['text']

def extract_tweet_user(tweet, user_dir):
    """extract user name and user profile picture from tweet
    """
    
    # find out if a tweet is an original tweet or a retweet.
    if tweet.has_key('retweeted_status'):
        url = tweet['retweeted_status']['user']['profile_image_url']
        name = tweet['retweeted_status']['user']['screen_name']
    else:
        url = tweet['user']['profile_image_url']
        name = tweet['user']['screen_name']

    # rename profile pictures
    img = user_dir + os.sep + name + '.' + url.split('.')[-1]
    
    return name, url, img
    
#==============================================================================
# start
#==============================================================================

regex_url = re.compile("http\S+")
regex_hashtag = re.compile("#[\w-]+")
regex_user = re.compile("@[\w]+")

# create profile picture directory
if os.path.isdir(data_dir):
    print "%s directory already exists." % data_dir
else:
    try:
        os.makedirs(data_dir)
        print "Created %s directory." % data_dir
    except:
        sys.exit("Cannot create %s directory." % data_dir)

# copy default files
shutil.copy(user_img_default, data_dir)
shutil.copy(style_name, data_dir)

# connect to database
with sqlite3.connect(DATABASE) as db_con:
    db_cur = db_con.cursor()
    db_cur.execute('SELECT SQLITE_VERSION()')
    version = db_cur.fetchone()
    print "SQLite version: %s" % version

    # check table from database
    try:
        db_cur.execute('SELECT id, tweet FROM Timeline ORDER BY id')
    except:
        print "Cannnot read database in %s" % DATABASE
        print "Probably a wrong structure."
        sys.exit(1)
    tweets_saved = db_cur.fetchall()
    if len(tweets_saved) == 0:
        sys.exit("No tweet saved in database. What's the point?")
    print "Reading database."
    print "%d tweets found." % len(tweets_saved)

    # download user picture
    if PICTURE:
        for tweet_id, tweet in tweets_saved:
            tweet_dic = eval(tweet.encode('utf-8', 'strict'))
            user_name, user_url, user_img = extract_tweet_user(
                                            tweet_dic, 
                                            data_dir)
            # do not download profile picture twice
            if not os.path.isfile(user_img):
                try:
                    urllib.urlretrieve(user_url, user_img)
                    print "Downloaded %s profile picture." % user_name
                except:
                    print "Cannot dowload %s profile picture." % user_name
    
    # create HTML file
    out_file = open(out_name, 'w')

    # print HTML preambule
    out_file.write(r"""
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
   "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" /> 
<title>~ Twitter timeline ~</title>
<link type="text/css" rel="stylesheet" href="%s/style.css" />
</head>
<body>
""" % data_dir )

    current_day = ""

    for tweet_id, tweet in tweets_saved:
        html = ""
        # convert tweet to real Python dictionary
        tweet_dic = eval(tweet.encode('utf-8', 'strict'))
        # extract data from tweet 
        tweet_day, tweet_time = extract_tweet_date(tweet_dic['created_at'])
        content = extract_tweet_content(tweet_dic)
        user_name, user_url, user_img = extract_tweet_user(
                                        tweet_dic, 
                                        data_dir)
        # check if user profile picture is available
        # picture could not be available for 2 raisons:
        # 1 - picture cannot be downloaded
        # 2 - picture was not downloaded because the --picture option
        #     was not set
        if not os.path.isfile(user_img): 
            user_img = user_img_default
        # add hyperlinks for urls
        urls = regex_url.findall(content)
        for url in urls:
            if len(url) < 15:
                # deal with incomplete urls
                continue
            content = content.replace(url, '<a href="%s">%s</a>' %(url, url))
        # add hyperlinks for hashtags
        tags = regex_hashtag.findall(content)
        for tag in tags:
            content = content.replace(
            tag, 
            '<a href="https://twitter.com/search?q=%23'+tag[1:]+'&src=hash">'+tag+'</a>')
        # add hyperlinks for users
        users = regex_user.findall(content)
        for user in users:
            content = content.replace(
            user, 
            '<a href="https://twitter.com/'+user[1:]+'">'+user+'</a>')
        # add header 
        if tweet_day != current_day:
            current_day = tweet_day
            html += '<div class="date">%s</div> \n \n' % current_day
        html += r"""
<div class="tweet">
<div class="picture">
<img width=48 src="%s" />
</div>
<pre>
<a href="https://twitter.com/pfff/status/%i">%s</a>
</pre>
<pre>
%s
</pre>
</div>
""" % (user_img, tweet_dic['id'], tweet_time, content)
        out_file.write(html.encode('utf-8'))

    out_file.write("""
</body>
</html>
""")


out_file.close()
print "Wrote Twitter timeline in", out_name
print "Pictures and stylesheet are in", data_dir
