#!/usr/bin/env python
import pickle, os

class CachedAssociation(object):
    def __init__(self, gpm):
        self.gpm = gpm
        if os.path.isfile('./associations.cache'):
            self.associations_dict = pickle.load(open('associations.cache', 'r'))
        else:
            self.associations_dict = dict()

    def look_for_match(self, album):
        print
        print "-----------------"
        print "Looking for match", album['id'], ":", ', '.join([artist['name'] for artist in album['artists']]), "-", album['name']
        if self.associations_dict.has_key(album['id']):
            return self.associations_dict[album['id']]

        res = self.gpm.search(album['artists'][0]['name'] + " " + album['name'])
        if len(res['album_hits']) == 0:
            # generate a list of heuristics first. Cases take only name or surname (Billie & Norah), take second artist name (Back & Gould)
            artist_name = album['artists'][0]['name'].split(' ')[0]
            album_name = album['name']
            print "??? No match found, trying heuristic", artist_name, album_name
            res = self.gpm.search(artist_name + " " + album_name)
            if len(res['album_hits']) == 0: # a better heuristic would have worked in the first place: strip () and [] !!!
                album_name = album['name'].split('[')[0]
                album_name = album_name.split('(')[0]  # should put a smart filter here instead...
                print "!!! No match found, trying stricter heuristic", artist_name, album_name
                res = self.gpm.search(artist_name + " " + album_name)

        if len(res['album_hits']) == 0:
            print "xxx No match found!"
        else:
            print len(res['album_hits']), "matches found"

        album_infos = [] * len(res['album_hits'])
        for i_album_hit in res['album_hits']:
            album_hit = i_album_hit['album']
            album_infos.append(self.gpm.get_album_info(album_hit['albumId']))

        candidate_matches = []
        best_match = None

        if len(res['album_hits']) > 0:
            best_match = album_infos[0] # sometimes it is not the first match. Run string similarity
            print "+++ Best match:", best_match['albumArtist'], "-", best_match['name']
            if album['tracks']['total'] != len(best_match['tracks']):
                print "?+? Warning: original had", album['tracks']['total'], "tracks, match has", len(best_match['tracks']), "tracks"
        if len(res['album_hits']) > 1:
            candidate_matches = [i_album_info for i, i_album_info in enumerate(album_infos) if i > 0]
            for candidate_match in candidate_matches:
                print "+ candidate:", candidate_match['albumArtist'], "-", candidate_match['name']

        if len(res['album_hits']) > 0:
            self.associations_dict[album['id']] = (best_match, candidate_matches)
            pickle.dump(self.associations_dict, open('associations.cache', 'wb'))

        return (best_match, candidate_matches)
