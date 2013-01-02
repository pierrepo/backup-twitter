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
backup_twitter_timeline.py: 

Downloads and stores full Twitter timeline. 
Can resume previous attempts.
"""

__author__ =  "Pierre Poulain"
__email__ = "pierre.poulain@cupnet.net"
__license__ = "GPL"
__version__ = 1.0


#==============================================================================
# modules
#==============================================================================
import argparse
import  sqlite3
from dateutil.parser import parse

import twitter # not standard Python module

#==============================================================================
# options
#==============================================================================
parser = argparse.ArgumentParser(description=__doc__)
 
parser.add_argument(
    'user', 
    type=str, 
    help="Twitter username. Required.")
parser.add_argument(
    '--count', 
    type=int, 
    default=20, 
    help="Number of tweets fetched at once. Should be between 1 and 100.")
parser.add_argument(
    '--version', 
    action='version', 
    version="%(prog)s "+str(__version__))
    
args = parser.parse_args()

USER = args.user
COUNT = args.count

#==============================================================================
# function
#==============================================================================
def save_tweet(cursor, tweet):
    """Save tweet to database
    """
    cursor.execute('INSERT OR IGNORE INTO Timeline VALUES (?,?)', 
    (tweet.id, str(tweet.AsDict())))
    if cursor.rowcount:
        date = parse(tweet.created_at)
        print "Saved tweet %d created %02i/%02i/%i %02i:%02i:%02i" % (
        tweet.id, 
        date.day, date.month, date.year, 
        date.hour, date.minute, date.second)


#==============================================================================
# start
#==============================================================================

# connect to database
DATABASE = "twitter_timeline_"+USER+".sqlite"

with sqlite3.connect(DATABASE) as db_con:
    db_cur = db_con.cursor()
    db_cur.execute('SELECT SQLITE_version()')
    version = db_cur.fetchone()
    print "SQLite version: %s" % version

    # check table from database
    db_cur.execute('CREATE TABLE IF NOT EXISTS \
    Timeline(id INTEGER NOT NULL UNIQUE, tweet TEXT NOT NULL)')
    db_cur.execute('SELECT id FROM Timeline')
    tweets_saved = db_cur.fetchall()
    print "Reading database"
    print "%d tweets saved so far" % len(tweets_saved)
    
    # connect to Twitter
    api = twitter.Api()

    # if no tweet saved so far
    # get id of the most recent tweet
    if len(tweets_saved) == 0:
        # get last tweet id
        tweet_tmp = api.GetUserTimeline(USER, count=1,  include_rts=1)
        tweet_id_max = tweet_tmp[0].id
        print "Last tweet id in timeline:", tweet_id_max 
        # max_id is inclusive 
        # add 1 to be sure, the most recent tweet is saved
        tweet_id_min = tweet_id_max + 1
    else:
        # get last and first id from already saved tweets
        tweet_id_max = max(tweets_saved)[0]
        tweet_id_min = min(tweets_saved)[0] 

    # the strategy to download a timeline is described in Twitter API
    # documentation: https://dev.twitter.com/docs/working-with-timelines

    # 1/2 download old tweets
    while True:
        try:
            # max_id is inclusive
            tweet_tmp = api.GetUserTimeline(
            USER, 
            include_rts=1, 
            max_id=tweet_id_min-1, 
            count=COUNT)
        except:
            print "Cannot download tweets. Something is broken somewhere."
            break
        if not tweet_tmp:
            print "No more old tweet to download."
            break
        for tw in tweet_tmp:
            save_tweet(db_cur, tw)
        # update min tweet_id
        tweet_id_min = tweet_tmp[-1].id



    # 2/2 download recent tweets
    while True:
        try:
            # since_id is exclusive
            tweet_tmp = api.GetUserTimeline(
            USER, 
            include_rts=1, 
            since_id=tweet_id_max, 
            count=COUNT)
        except:
            print "Cannot download tweets. Something is broken somewhere."
            break
        if not tweet_tmp:
            print "No more new tweet to download."
            break
        for tw in tweet_tmp:
            save_tweet(db_cur, tw)
        # update min tweet_id
        tweet_id_max = tweet_tmp[0].id

    # print final count
    db_cur.execute('SELECT id FROM Timeline')
    tweets_saved = db_cur.fetchall()
    print "Reading database"
    print "%d tweets saved so far" % len(tweets_saved)
    print "Bye bye"

