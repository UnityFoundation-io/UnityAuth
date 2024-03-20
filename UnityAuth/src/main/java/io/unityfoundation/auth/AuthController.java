package io.unityfoundation.auth;

import io.micronaut.core.annotation.Introspected;
import io.micronaut.core.annotation.Nullable;
import io.micronaut.http.HttpResponse;
import io.micronaut.http.annotation.Body;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;
import io.micronaut.security.annotation.Secured;
import io.micronaut.security.authentication.Authentication;
import io.micronaut.security.rules.SecurityRule;
import io.micronaut.serde.annotation.Serdeable;
import io.unityfoundation.auth.entities.Permission.PermissionScope;
import io.unityfoundation.auth.entities.Service;
import io.unityfoundation.auth.entities.Service.ServiceStatus;
import io.unityfoundation.auth.entities.ServiceRepo;
import io.unityfoundation.auth.entities.Tenant;
import io.unityfoundation.auth.entities.TenantRepo;
import io.unityfoundation.auth.entities.User;
import io.unityfoundation.auth.entities.UserRepo;
import java.util.List;
import java.util.Optional;

@Secured(SecurityRule.IS_AUTHENTICATED)
@Controller("/api")
public class AuthController {

  private final UserRepo userRepo;
  private final ServiceRepo serviceRepo;
  private final TenantRepo tenantRepo;

  public AuthController(UserRepo userRepo, ServiceRepo serviceRepo, TenantRepo tenantRepo) {
    this.userRepo = userRepo;
    this.serviceRepo = serviceRepo;
    this.tenantRepo = tenantRepo;
  }

  @Post("/hasPermission")
  public HttpResponse<HasPermissionResponse> hasPermission(@Body HasPermissionRequest requestDTO,
      Authentication authentication) {

    Optional<Tenant> tenantOptional = tenantRepo.findById(requestDTO.tenantId());
    if (tenantOptional.isEmpty()) {
      return createHasPermissionResponse(false, authentication.getName(),null, null, "Cannot find tenant!", List.of());
    }

    User user = userRepo.findByEmail(authentication.getName()).orElse(null);
    if (checkUserStatus(user)) {
      return createHasPermissionResponse(false, authentication.getName(), null, null, "The user’s account has been disabled!", List.of());
    }

    Optional<Service> service = serviceRepo.findById(requestDTO.serviceId());

    String serviceStatusCheckResult = checkServiceStatus(service);
    if (serviceStatusCheckResult != null) {
      return createHasPermissionResponse(false, user.getEmail(), user.getFirstName(), user.getLastName(), serviceStatusCheckResult, List.of());
    }

    if (!userRepo.isServiceAvailable(user.getId(), service.get().getId())) {
      return createHasPermissionResponse(false, user.getEmail(), user.getFirstName(), user.getLastName(),
          "The requested service is not enabled for the requested tenant!", List.of());
    }

    List<String> commonPermissions = checkUserPermission(user, tenantOptional.get(), requestDTO.permissions());
    if (commonPermissions.isEmpty()) {
      return createHasPermissionResponse(false, user.getEmail(), user.getFirstName(), user.getLastName(), "The user does not have permission!", commonPermissions);
    }

    return createHasPermissionResponse(true, user.getEmail(), user.getFirstName(), user.getLastName(), null, commonPermissions);
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

  private List<String> checkUserPermission(User user, Tenant tenant, List<String> permissions) {
    List<TenantPermission> userPermissions = userRepo.getTenantPermissionsFor(user.getId()).stream()
        .filter(tenantPermission ->
            PermissionScope.SYSTEM.equals(tenantPermission.permissionScope()) ||
            ((PermissionScope.TENANT.equals(tenantPermission.permissionScope()) || PermissionScope.SUBTENANT.equals(tenantPermission.permissionScope()))
             && tenantPermission.tenantId == tenant.getId()))
        .toList();

    List<String> commonPermissions = userPermissions.stream()
        .map(TenantPermission::permissionName)
        .filter(permissions::contains)
        .toList();

    return commonPermissions;
  }

  private HttpResponse<HasPermissionResponse> createHasPermissionResponse(boolean hasPermission,
                                                                          String userEmail,
                                                                          String firstName,
                                                                          String lastName,
                                                                          String message,
                                                                          List<String> permissions) {
    return HttpResponse.ok(new HasPermissionResponse(hasPermission, userEmail, firstName, lastName, message, permissions));
  }

  @Serdeable
  public record HasPermissionResponse(
      boolean hasPermission,
      @Nullable String userEmail,
      @Nullable String firstName,
      @Nullable String lastName,
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

}
