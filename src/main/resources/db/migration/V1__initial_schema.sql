CREATE TABLE tenant
(
    id     int AUTO_INCREMENT PRIMARY KEY,
    name   varchar(255) NOT NULL,
    status varchar(255) NOT NULL
);

CREATE TABLE service
(
    id          int AUTO_INCREMENT PRIMARY KEY,
    name        varchar(255) NOT NULL,
    description text,
    status      varchar(255)
);

CREATE TABLE tenant_service
(
    tenant_id  int NOT NULL,
    service_id int NOT NULL,
    status     varchar(255),
    PRIMARY KEY (tenant_id, service_id)
);

CREATE TABLE permission
(
    id          int AUTO_INCREMENT PRIMARY KEY,
    name        varchar(255) NOT NULL,
    description text,
    scope       varchar(255)
);

CREATE TABLE role
(
    id          int AUTO_INCREMENT PRIMARY KEY,
    name        varchar(255) NOT NULL,
    description text
);

CREATE TABLE role_permission
(
    role_id       int NOT NULL,
    permission_id int NOT NULL,
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE user
(
    id       int AUTO_INCREMENT PRIMARY KEY,
    email    varchar(255) NOT NULL,
    password varchar(255),
    status   varchar(255),
    UNIQUE KEY unique_email (email)
);

CREATE TABLE user_role
(
    tenant_id int NOT NULL,
    user_id   int NOT NULL,
    role_id   int NOT NULL,
    PRIMARY KEY (tenant_id, user_id, role_id)
);

