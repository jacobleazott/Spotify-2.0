CREATE TABLE playlists (
    id TEXT UNIQUE PRIMARY KEY,
    name TEXT,
    description TEXT
) WITHOUT ROWID;

CREATE TABLE artists (
    id TEXT UNIQUE PRIMARY KEY,
    name TEXT
) WITHOUT ROWID;

CREATE TABLE albums (
    id TEXT UNIQUE PRIMARY KEY,
    name TEXT,
    release_date TEXT,
    total_tracks INTEGER
) WITHOUT ROWID;

CREATE TABLE tracks (
    id TEXT UNIQUE PRIMARY KEY,
    name TEXT,
    duration_ms INTEGER,
    is_local INTEGER,
    is_playable INTEGER,
    disc_number INTEGER,
    track_number INTEGER
) WITHOUT ROWID;

CREATE TABLE followed_artists (
    id TEXT PRIMARY KEY REFERENCES artists(id)
) WITHOUT ROWID;

CREATE TABLE playlists_tracks (
    id_playlist TEXT REFERENCES playlists(id),
    id_track TEXT REFERENCES tracks(id)
);

CREATE TABLE tracks_artists (
    id_track TEXT REFERENCES tracks(id),
    id_artist TEXT REFERENCES artists(id),
    UNIQUE(id_track, id_artist)
);

CREATE TABLE tracks_albums (
    id_track TEXT REFERENCES tracks(id),
    id_album TEXT REFERENCES albums(id),
    UNIQUE(id_track, id_album)
);

CREATE TABLE albums_artists (
    id_album TEXT REFERENCES albums(id),
    id_artist TEXT REFERENCES artists(id),
    UNIQUE(id_album, id_artist)
);

-- OPTIONAL: listening_sessions
CREATE TABLE listening_sessions (
    time TIMESTAMP NOT NULL,
    id_track TEXT -- REFERENCES tracks(id)"
);

-- OPTIONAL: track_play_counts
CREATE TABLE track_play_counts (
    id_track TEXT REFERENCES tracks(id) PRIMARY KEY,
    play_count INTEGER NOT NULL
) WITHOUT ROWID;
