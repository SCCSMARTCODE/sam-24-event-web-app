CREATE DATABASE IF NOT EXISTS sam24_base_db;

CREATE USER IF NOT EXISTS 'sam24_master'@'localhost' IDENTIFIED BY 'sam24_pass_master';
GRANT ALL PRIVILEGES ON smp_base_db.* TO 'sam24_master'@'localhost';
FLUSH PRIVILEGES;
