flask_blog/schema.sql

DROP TABLE IF EXISTS posts;

CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    namee TEXT NOT NULL,
    title TEXT NOT NULL,
    age int  not null
);
