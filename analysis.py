#!/usr/bin/env python
# coding=utf-8
# shows a user's playlists (need to be authenticated via oauth)

import sys
import spotipy
import spotipy.util as util
from cachedrequest import CachedRequest
from pprint import pprint



def show_tracks(tracks):
    for i, track in enumerate(tracks):
        print "   %d %32.32s %s" % (i, track['artists'][0]['name'],
            track['name'])

if __name__ == '__main__':
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        print "Whoops, need your username!"
        print "usage: python user_playlists.py [username]"
        sys.exit()

    token = util.prompt_for_user_token(username, scope='user-library-read playlist-read-private')

    if token:
        sp = spotipy.Spotify(auth=token)
        r = CachedRequest(sp)

        playlists = r.get_playlists([], username)
        for playlist in playlists:
            if playlist['tracks']['total'] == 0:
                print "###############"
                print "Warning:", playlist['name'], "is empty"
                print "###############"

            tracks = r.get_playlist_tracks(playlist)

            playlist_album = tracks[0]['album']
            if all(track['album']['id'] == playlist_album['id'] for track in tracks):
                for separator in [u' \u2014 ', u' \u2013 ', " - ", None]:
                    if separator is None:
                        raise Exception('Error: no separator worked for %s', playlist['name'].split(u' \u2014 '))
                    if len(playlist['name'].split(separator,1)) != 2:
                        continue
                    else:
                        if playlist_album['name'] != playlist['name'].split(separator, 1)[1]:
                            print "###############"
                            print "Warning: playlist named", playlist['name'], "comes from album", playlist_album['name']
                            print "###############"
                        break
            else:
                print "###############"
                print "Warning:", playlist['name'], "contains tracks from multiple albums"
                print "###############"

            # print playlist['name']
            # print '  total tracks', playlist['tracks']['total']


        your_music = r.get_your_music_albums()
        print "++++++Your Music Albums"
        for album in your_music:
            print "Album", album['name'], "id:", album['id'], "external_ids:", album['external_ids']

        playlist_albums = r.get_playlists_albums(playlists)
        print "++++++Playlist Albums"
        for album in [album for album in playlist_albums if album is not None]:
            print "Album", album['name'], "id:", album['id'], "external_ids:", album['external_ids']

        for key, album in r.albums_dict.items():
            print "Album id:", key, "Name:", album['name']



    else:
        print "Can't get token for", username