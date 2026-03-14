



Abstract Repository (Track Repository)
-> returns tracks
Abstract Source (Source Bundle)
-> .track returns tracks, .album returns albums
Track Service
-> more track related methods/ exposing underlying methods
App Service
-> .track gives track service, .album gives album service etc
Implementation Hell


Repositories -
    They need to know how to grab specific information from their sources
    Take that data and put into models
        Important to know that we need to deal with nested models
    Objects should return as "fully" saturated

Services -
    Know the repository structure but is source agnostic
    Holds extra hydration logic (Only for albums and playlists)
    Manages caching results
    Supports "higher" level functionality 
        like (get albums in date range, etc)


GUIDING RULES - 
    If you ask for a singular/ multiple of just an object you get that object fully saturated
        ie if you request a track you should get all the track data AND album data AND artist data
        though you don't need to fully saturate the "tracks" within the album since we are requesting
        the track and not the album.
    Same idea with playlists, if you request a playlist it should return fully qualified objects for 
        the tracks within the playlist. It should also give you fully hydrated objects for albums and artists.

    Tracks are always fully hydrated
    Artists are always fully hydrated
    Albums are hydrated EXCEPT their track list unless "album" is gotten specifically
    Playlists should be fully hydrated to the rules above EXCEPT when getting a list of playlists
        ie get_user_playlists gives a list of playlist id's and playlist data BUT not tracks
        we may make a get_playlists function but guiding principle is that if we request a "blanks"
        list of objects we will get fully hydrated for that specific object but not their "lists"
            get_user_playlists -> getting "USERS" "PLAYLISTS" so no tracks/ albums but hydrated PLAYLIST
            get_artists_albums -> getting "ARTISTS" "ALBUMS" so no tracks but hydrated ALBUMS
        Notable exceptions are
            get_album_tracks
            get_playlist_tracks
        So overarching idea is if you request a list of objects that don't have lists of nested objects your gucci
        if you request stuff with nested lists of data... make sure you validate you have the data before


Need "Hydrating" methods for 
    Playlists
    Albums
Everything else should always be hydrated so I think we just pass a list of Playlist objects into the hydration
    method and then the code makes sure we have what is necessary and if we don't it knows how to make a bulk call
    of get_playlists or get_albums. With of course set checking and cache checking so we don't do double duty.
