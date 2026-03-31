package io.unityfoundation.auth;

import io.micronaut.context.annotation.Value;
import io.micronaut.http.HttpRequest;
import io.micronaut.http.HttpResponse;
import io.micronaut.http.HttpStatus;
import io.micronaut.http.annotation.*;
import io.micronaut.http.exceptions.HttpStatusException;
import io.micronaut.security.annotation.Secured;
import io.micronaut.security.rules.SecurityRule;
import io.micronaut.serde.annotation.Serdeable;
import io.unityfoundation.auth.entities.PasswordResetToken;
import io.unityfoundation.auth.entities.PasswordResetTokenRepo;
import io.unityfoundation.auth.entities.User;
import io.unityfoundation.auth.entities.UserRepo;
import jakarta.transaction.Transactional;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Optional;
import java.util.UUID;

@Secured(SecurityRule.IS_ANONYMOUS)
@Controller("/api/password-reset")
public class PasswordResetController {

    private final UserRepo userRepo;
    private final PasswordResetTokenRepo tokenRepo;
    private final PasswordEncoder passwordEncoder;

    @Value("${unity.auth.internal-token}")
    protected String internalToken;

    public PasswordResetController(UserRepo userRepo, PasswordResetTokenRepo tokenRepo, PasswordEncoder passwordEncoder) {
        this.userRepo = userRepo;
        this.tokenRepo = tokenRepo;
        this.passwordEncoder = passwordEncoder;
    }

    @Post("/generate")
    public HttpResponse<GenerateTokenResponse> generateToken(@Body @Valid GenerateTokenRequest request, HttpRequest<?> httpRequest) {
        String authHeader = httpRequest.getHeaders().get("X-Unity-Auth-Internal");
        if (internalToken == null || !internalToken.equals(authHeader)) {
            return HttpResponse.status(HttpStatus.FORBIDDEN);
        }

        Optional<User> userOptional = userRepo.findByEmail(request.email());
        if (userOptional.isEmpty()) {
            // We return 200 even if user not found for security reasons in public APIs, 
            // but this is an internal API so we can be more explicit if we want.
            // Let's stay explicit for internal use.
            throw new HttpStatusException(HttpStatus.NOT_FOUND, "User not found");
        }

        User user = userOptional.get();
        tokenRepo.deleteByUserId(user.getId());

        PasswordResetToken token = new PasswordResetToken();
        token.setToken(UUID.randomUUID().toString());
        token.setUserId(user.getId());
        token.setExpiry(Instant.now().plus(1, ChronoUnit.HOURS));
        tokenRepo.save(token);

        return HttpResponse.ok(new GenerateTokenResponse(token.getToken()));
    }

    @Post("/reset")
    @Transactional
    public HttpResponse<?> resetPassword(@Body @Valid ResetPasswordRequest request, HttpRequest<?> httpRequest) {
        String authHeader = httpRequest.getHeaders().get("X-Unity-Auth-Internal");
        if (internalToken == null || !internalToken.equals(authHeader)) {
            return HttpResponse.status(HttpStatus.FORBIDDEN);
        }

        Optional<PasswordResetToken> tokenOptional = tokenRepo.findByToken(request.token());
        
        if (tokenOptional.isEmpty()) {
            throw new HttpStatusException(HttpStatus.BAD_REQUEST, "Invalid token");
        }

        PasswordResetToken token = tokenOptional.get();
        if (token.getExpiry().isBefore(Instant.now())) {
            tokenRepo.delete(token);
            throw new HttpStatusException(HttpStatus.BAD_REQUEST, "Token expired");
        }

        Optional<User> userOptional = userRepo.findById(token.getUserId());
        if (userOptional.isEmpty()) {
            throw new HttpStatusException(HttpStatus.INTERNAL_SERVER_ERROR, "User not found");
        }

        User user = userOptional.get();
        user.setPassword(passwordEncoder.encode(request.newPassword()));
        userRepo.update(user);

        tokenRepo.delete(token);

        return HttpResponse.ok();
    }

    @Serdeable
    public record GenerateTokenRequest(@NotBlank String email) {}

    @Serdeable
    public record GenerateTokenResponse(@NotBlank String token) {}

    @Serdeable
    public record ResetPasswordRequest(@NotBlank String token, @NotBlank String newPassword) {}
}
