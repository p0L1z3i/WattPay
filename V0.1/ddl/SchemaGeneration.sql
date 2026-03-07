-- Create schema (If you want any other schema instead of public)
CREATE SCHEMA IF NOT EXISTS "SaiKrupa";

SET search_path TO "SaiKrupa";

-- Create owners table
CREATE TABLE IF NOT EXISTS owners (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    contact VARCHAR(15),
    email VARCHAR(100)
);

-- Create tenants table
CREATE TABLE IF NOT EXISTS tenants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    user_name VARCHAR(100),
    contact VARCHAR(15),
    door_number INTEGER,
    floor VARCHAR(50),
    owner_id INTEGER,

    CONSTRAINT fk_owner
        FOREIGN KEY(owner_id)
            REFERENCES owners(id)
            ON DELETE RESTRICT
            ON UPDATE CASCADE
);
