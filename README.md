# UnityAuth

UnityAuth is a comprehensive authentication and authorization service built with modern
microservices architecture. It provides JWT-based authentication, user management, and
a web-based administration interface.

## QuickStart

### Local Environment
From the project root, copy `setenv.sh.example` into `setenv.sh` and update the correct
environment variable values.
* If used together with Libre311 project
(https://github.com/UnityFoundation-io/Libre311.git), `LIBRE311_UI_BASE_URL` must be updated
to base URL of Libre311 UI.
* If use a local database, also update the `DATASOURCES_DEFAULT_*` environment variables
  for the corresponding database.

Run the UnityAuth API with:
```shell
source setenv.sh
cd UnityAuth
./gradlew run
```
This starts the UnityAuth API server on http://localhost:9090 if the `MICRONAUT_ENVIRONMENTS`
environment variable contains `local`.

Run the UnityAuth UI in another terminal windows:
```shell
source setenv.sh
cd frontend
npm install
npm run dev
```
This starts the frontend on http://localhost:3001.

### Docker Environment
To launch the auth service, you can use the docker compose from the project root:

```sh
docker compose -f docker-compose.local.yml up
```

This will start containers for the UnityAuth API, UI and database server with service
names `unity-auth-api`, `unity-auth-ui`, and `unity-auth-db`, respectively.

- **UnityAuth API** on http://localhost:9090 (inside Docker http://unity-auth-api:9090)
- **UnityAuth UI** on http://localhost:3001 (inside Docker http://unity-auth-ui:3001)
- **MySQL Database** is open on port `13306` in `localhost` (within Docker is port `3306`
  with host name `unity-auth-db`)

#### Hosts File Updates

When using Docker environment, add these to your `/etc/hosts` file
for consistent internal-external service name resolution:

```txt
127.0.0.1 unity-auth-api
127.0.0.1 unity-auth-ui
```

You can log in with these accounts.
**Password for all the following accounts is `test`**

- **Unity Administrator** `unity_admin@example.com`
- **Tenant Administrator** `tenant_admin@example.com`
- **Libre311 Administrator** `libre311_admin@example.com`
- **Libre311 Request Manager** `libre311_request_manager@example.com`
- **Libre311 Jurisdiction Administrator** `libre311_jurisdiction_admin@example.com`
- **Libre311 Jurisdiction Request Manager** `libre311_jurisdiction_request_manager@example.com`
- **STL Sub-tenant Administrator** `stl_subtenant_admin@example.com`

## Project Structure

This repository contains three main subprojects:

### 1. UnityAuth (Main Service)

**Location:** `/UnityAuth`

**Technology:** Java 21 + Micronaut Framework

The core authentication service that provides:

- JWT token generation and validation
- User authentication and authorization
- RESTful API endpoints for authentication operations
- Database integration with MySQL
- JWK (JSON Web Key) management for token signing
- Flyway database migrations

**Key Features:**

- Micronaut-based microservice architecture
- JWT security with configurable key rotation
- BCrypt password hashing
- Database connection pooling with HikariCP
- Reactive programming support with Reactor

### 2. AuthGenHash (Utility Tool)

**Location:** `/AuthGenHash`

**Technology:** Java 17 + Micronaut + PicoCLI

A command-line utility for generating secure password hashes compatible with the UnityAuth service.

**Purpose:**

- Generate BCrypt password hashes for administrative users
- Secure password handling (interactive mode prevents history logging)
- Standalone tool for initial system setup and user management

### 3. Frontend (Web Administration Interface)

**Location:** `/frontend`

**Technology:** SvelteKit + TypeScript + Tailwind CSS

A modern web application providing administrative interface for the UnityAuth service.

**Features:**

- User authentication and session management
- User administration and management
- Tenant management capabilities
- Settings configuration
- Responsive design with Tailwind CSS
- TypeScript for type safety
- Comprehensive testing with Playwright and Vitest

**Key Technologies:**

- SvelteKit for the web framework
- TypeScript for type safety
- Tailwind CSS for styling
- Playwright for end-to-end testing
- Vitest for unit testing
- ESLint and Prettier for code quality

## Architecture Overview

The system follows a microservices architecture:

1. **Database Layer:** MySQL database for persistent storage
2. **API Layer:** UnityAuth service provides REST APIs
3. **Frontend Layer:** SvelteKit web application
4. **Utility Layer:** AuthGenHash for administrative tasks

## Client Integration

To integrate with the UnityAuth service, add this configuration to your client application's `application.yaml`:

```yaml
security:
  enabled: true
  token:
    enabled: true
    jwt:
      enabled: true
      signatures:
        jwks:
          unity:
            url: ${AUTH_JWKS:`http://localhost:8081/keys`}
```

## Security Configuration

The service uses JSON Web Keys (JWK) for token signing. To generate primary and secondary keys:

1. Visit <https://mkjwk.org/>
2. Generate JSON Web Keys
3. Set environment variables:
   - `JWK_PRIMARY`: Primary signing key
   - `JWK_SECONDARY`: Secondary signing key for rotation

## Development Environment

### Prerequisites

- Java 17 or higher
- Node.js 18 or higher
- Docker and Docker Compose
- MySQL 8.0 (if running locally)

### Individual Service Development

#### UnityAuth Service

```bash
cd UnityAuth
./gradlew run
```

#### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

#### AuthGenHash Utility

```bash
cd AuthGenHash
./gradlew shadowJar
java -jar build/libs/AuthGenHash-0.1-all.jar -p
```
