DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS files;

CREATE TABLE user (
  id          INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  name        VARCHAR(64)                       NOT NULL,
  password    VARCHAR(128)                      NOT NULL,
  email       VARCHAR(64),
  create_time INTEGER                           NOT NULL DEFAULT (datatime('now', 'localtime'))
);

CREATE TABLE files (
  id           INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  filename     VARCHAR(128)                      NOT NULL,
  size         INTEGER,
  path         VARCHAR(512),
  url          VARCHAR(512),
  version_code INTEGER,
  version_name VARCHAR(16),
  create_time  INTEGER                           NOT NULL DEFAULT (datatime('now', 'localtime'))
)