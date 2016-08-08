#!/usr/bin/env python
# coding=utf-8
# Attempts a conversion from Spotify to Google Play Music library (need to specify credentials, will use oath in the future)

import sys
import spotipy
import spotipy.util as util
from gmusicapi import Mobileclient
from cachedrequest import CachedRequest
from cachedassociation import CachedAssociation

if __name__ == '__main__':

    if len(sys.argv) == 3:
        username = sys.argv[1]
        password = sys.argv[2]
    else:
        print "Whoops, need your username and password"
        print "usage: python spotibye.py [username] [password]"
        sys.exit()

    token = util.prompt_for_user_token(username, scope='user-library-read playlist-read-private')

    if token:
        sp = spotipy.Spotify(auth=token)
    else:
        print "Could not login to Spotify"

    gpm = Mobileclient()
    logged_in = gpm.login(username, password, Mobileclient.FROM_MAC_ADDRESS)

    if not logged_in:
        print "Could not login to Google Play Music"

    if token and logged_in:

        r = CachedRequest(sp)
        a = CachedAssociation(gpm)

        playlists = r.get_playlists([], username)
        r.get_your_music_albums()
        r.get_playlists_albums(playlists)

        for album in r.albums_dict.values():
            best_match, candidate_matches = a.look_for_match(album)
