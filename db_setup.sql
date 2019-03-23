CREATE SCHEMA IF NOT EXISTS auth;

DROP TABLE IF EXISTS auth.user CASCADE;
CREATE TABLE auth.user (
  uid         char(20)      UNIQUE NOT NULL,
  email       varchar(70)   UNIQUE NOT NULL,
  password    varchar(100)
);

INSERT INTO auth.user (email, password, uid)
  VALUES ('santa@claus.example', 'very_secure', 'abcdefghijklmnopqrst');

DROP TABLE IF EXISTS auth.session CASCADE;
CREATE TABLE auth.session (
  uid       char(20)        UNIQUE NOT NULL REFERENCES auth.user(uid),
  token     char(20)        UNIQUE NOT NULL,
  created   timestamp       NOT NULL,
  timeout   interval        NOT NULL
);

DROP TABLE IF EXISTS auth.pending_signup CASCADE;
CREATE TABLE auth.pending_signup (
  email     char(70)        UNIQUE NOT NULL,
  code      char(6)         UNIQUE NOT NULL,
  created   timestamp       NOT NULL
)
