package io.unityfoundation.auth;

import static io.micronaut.security.authentication.AuthenticationFailureReason.CREDENTIALS_DO_NOT_MATCH;

import io.micronaut.core.annotation.NonNull;
import io.micronaut.core.annotation.Nullable;
import io.micronaut.http.HttpRequest;
import io.micronaut.security.authentication.Authentication;
import io.micronaut.security.authentication.AuthenticationException;
import io.micronaut.security.authentication.AuthenticationFailed;
import io.micronaut.security.authentication.AuthenticationProvider;
import io.micronaut.security.authentication.AuthenticationRequest;
import io.micronaut.security.authentication.AuthenticationResponse;
import io.micronaut.serde.annotation.Serdeable;
import io.unityfoundation.auth.entities.User;
import io.unityfoundation.auth.entities.UserRepo;
import jakarta.inject.Singleton;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import org.reactivestreams.Publisher;
import reactor.core.publisher.Mono;
import reactor.core.scheduler.Schedulers;

@Singleton
public class UnityAuthenticationProvider implements AuthenticationProvider<HttpRequest<?>> {

    public static class UnityAuthentication implements Authentication {

        User user;

        private UnityAuthentication(User user) {
            this.user = user;
        }

        public static UnityAuthentication from(User user) {
            return new UnityAuthentication(user);
        }

        Map<String, Object> attributes = new HashMap<>();

        @Override
        public @NonNull Map<String, Object> getAttributes() {
            return attributes;
        }

        @Override
        public String getName() {
            return this.user.getEmail();
        }

        public User getUser() {
            return this.user;
        }
    }

    @Serdeable
    static class UnityAuthenticationResponse implements AuthenticationResponse {

        Authentication authentication;

        private UnityAuthenticationResponse(User user) {
            this.authentication = UnityAuthentication.from(user);
        }

        static UnityAuthenticationResponse success(User user) {
            return new UnityAuthenticationResponse(user);
        }

        @Override
        public Optional<Authentication> getAuthentication() {
            return Optional.of(authentication);
        }
    }

    private final UserRepo userRepo;
    private final PasswordEncoder passwordEncoder;

    public UnityAuthenticationProvider(UserRepo userRepo,
        PasswordEncoder passwordEncoder) {
        this.userRepo = userRepo;
        this.passwordEncoder = passwordEncoder;
    }

    /**
     * Authenticates the user with the given authentication request.
     *
     * @param httpRequest           The HTTP request associated with the authentication.
     * @param authenticationRequest The authentication request containing user credentials.
     * @return A Publisher emitting an AuthenticationResponse upon successful authentication, or
     * throwing an AuthenticationException if authentication fails.
     */
    @Override
    public Publisher<AuthenticationResponse> authenticate(@Nullable HttpRequest<?> httpRequest,
        AuthenticationRequest<?, ?> authenticationRequest) {
        return Mono.fromCallable(() -> findUser(authenticationRequest))
            .subscribeOn(Schedulers.boundedElastic())
            .flatMap(user -> {
                AuthenticationFailed authenticationFailed = validate(user, authenticationRequest);
                if (authenticationFailed != null) {
                    return Mono.error(new AuthenticationException(authenticationFailed));
                } else {
                    return Mono.just(UnityAuthenticationResponse.success(user));
                }
            });
    }

    private AuthenticationFailed validate(User user,
        AuthenticationRequest<?, ?> authenticationRequest) {
        AuthenticationFailed authenticationFailed = null;
        if (user == null) {
            authenticationFailed = new AuthenticationFailed(CREDENTIALS_DO_NOT_MATCH);
        } else if (!passwordEncoder.matches(authenticationRequest.getSecret().toString(),
            user.getPassword())) {
            authenticationFailed = new AuthenticationFailed(CREDENTIALS_DO_NOT_MATCH);
        }

        return authenticationFailed;
    }

    private User findUser(AuthenticationRequest<?, ?> authRequest) {
        final Object username = authRequest.getIdentity();
        return userRepo.findUserForAuthentication(username.toString()).orElse(null);
    }

}

