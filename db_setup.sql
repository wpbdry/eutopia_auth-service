CREATE SCHEMA auth;

CREATE TABLE auth.user (
  uid         char(20)      UNIQUE NOT NULL,
  full_name   varchar(70)   NOT NULL,
  call_name   varchar(20),
  email       varchar(70)   UNIQUE NOT NULL,
  password    varchar(50)   NOT NULL
);

INSERT INTO auth.user (full_name, call_name, email, password, uid)
  VALUES ('Santa Claus', 'Santa', 'santa@claus.example', 'very_secure', 'abcdefghijklmnopqrst');

CREATE TABLE auth.session (
  uid       char(20)        UNIQUE NOT NULL REFERENCES auth.user(uid),
  created   timestamp       NOT NULL,
  timeout   interval        NOT NULL
);
