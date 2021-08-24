create database test;
use test;
		
CREATE TABLE pattern (
    id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    pattern VARCHAR(30) NOT NULL,
    description VARCHAR(30) NOT NULL
);

INSERT INTO 
    pattern (pattern, description)
VALUES 
    ('Cancer de mama','Principales'),
    ('Breast cancer','Main'),
    ('Cancer de cervix','Principales'),
    ('Cervical Cancer','Main'),
    ('Cancer de prostata','Principales'),
    ('Prostate cancer','Main'),
    ('Cancer de pulmon','Principales'),
    ('Lung cancer','Main');
