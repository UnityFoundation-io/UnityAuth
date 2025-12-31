# UnityAuth
Unity foundation security server

## Developer Setup

### Prerequisites

- **Java 21** (required - the project will not build with other versions)
- Gradle (wrapper included)

If you use SDKMAN, you can install and switch to Java 21:
```bash
sdk install java 21.0.2-tem   # or any Java 21 distribution
sdk use java 21.0.2-tem
```

### Running Tests

Run tests from the `UnityAuth` directory:
```bash
cd UnityAuth
./gradlew test
```

**Note:** Tests explicitly use the `test` environment via `@MicronautTest(environments = "test")`, so they will work correctly even if you have `MICRONAUT_ENVIRONMENTS=local` set in your shell.

### Running the Application

```bash
cd UnityAuth
source ../setenv.sh   # Set environment variables (edit first with your DB credentials)
./gradlew run
```

## CORS Configuration

UnityAuth includes CORS (Cross-Origin Resource Sharing) configuration to allow frontend applications to make requests to the API.

### Allowed Origins

CORS is configured to allow requests from:
- `http://localhost:3000` and `http://localhost:3001` (local development)
- `http://127.0.0.1:3000` and `http://127.0.0.1:3001` (local development)
- Docker container hostnames (e.g., `http://unity-auth-ui:3001`)

### Configuration Files

CORS settings are defined in environment-specific configuration files:
- `application-local.yml` - Local development
- `application-docker.yml` - Docker environment
- `application-test.yml` - Test environment

### Example Configuration

```yaml
micronaut:
  server:
    cors:
      enabled: true
      configurations:
        web:
          allowed-origins-regex: '^http:\/\/(.*?)(?:localhost|127\.0\.0\.1)(?::\d+)?$'
          allowedOrigins:
            - http://localhost:3000
            - http://localhost:3001
      localhost-pass-through: true
```

### Production Considerations

For production deployments, update the `allowed-origins-regex` and `allowedOrigins` to match your actual frontend domain(s).

## Usage:
Insert this code to the client application.yaml file
```
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
AUTH_JWKS points to this service:

## How to create primary and secondary key
Go to the https://mkjwk.org/. Create the JSON Web Keys and define JWK_PRIMARY and JWK_SECONDARY environment variables with generated JSON Web Key (JWK).


