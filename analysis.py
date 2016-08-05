# !/bin/env python
# coding=utf-8
# shows a user's playlists (need to be authenticated via oauth)

import sys
import spotipy
import spotipy.util as util
import pickle, os

def show_tracks(tracks):
    for i, item in enumerate(tracks['items']):
        track = item['track']
        print "   %d %32.32s %s" % (i, track['artists'][0]['name'],
            track['name'])

class CachedRequest(object):
    def __init__(self):
        if os.path.isfile('./tracks.cache'):
            self.tracks_dict = pickle.load(open('tracks.cache', 'r'))
        else:
            self.tracks_dict = dict()

    def get_playlist_tracks(self, playlist):
        if self.tracks_dict.has_key(playlist['id']):
            return self.tracks_dict[playlist['id']]

        tracks = []
        results = sp.user_playlist(playlist['owner']['id'], playlist['id'], fields="tracks,next")
        i_tracks = results['tracks']
        tracks += i_tracks['items']
        while i_tracks['next']:
            i_tracks = sp.next(i_tracks)
            tracks += i_tracks['items']

        if playlist['tracks']['total'] != len(tracks):
            raise Exception('Read the wrong number of tracks: %d of %d'%
                            (len(tracks), playlist['tracks']['total']) )

        self.tracks_dict[playlist['id']] = tracks
        pickle.dump(self.tracks_dict, open('tracks.cache', 'wb'))

        return tracks

    def get_playlists(self, exclude = None, username = None):
        if os.path.isfile('./playlists.cache'):
            items = pickle.load(open('playlists.cache', 'r'))
            items = [playlist for playlist in items if
                     playlist['name'] not in exclude and (username is None or playlist['owner']['id'] == username)]
            return items

        n_total = None
        items = []
        playlists = sp.user_playlists(username)
        n_total = playlists['total']
        items += playlists['items']
        while playlists['next']:
            playlists = sp.next(playlists)
            items += playlists['items']

        if len(items) != n_total:
            raise Exception('Read the wrong number of playlists')

        pickle.dump(items, open('playlists.cache', 'wb'))
        items = [playlist for playlist in items if playlist['name'] not in exclude and ( username is None or playlist['owner']['id'] == username ) ]
        return items

if __name__ == '__main__':
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        print "Whoops, need your username!"
        print "usage: python user_playlists.py [username]"
        sys.exit()

    token = util.prompt_for_user_token(username)
    r = CachedRequest()

    if token:
        sp = spotipy.Spotify(auth=token)
        for playlist in r.get_playlists([], username):
            if playlist['tracks']['total'] == 0:
                print "###############"
                print "Warning:", playlist['name'], "is empty"
                print "###############"

            tracks = r.get_playlist_tracks(playlist)

            playlist_album = tracks[0]['track']['album']
            if all(track['track']['album']['id'] == playlist_album['id'] for track in tracks):
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
                print "Warning:", playlist['name'], "containts tracks from multiple albums"
                print "###############"

            #print playlist['name']
            #print '  total tracks', playlist['tracks']['total']
    else:
        print "Can't get token for", username