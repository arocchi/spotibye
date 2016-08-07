#!/usr/bin/env python
import pickle, os

class CachedRequest(object):
    def __init__(self, sp):
        self.sp = sp
        if os.path.isfile('./tracks.cache'):
            self.tracks_dict = pickle.load(open('tracks.cache', 'r'))
        else:
            self.tracks_dict = dict()

        if os.path.isfile('./playlists_tracks.cache'):
            self.playlists_tracks_dict = pickle.load(open('playlists_tracks.cache', 'r'))
        else:
            self.playlists_tracks_dict = dict()

        if os.path.isfile('./albums.cache'):
            self.albums_dict = pickle.load(open('albums.cache', 'r'))
        else:
            self.albums_dict = dict()

    def get_playlist_tracks(self, playlist):
        if self.playlists_tracks_dict.has_key(playlist['id']):
            return self.playlists_tracks_dict[playlist['id']]

        tracks = []
        results = self.sp.user_playlist(playlist['owner']['id'], playlist['id'], fields="tracks,next")
        i_tracks = results['tracks']
        for item in i_tracks['items']:
            item['track']['added_at'] = item['added_at']
        tracks += [item['track'] for item in i_tracks['items']]
        while i_tracks['next']:
            i_tracks = self.sp.next(i_tracks)
            for item in i_tracks['items']:
                item['track']['added_at'] = item['added_at']
            tracks += [item['track'] for item in i_tracks['items']]

        if playlist['tracks']['total'] != len(tracks):
            raise Exception('Read the wrong number of tracks: %d of %d'%
                            (len(tracks), playlist['tracks']['total']) )

        self.playlists_tracks_dict[playlist['id']] = tracks
        pickle.dump(self.playlists_tracks_dict, open('playlists_tracks.cache', 'wb'))

        return tracks

    def get_album_tracks(self, album):
        if self.tracks_dict.has_key(album['id']):
            return self.tracks_dict[album['id']]

        tracks = []
        i_tracks = self.sp.album_tracks(album['id'])
        tracks += i_tracks['items']
        while i_tracks['next']:
            i_tracks = self.sp.next(i_tracks)
            tracks += i_tracks['items']

        if album['tracks']['total'] != len(tracks):
            raise Exception('Read the wrong number of tracks: %d of %d'%
                            (len(tracks), album['tracks']['total']) )

        self.tracks_dict[album['id']] = tracks
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
        playlists = self.sp.user_playlists(username)
        n_total = playlists['total']
        items += playlists['items']
        while playlists['next']:
            playlists = self.sp.next(playlists)
            items += playlists['items']

        if len(items) != n_total:
            raise Exception('Read the wrong number of playlists')

        pickle.dump(items, open('playlists.cache', 'wb'))
        items = [playlist for playlist in items if playlist['name'] not in exclude and ( username is None or playlist['owner']['id'] == username ) ]
        return items

    def get_your_music_albums(self):
        dump_pickle = False
        if os.path.isfile('./yourmusic.cache'):
            items = pickle.load(open('yourmusic.cache', 'r'))
            for item in items:
                if not self.albums_dict.has_key(item['id']):
                    dump_pickle = True
                    self.albums_dict[item['id']] = item
            if dump_pickle:
                pickle.dump(self.albums_dict, open('albums.cache', 'wb'))
            return items

        n_total = None
        items = []
        albums = self.sp.current_user_saved_albums()
        n_total = albums['total']
        for item in albums['items']:
            item['album']['added_at'] = item['added_at']
            self.get_album_tracks(item['album'])
        items += [item['album'] for item in albums['items']]
        while albums['next']:
            albums = self.sp.next(albums)
            for item in albums['items']:
                item['album']['added_at'] = item['added_at']
                self.get_album_tracks(item['album'])
            items += [item['album'] for item in albums['items']]

        if len(items) != n_total:
            raise Exception('Read the wrong number of albums')

        pickle.dump(items, open('yourmusic.cache', 'wb'))
        for item in items:
            print item
            if not self.albums_dict.has_key(item['id']):
                dump_pickle = True
                self.albums_dict[item['id']] = item
        if dump_pickle:
            pickle.dump(self.albums_dict, open('albums.cache', 'wb'))
        return items

    def get_playlists_albums(self, playlists):
        albums = len(playlists)*[None]
        albums_id = len(playlists)*[None]

        for i, playlist in enumerate(playlists):
            tracks = self.get_playlist_tracks(playlist)
            playlist_album = tracks[0]['album']
            if not all(track['album']['id'] == playlist_album['id'] for track in tracks):
                continue
                #raise Exception('Error: %s containts tracks from multiple albums'%playlist['name'])
            albums_id[i] = playlist_album['id']

            if self.albums_dict.has_key(playlist_album['id']):
                albums[i] = self.albums_dict[playlist_album['id']]

        dump_pickle = False
        req = []
        for i in xrange(len(albums)):
            if albums[i] is None and albums_id[i] is not None:
                dump_pickle = True

                id = albums_id[i]

                req.append({'i':i, 'id':id})

                if len(req) == 20 or i == len(albums)-1:
                    res = self.sp.albums([r['id'] for r in req])
                    for j, album in enumerate(res['albums']):
                        self.albums_dict[req[j]['id']] = album
                        albums[req[j]['i']] = album
                        playlist = playlists[req[j]['i']]
                        self.tracks_dict[album['id']] = self.get_album_tracks(album)
                    req = []


        if dump_pickle:
            pickle.dump(self.tracks_dict, open('tracks.cache', 'wb'))
            pickle.dump(self.albums_dict, open('albums.cache', 'wb'))

        return albums

    def get_playlist_album(self, playlist):
        return self.get_playlists_albums([playlist])[0]