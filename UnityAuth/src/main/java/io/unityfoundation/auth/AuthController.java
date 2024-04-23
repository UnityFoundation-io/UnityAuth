package io.unityfoundation.auth;

import io.micronaut.core.annotation.Introspected;
import io.micronaut.core.annotation.Nullable;
import io.micronaut.http.HttpResponse;
import io.micronaut.http.HttpStatus;
import io.micronaut.http.annotation.*;
import io.micronaut.http.exceptions.HttpStatusException;
import io.micronaut.security.annotation.Secured;
import io.micronaut.security.authentication.Authentication;
import io.micronaut.security.rules.SecurityRule;
import io.micronaut.serde.annotation.Serdeable;
import io.unityfoundation.auth.entities.*;
import io.unityfoundation.auth.entities.Permission.PermissionScope;
import io.unityfoundation.auth.entities.Service.ServiceStatus;
import jakarta.validation.constraints.NotNull;
import java.util.List;
import java.util.Optional;
import java.util.function.BiPredicate;

@Secured(SecurityRule.IS_AUTHENTICATED)
@Controller("/api")
public class AuthController {

  private final UserRepo userRepo;
  private final ServiceRepo serviceRepo;
  private final TenantRepo tenantRepo;
  private final RoleRepo roleRepo;

  public AuthController(UserRepo userRepo, ServiceRepo serviceRepo, TenantRepo tenantRepo, RoleRepo roleRepo) {
    this.userRepo = userRepo;
    this.serviceRepo = serviceRepo;
    this.tenantRepo = tenantRepo;
      this.roleRepo = roleRepo;
  }

  @Post("/principal/permissions")
  public UserPermissionsResponse permissions(@Body UserPermissionsRequest requestDTO,
      Authentication authentication) {
    Optional<Tenant> maybeTenant = tenantRepo.findById(requestDTO.tenantId());
    if (maybeTenant.isEmpty()){
      return new UserPermissionsResponse.Failure("No tenant found.");
    }
    Tenant tenant = maybeTenant.get();

    if (!tenant.getStatus().equals(Tenant.TenantStatus.ENABLED)){
      return new UserPermissionsResponse.Failure("The tenant is not enabled.");
    }

    User user = userRepo.findByEmail(authentication.getName()).orElse(null);
    if (checkUserStatus(user)) {
      return new UserPermissionsResponse.Failure("The user's account has been disabled.");
    }

    Service service = serviceRepo.findById(requestDTO.serviceId())
        .orElseThrow(() -> new HttpStatusException(HttpStatus.NOT_FOUND, "Service not found."));

    if (service.getStatus() == ServiceStatus.DISABLED) {
      throw new HttpStatusException(HttpStatus.FORBIDDEN, "The service is disabled.");
    } else if (service.getStatus() == ServiceStatus.DOWN_FOR_MAINTENANCE) {

      throw new HttpStatusException(HttpStatus.SERVICE_UNAVAILABLE,
          "The service is down for maintenance.");
    }

    if (!userRepo.isServiceAvailable(user.getId(), service.getId())) {
      return new UserPermissionsResponse.Failure(
          "The Tenant and/or Service is not available for this user");
    }

    return new UserPermissionsResponse.Success(getPermissionsFor(user, tenant));
  }

  @Post("/hasPermission")
  public HttpResponse<HasPermissionResponse> hasPermission(@Body HasPermissionRequest requestDTO,
      Authentication authentication) {

    Optional<Tenant> tenantOptional = tenantRepo.findById(requestDTO.tenantId());
    if (tenantOptional.isEmpty()) {
      return createHasPermissionResponse(false, authentication.getName(),"Cannot find tenant!", List.of());
    }

    User user = userRepo.findByEmail(authentication.getName()).orElse(null);
    if (checkUserStatus(user)) {
      return createHasPermissionResponse(false, authentication.getName(), "The user’s account has been disabled!", List.of());
    }

    Optional<Service> service = serviceRepo.findById(requestDTO.serviceId());

    String serviceStatusCheckResult = checkServiceStatus(service);
    if (serviceStatusCheckResult != null) {
      return createHasPermissionResponse(false, user.getEmail(), serviceStatusCheckResult, List.of());
    }

    if (!userRepo.isServiceAvailable(user.getId(), service.get().getId())) {
      return createHasPermissionResponse(false, user.getEmail(), "The requested service is not enabled for the requested tenant!", List.of());
    }

    List<String> commonPermissions = checkUserPermission(user, tenantOptional.get(), requestDTO.permissions());
    if (commonPermissions.isEmpty()) {
      return createHasPermissionResponse(false, user.getEmail(), "The user does not have permission!", commonPermissions);
    }

    return createHasPermissionResponse(true, user.getEmail(), null, commonPermissions);
  }

  @Get("/roles")
  public HttpResponse<?> getRoles() {
    return HttpResponse.ok(roleRepo.findAll());
  }

  @Get("/tenants")
  public HttpResponse<?> getTenants(Authentication authentication) {

    String authenticatedUserEmail = authentication.getName();

    if(userRepo.existsByEmailAndRoleEqualsUnityAdmin(authenticatedUserEmail)) {
      return HttpResponse.ok(tenantRepo.findAll());
    }

    return HttpResponse.ok(tenantRepo.findAllByUserEmail(authenticatedUserEmail));
  }

  @Get("/tenants/{id}/users")
  public HttpResponse<List<UserResponse>> getTenantUsers(@PathVariable Long id, Authentication authentication) {

    // reject if the declared tenant does not exist
    if (tenantRepo.existsById(id)) {
      return HttpResponse.badRequest();
    }

    // todo: it would be nice to capture the roles and have them automatically mapped to UserResponse.roles
    List<UserResponse> tenantUsers = userRepo.findAllByTenantId(id).stream().map(user ->
            new UserResponse(user.getId(), user.getEmail(), user.getFirstName(), user.getLastName(),
                    userRepo.getUserRolesByUserId(user.getId())
                    )).toList();

    return HttpResponse.ok(tenantUsers);
  }

  private boolean checkUserStatus(User user) {
    return user == null || user.getStatus() != User.UserStatus.ENABLED;
  }

  private String checkServiceStatus(Optional<Service> service) {
    if (service.isEmpty()) {
      return "The service does not exists!";
    } else {
      ServiceStatus status = service.get().getStatus();
      if (ServiceStatus.DISABLED.equals(status)) {
        return "The service is disabled!";
      } else if (ServiceStatus.DOWN_FOR_MAINTENANCE.equals(status)) {
        return "The service is temporarily down for maintenance!";
      }
    }
    return null;
  }

    private final BiPredicate<TenantPermission, Tenant> isTenantOrSystemOrSubtenantScopeAndBelongsToTenant = (tp, t) ->
        PermissionScope.SYSTEM.equals(tp.permissionScope()) || (
            (PermissionScope.TENANT.equals(tp.permissionScope())
                || PermissionScope.SUBTENANT.equals(tp.permissionScope()))
                && tp.tenantId == t.getId());


  private List<String> checkUserPermission(User user, Tenant tenant, List<String> permissions) {
    List<String> commonPermissions = getPermissionsFor(user, tenant).stream()
        .filter(permissions::contains).toList();

    return commonPermissions;
  }

  private List<String> getPermissionsFor(User user, Tenant tenant) {
    return userRepo.getTenantPermissionsFor(user.getId()).stream()
        .filter(tenantPermission ->
            isTenantOrSystemOrSubtenantScopeAndBelongsToTenant.test(tenantPermission, tenant))
        .map(TenantPermission::permissionName)
        .toList();
  }

  private HttpResponse<HasPermissionResponse> createHasPermissionResponse(boolean hasPermission,
                                                                          String userEmail,
                                                                          String message,
                                                                          List<String> permissions) {
    return HttpResponse.ok(new HasPermissionResponse(hasPermission, userEmail, message, permissions));
  }

  @Serdeable
  public record HasPermissionResponse(
      boolean hasPermission,
      @Nullable String userEmail,
      @Nullable String errorMessage,
      List<String> permissions
  ) {

  }

  @Introspected
  public record TenantPermission(
      long tenantId,
      String permissionName,
      PermissionScope permissionScope

  ) {

  }


  public sealed interface UserPermissionsResponse {
    @Serdeable
    record Success(List<String> permissions) implements UserPermissionsResponse {}
    @Serdeable
    record Failure(String errorMessage) implements  UserPermissionsResponse {}
  }

  @Serdeable
  public record UserPermissionsRequest(@NotNull Long tenantId,
                                       @NotNull Long serviceId) {

  }

}
