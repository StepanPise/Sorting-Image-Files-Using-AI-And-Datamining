-- PHOTOS
CREATE TABLE IF NOT EXISTS photos (
    id SERIAL PRIMARY KEY,
    path TEXT NOT NULL,
    filename TEXT NOT NULL,
    hash TEXT UNIQUE NOT NULL,
    already_analyzed INTEGER DEFAULT 0,
    location_data_country TEXT,
    location_data_city TEXT,
    time_data TEXT,
    width INTEGER,
    height INTEGER
);

-- TAGS
CREATE TABLE IF NOT EXISTS tags (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

-- Photo <-> Tags (M:N)
CREATE TABLE IF NOT EXISTS photo_tags (
    photo_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    FOREIGN KEY (photo_id) REFERENCES photos(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id)  REFERENCES tags(id)   ON DELETE CASCADE
);

-- PEOPLE
CREATE TABLE IF NOT EXISTS people (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    avg_embedding BYTEA
);

-- FACES
CREATE TABLE IF NOT EXISTS faces (
    id SERIAL PRIMARY KEY,
    photo_id INTEGER NOT NULL,
    embedding BYTEA NOT NULL,
    face_coords TEXT,
    person_id INTEGER,
    FOREIGN KEY (photo_id) REFERENCES photos(id) ON DELETE CASCADE,
    FOREIGN KEY (person_id) REFERENCES people(id) ON DELETE SET NULL
);

-- SYSTEM PREFS
CREATE TABLE IF NOT EXISTS system_preferences (
    key TEXT PRIMARY KEY,
    value TEXT
);


