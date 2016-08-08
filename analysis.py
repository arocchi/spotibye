#!/usr/bin/env python
# coding=utf-8
# Perform ana analysis of Spotify library (need to be authenticated via oauth)

import sys
import spotipy
import spotipy.util as util
from cachedrequest import CachedRequest

def print_playlists_warnings(r, playlists):
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
                if len(playlist['name'].split(separator, 1)) != 2:
                    continue
                else:
                    if playlist_album['name'] != playlist['name'].split(separator, 1)[1]:
                        print "Warning: playlist named", playlist['name'], "comes from album", playlist_album['name']
                    break
        else:
            print "###############"
            print "Warning:", playlist['name'], "with id", playlist['id'], "contains tracks from multiple albums, will not be considered as album"
            playlist_albums = dict()
            for track in tracks:
                if playlist_albums.has_key(track['album']['id']):
                    playlist_albums[track['album']['id']] += [track]
                else:
                    playlist_albums[track['album']['id']] = [track]
            for album_id, a_tracks in playlist_albums.items():
                for a_track in a_tracks:
                    print "Track", a_track['name'], "from album", a_track['album']['name']
            print "###############"

def print_albums_warnings(r, albums):
    for album in albums:
        if len(album['name']) == 0:
            print "************"
            print "Warning: album with id", album['id'], "has no name,", album['tracks']['total'], "tracks"
            print "Track Listing:"
            tracks = r.get_album_tracks(album)
            print_tracks(tracks)
            print "External urls:"
            print album['external_urls']['spotify']
            print "************"

        if len(album['external_ids'].items()) == 0:
            print "************"
            print "Warning: album", album['name'] ,"with id", album['id'], "has no external ids"
            print "************"

        if album['tracks']['total'] == 0:
            print "************"
            print "Warning: album with id", album['id'], ",", album['name'], "has zero tracks"
            print "************"

def print_tracks(tracks):
    for i, track in enumerate(tracks):
        print "   %d %32.32s %s" % (i, track['artists'][0]['name'],
            track['name'])

def count_tracks(albums):
    return sum([album['tracks']['total'] for album in albums])

if __name__ == '__main__':
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        print "Whoops, need your username!"
        print "usage: python analysis.py [username]"
        sys.exit()

    token = util.prompt_for_user_token(username, scope='user-library-read playlist-read-private')

    if token:
        sp = spotipy.Spotify(auth=token)
        r = CachedRequest(sp)

        playlists = r.get_playlists([], username)
        print_playlists_warnings(r, playlists)

            # print playlist['name']
            # print '  total tracks', playlist['tracks']['total']


        your_music = r.get_your_music_albums()
        """
        print "++++++Your Music Albums"
        for album in your_music:
            print "Album", album['name'], "id:", album['id'], "external_ids:", album['external_ids']
        """
        print count_tracks(your_music), "tracks in", len(your_music), "albums"

        playlist_2_albums = r.get_playlists_albums(playlists)
        playlist_albums = [album for album in playlist_2_albums if album is not None]
        """
        print "++++++Playlist Albums"
        for album in playlist_albums:
            print "Album", album['name'], "id:", album['id'], "external_ids:", album['external_ids']
        """
        print count_tracks(playlist_albums), "tracks in", len(playlist_albums), "playlist albums"

        """
        for key, album in r.albums_dict.items():
            print "Album id:", key, "Name:", album['name']
        """

        print_albums_warnings(r, r.albums_dict.values())

    else:
        print "Can't get token for", username