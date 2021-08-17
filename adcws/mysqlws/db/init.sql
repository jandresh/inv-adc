-- CREATE DATABASE knights;
-- use knights;

-- CREATE TABLE favorite_colors (
--   name VARCHAR(20),
--   color VARCHAR(10)
-- );

-- INSERT INTO favorite_colors
--   (name, color)
-- VALUES
--   ('Lancelot', 'blue'),
--   ('Galahad', 'yellow');

create database test;
use test;
		
CREATE TABLE pattern (
id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
pattern VARCHAR(30) NOT NULL,
description VARCHAR(30) NOT NULL
);

INSERT INTO pattern (pattern, description)
VALUES ('Mama','Principal'),
('Breast','Main');
