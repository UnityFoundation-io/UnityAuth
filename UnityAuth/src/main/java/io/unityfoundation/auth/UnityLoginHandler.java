package io.unityfoundation.auth;

import io.micronaut.context.annotation.Primary;
import io.micronaut.http.HttpRequest;
import io.micronaut.http.HttpResponse;
import io.micronaut.http.MutableHttpResponse;
import io.micronaut.security.authentication.Authentication;
import io.micronaut.security.authentication.AuthenticationResponse;
import io.micronaut.security.handlers.LoginHandler;
import io.micronaut.security.token.bearer.AccessRefreshTokenLoginHandler;
import io.micronaut.security.token.generator.AccessRefreshTokenGenerator;
import io.micronaut.security.token.render.AccessRefreshToken;
import io.micronaut.serde.annotation.Serdeable;
import io.unityfoundation.auth.UnityAuthenticationProvider.UnityAuthentication;
import jakarta.inject.Singleton;
import java.util.Optional;

@Singleton
@Primary
public class UnityLoginHandler implements LoginHandler<HttpRequest<?>, MutableHttpResponse<?>> {

    @Serdeable
    public static class UnityLoginResponse {

        AccessRefreshToken tokenInfo;
        String firstName;
        String lastName;

        public UnityLoginResponse(AccessRefreshToken art, UnityAuthentication unityAuthentication) {
            tokenInfo = art;
            firstName = "todo";
            lastName = "todo";
//            firstName = unityAuthentication.getUser().getFirstName()
//            lastName = unityAuthentication.getUser().getLastName();
        }

        public AccessRefreshToken getTokenInfo() {
            return tokenInfo;
        }

        public String getFirstName() {
            return firstName;
        }

        public String getLastName() {
            return lastName;
        }
    }

    AccessRefreshTokenLoginHandler accessRefreshTokenLoginHandler;
    AccessRefreshTokenGenerator accessRefreshTokenGenerator;

    public UnityLoginHandler(AccessRefreshTokenLoginHandler accessRefreshTokenLoginHandler,
        AccessRefreshTokenGenerator accessRefreshTokenGenerator) {
        this.accessRefreshTokenLoginHandler = accessRefreshTokenLoginHandler;
        this.accessRefreshTokenGenerator = accessRefreshTokenGenerator;
    }

    @Override
    public MutableHttpResponse<?> loginSuccess(Authentication authentication,
        HttpRequest<?> request) {
        Optional<AccessRefreshToken> accessRefreshTokenOptional = this.accessRefreshTokenGenerator.generate(
            authentication);

        return accessRefreshTokenOptional.isPresent() ? HttpResponse.ok(
            new UnityLoginResponse(accessRefreshTokenOptional.get(),
                (UnityAuthentication) authentication)) : HttpResponse.serverError();
    }

    @Override
    public MutableHttpResponse<?> loginRefresh(Authentication authentication, String refreshToken,
        HttpRequest<?> request) {
        return accessRefreshTokenLoginHandler.loginRefresh(authentication, refreshToken, request);
    }

    @Override
    public MutableHttpResponse<?> loginFailed(AuthenticationResponse authenticationResponse,
        HttpRequest<?> request) {
        return accessRefreshTokenLoginHandler.loginFailed(authenticationResponse, request);
    }
}
