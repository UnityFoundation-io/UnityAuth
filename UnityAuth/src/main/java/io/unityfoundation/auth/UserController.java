package io.unityfoundation.auth;

import io.micronaut.http.HttpResponse;
import io.micronaut.http.HttpStatus;
import io.micronaut.http.annotation.*;
import io.micronaut.security.annotation.Secured;
import io.micronaut.security.authentication.Authentication;
import io.micronaut.security.rules.SecurityRule;
import io.micronaut.serde.annotation.Serdeable;
import io.unityfoundation.auth.entities.*;
import jakarta.transaction.Transactional;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;

import java.util.List;
import java.util.Objects;
import java.util.Optional;

@Secured(SecurityRule.IS_AUTHENTICATED)
@Controller("/api/users")
public class UserController {

    private final UserRepo userRepo;
    private final TenantRepo tenantRepo;
    private final RoleRepo roleRepo;

    public UserController(UserRepo userRepo, TenantRepo tenantRepo, RoleRepo roleRepo) {
        this.userRepo = userRepo;
        this.tenantRepo = tenantRepo;
        this.roleRepo = roleRepo;
    }

    @Post
    public HttpResponse<?> createUser(@Body AddUserRequest requestDTO,
                                                 Authentication authentication) {

        Long requestTenantId = requestDTO.tenantId();

        // reject if the declared tenant does not exist
        if (tenantRepo.existsById(requestTenantId)) {
            return HttpResponse.notFound("Tenant does not exist");
        }

        Role unityAdministrator = roleRepo.findByName("Unity Administrator");

        // ignore roles not defined by application
        List<Long> rolesIntersection = getRolesIntersection(requestDTO.roles());

        // reject if caller is not a unity nor tenant admin of the declared tenant
        String authUserEmail = authentication.getName();
        if (!userRepo.existsByEmailAndRoleEqualsUnityAdmin(authUserEmail)) {
            if (!userRepo.existsByEmailAndTenantEqualsAndIsTenantAdmin(authUserEmail, requestTenantId)) {
                return HttpResponse.status(HttpStatus.FORBIDDEN,
                        "Authenticated user is not authorized to make changes under declared tenant.");
            } else if (rolesIntersection.stream().anyMatch(roleId -> roleId.equals(unityAdministrator.getId()))){
                // authenticated tenant admin user cannot grant unity admin role
                return HttpResponse.status(HttpStatus.FORBIDDEN,
                        "Authenticated user is not authorized to grant Unity Admin");
            }
        }

        // reject if new user already exists under a tenant
        if (userRepo.existsByEmailAndTenantId(requestDTO.email(), requestTenantId)) {
            return HttpResponse.badRequest("User already exists under declared tenant.");
        }

        // if the new user exists, create a new user-role entry
        // otherwise, create the user along with user-role entry
        Optional<User> userOptional = userRepo.findByEmail(requestDTO.email());
        User user;
        if (userOptional.isEmpty()) {
            User newUser = new User();
            newUser.setEmail(requestDTO.email());
            newUser.setPassword(requestDTO.password());
            newUser.setFirstName(requestDTO.firstName);
            newUser.setLastName(requestDTO.lastName);
            newUser.setStatus(User.UserStatus.ENABLED);
            user = userRepo.save(newUser);
        } else {
            user = userOptional.get();
        }

        rolesIntersection.forEach(roleId -> userRepo.insertUserRole(user.getId(), requestTenantId, roleId));

        return HttpResponse.created(new UserResponse(user.getId(),
                user.getEmail(),
                user.getFirstName(),
                user.getLastName(),
                rolesIntersection));
    }

    @Patch("{id}/roles")
    public HttpResponse<?> updateUserRoles(@PathVariable Long id, @Body UpdateUserRolesRequest requestDTO,
                                                Authentication authentication) {
        Long requestTenantId = requestDTO.tenantId();

        // reject if the declared tenant does not exist
        if (tenantRepo.existsById(requestTenantId)) {
            return HttpResponse.notFound("Tenant does not exist");
        }

        Optional<User> userOptional = userRepo.findById(id);
        if (userOptional.isEmpty()) {
            return HttpResponse.notFound("User not found.");
        }

        User user = userOptional.get();
        Role unityAdministrator = roleRepo.findByName("Unity Administrator");

        // ignore roles not defined by application
        List<Long> rolesIntersection = getRolesIntersection(requestDTO.roles());

        // if unity admin, proceed; otherwise, reject if roles exceed authenticated user's under same tenant.
        String authUserEmail = authentication.getName();
        if (!userRepo.existsByEmailAndRoleEqualsUnityAdmin(authUserEmail)) {
            if (!userRepo.existsByEmailAndTenantEqualsAndIsTenantAdmin(authUserEmail, requestTenantId)) {
                return HttpResponse.status(HttpStatus.FORBIDDEN,
                        "Authenticated user is not authorized to make changes under declared tenant.");
            } else if (rolesIntersection.stream().anyMatch(roleId -> roleId.equals(unityAdministrator.getId()))){
                // authenticated tenant admin user cannot grant unity admin role
                return HttpResponse.status(HttpStatus.FORBIDDEN,
                        "Authenticated user is not authorized to grant Unity Admin");
            }
        }

        applyRolesPatch(rolesIntersection, requestTenantId, user.getId());

        // return updated user
        return HttpResponse.created(new UserResponse(user.getId(),
                user.getEmail(),
                user.getFirstName(),
                user.getLastName(),
                rolesIntersection));
    }

    private List<Long> getRolesIntersection(List<Long> requestRoles) {
        List<Long> roles = roleRepo.findAllRoleIds();
        return requestRoles.stream()
                .distinct()
                .filter(roles::contains)
                .toList();
    }


    @Transactional
    public void applyRolesPatch(List<Long> requestRoles, Long requestTenantId, Long userId) {
        userRepo.deleteRoleByTenantIdAndUserId(requestTenantId, userId);
        requestRoles.forEach(roleId -> userRepo.insertUserRole(userId, requestTenantId, roleId));
    }

    @Patch("{id}")
    public HttpResponse<?> selfPatch(@PathVariable Long id, @Body UpdateSelfRequest requestDTO,
                                                Authentication authentication) {

        Optional<User> userOptional = userRepo.findByEmail(authentication.getName());
        if (userOptional.isEmpty()) {
            return HttpResponse.notFound("User not found.");
        }

        User user = userOptional.get();
        if (!Objects.equals(user.getId(), id)) {
            return HttpResponse.badRequest("User id mismatch.");
        }

        if (requestDTO.firstName != null) {
            user.setFirstName(requestDTO.firstName);
        }
        if (requestDTO.lastName != null) {
            user.setLastName(requestDTO.lastName);
        }
        if (requestDTO.password != null) {
            user.setPassword(requestDTO.password);
        }

        User saved = userRepo.save(user);
        return HttpResponse.ok(new UserResponse(saved.getId(), saved.getEmail(), saved.getFirstName(), saved.getLastName(),
                userRepo.getUserRolesByUserId(saved.getId())));
    }

    @Serdeable
    public record UpdateUserRolesRequest(
            @NotNull Long tenantId,
            List<Long> roles) {
    }

    @Serdeable
    public record AddUserRequest(
            @NotBlank String email,
            @NotBlank String firstName,
            @NotBlank String lastName,
            @NotNull Long tenantId,
            @NotBlank String password,
            @NotEmpty List<Long> roles) {
    }

    @Serdeable
    public record UpdateSelfRequest(
            @NotBlank String firstName,
            @NotBlank String lastName,
            @NotBlank String password) {
    }
}
