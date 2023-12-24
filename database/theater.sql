/*
DROP TABLE members;
CREATE TABLE members (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
    email TEXT NOT NULL UNIQUE, 
    hash TEXT NOT NULL, 
    fname TEXT NOT NULL,
    lname TEXT NOT NULL,
    phone TEXT NOT NULL);

CREATE UNIQUE INDEX email ON members (email);

DROP TABLE staff;
CREATE TABLE staff (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
    username TEXT NOT NULL, 
    hash TEXT NOT NULL );

*/

DROP TABLE movies;
CREATE TABLE movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
    tmdb_id INTEGER UNIQUE NOT NULL,
    title TEXT NOT NULL,
    active BOOLEAN NOT NULL,
    deleted BOOLEAN NOT NULL);

INSERT INTO movies (tmdb_id, title, active, deleted) VALUES (787699, 'Wonka', True, False);
INSERT INTO movies (tmdb_id, title, active, deleted) VALUES (572802, 'Aquaman and the Lost Kingdom', True, False);
INSERT INTO movies (tmdb_id, title, active, deleted) VALUES (695721, 'The Hunger Games: The Ballad of Songbirds & Snakes', True, False);
INSERT INTO movies (tmdb_id, title, active, deleted) VALUES (901362, 'Trolls Band Together', True, False);
INSERT INTO movies (tmdb_id, title, active, deleted) VALUES (940551, 'Migration', True, False);
INSERT INTO movies (tmdb_id, title, active, deleted) VALUES (748783, 'The Garfield Movie', False, False);


DROP TABLE staff_changes;
CREATE TABLE staff_changes (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    staff_id INTEGER NOT NULL,
    change TEXT NOT NULL CHECK (change == 'added' OR change == 'activated' OR change == 'inactivated' OR change == 'deleted'),
    table_name TEXT NOT NULL,
    data_id INTEGER NOT NULL,
    date_time DATETIME NOT NULL,
    FOREIGN KEY(staff_id) REFERENCES staff(id)
);


/*
DROP TABLE auditoriums;
CREATE TABLE auditoriums (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
    a_rows INTEGER NOT NULL, 
    l_cols INTEGER NOT NULL, 
    m_cols INTEGER NOT NULL,
    r_cols INTEGER NOT NULL);

DROP TABLE screenings;
CREATE TABLE screenings (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
    auditorium_id INTEGER NOT NULL, 
    movie_id INTEGER NOT NULL, 
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    seats INTEGER NOT NULL,
    FOREIGN KEY(auditorium_id) REFERENCES auditoriums(id),
    FOREIGN KEY(movie_id) REFERENCES movies(id));

DROP TABLE tickets;
CREATE TABLE tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
    screening_id INTEGER NOT NULL, 
    seat TEXT NOT NULL, 
    price FLOAT NOT NULL,
    FOREIGN KEY(screening_id) REFERENCES screenings(id));
*/


-- TODO: ADD watch list table