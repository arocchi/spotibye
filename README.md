# spotibye
Spotibye is a tool that allows to migrate from Spotify to Google Play Music.
It is built for music lovers who have a big collection of Music, in particolar, it is useful for those who met the 10k Song limit in Spotify's "Your Music".
The idea of conversion in Spotibye focuses around the *album* rather than the playlist.
While there are already out there a number of tools to export Spotify playlists to Google Play Music, there is no easy way to transfer the whole Music Library ("Your Music").
Furthermore, for old time users, it is typical to have a collection where albums are either saved in "Your Music" as `Albums`, or as playlists, where each playlist represents an album.
Spotibye will therefore detect whose playlist are albums (1 playlist for 1 album scenarios), and also download a list of saved Albums in "Your Music", and save them in Google Play Music.
It will give useful reports on the migration process, so that grey areas and failed migrations (i.e., albums which are present in one catalog and missing in the other) will be notified to the user.
Also, in the migration process it will try to avoid duplicates, thus keeping the Google Play Music library tidy: this allows to slim down the number of tracks saved in Google Library, which is also limited to 30k at the moment, and use whenever possible the uploaded albums (for which there is a limit of 50k tracks). Theoretically, this allows to have a Music Library in Google Play Music of up to 80k tracks.
The rationale behind all of this is:
_a playlist is not an album_

## Tools
- analysis: get a cleaned-up list of all albums in collection

### Data structures:
The data structures used are the same documented by Spotify, with the difference that `albums` and `playlist tracks` objects are "flattened", that is, the `date_added` field is moved inside the data structure:
```
item (paged playlist track)
{
    date_added: '...',
    track: {...}
}
```
becomes
```
track
{
    date_added: '...',
    ...
}
```
and the same for user albums
```
item (paged user album list)
{
    date_added: '...',
    album: {...}
}
```
becomes
```
album
{
    date_added: '...',
    ...
}
```

This flattening allows to use the same data structure for albums coming from playlists and albums coming from the user library, and from tracks coming from playlists and tracks coming from albums.

## Planned tools
- spotiwhy: convert from "My Music" to playlist and vice-versa, when possible (all in Spotify)
- spotibye: list all spotify albums (either from "Your Music" or from playlists) and perform a (semi-)automatic album search and import in Google Play Music