-- DROP TABLE users;
-- CREATE TABLE users (
--     id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
--     username TEXT NOT NULL, 
--     hash TEXT NOT NULL, 
--     fname TEXT NOT NULL,
--     lname TEXT NOT NULL,
--     phone TEXT NOT NULL);

-- CREATE UNIQUE INDEX username ON users (username);

-- DROP TABLE staff;
CREATE TABLE staff (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
    username TEXT NOT NULL, 
    hash TEXT NOT NULL );
