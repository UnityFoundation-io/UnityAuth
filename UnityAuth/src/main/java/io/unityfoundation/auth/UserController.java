package io.unityfoundation.auth;

import io.micronaut.core.annotation.Nullable;
import io.micronaut.http.HttpResponse;
import io.micronaut.http.annotation.*;
import io.micronaut.security.annotation.Secured;
import io.micronaut.security.authentication.Authentication;
import io.micronaut.security.rules.SecurityRule;
import io.micronaut.serde.annotation.Serdeable;
import io.unityfoundation.auth.entities.*;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;

import java.util.List;

@Secured(SecurityRule.IS_AUTHENTICATED)
@Controller("/api/users")
public class UserController {

    private final UserRepo userRepo;
    private final TenantRepo tenantRepo;

    public UserController(UserRepo userRepo, TenantRepo tenantRepo) {
        this.userRepo = userRepo;
        this.tenantRepo = tenantRepo;
    }

    @Post
    public HttpResponse<?> createUser(@Body AddUserRequest requestDTO,
                                                 Authentication authentication) {

        Long requestTenantId = requestDTO.tenantId();

        // reject if the declared tenant does not exist
        if (tenantRepo.existsById(requestTenantId)) {
            return HttpResponse.badRequest("Tenant does not exist");
        }

        // reject if caller is not a unity nor tenant admin of the declared tenant
        if (!isUserUnityOrTenantAdmin(authentication.getName(), requestTenantId)) {
            return HttpResponse.badRequest("Authenticated user is not authorized to make changes under declared tenant.");
        }

        // reject if new user already exists under a tenant
        if (userRepo.existsByEmailAndTenantId(requestDTO.email(), requestTenantId)) {
            return HttpResponse.badRequest("User already exists under declared tenant.");
        }

        // reject if the declared roles supersede that of the authenticated user if authenticated user is not a unity admin
        // ie. first condition is applied assumes that authenticated user is a tenant admin of the declared tenant

        // if the new user exists, create a new user-role entry
        // otherwise, create the user along with user-role entry

    }

    @Patch("{id}/roles")
    public HttpResponse<UserResponse> updateUserRoles(@PathVariable Long id, @Body UpdateUserRolesRequest requestDTO,
                                                Authentication authentication) {
        // get user under tenant
        // if unity admin, proceed; otherwise, reject if roles exceed authenticated user's under same tenant.
        // apply patch


        // return updated user
    }

    @Patch("{id}")
    public HttpResponse<UserResponse> selfPatch(@PathVariable Long id, @Body UpdateSelfRequest requestDTO,
                                                Authentication authentication) {
        // get user (and verify id?)
        // perform patch

        // return updated user
    }

    private boolean isUserUnityOrTenantAdmin(String email, Long requestTenantId) {
        return false;
    }

    @Serdeable
    public record UpdateUserRolesRequest(
            @NotNull Long tenantId,
            List<String> roles) {
    }

    @Serdeable
    public record AddUserRequest(
            @NotBlank String email,
            @NotBlank String firstName,
            @NotBlank String lastName,
            @NotNull Long tenantId,
            @NotBlank String password,
            @NotEmpty List<String> roles) {
    }

    @Serdeable
    public record UpdateSelfRequest(
            @NotBlank String firstName,
            @NotBlank String lastName,
            @NotBlank String password) {
    }


}
