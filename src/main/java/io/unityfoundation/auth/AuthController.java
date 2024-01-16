package io.unityfoundation.auth;

import io.micronaut.core.annotation.Nullable;
import io.micronaut.http.annotation.Body;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;
import io.micronaut.http.annotation.QueryValue;
import io.micronaut.security.annotation.Secured;
import io.micronaut.security.authentication.Authentication;
import io.micronaut.security.rules.SecurityRule;
import io.unityfoundation.auth.entities.Permission.PermissionScope;
import io.unityfoundation.auth.entities.Service;
import io.unityfoundation.auth.entities.ServiceRepo;
import io.unityfoundation.auth.entities.Tenant;
import io.unityfoundation.auth.entities.Tenant.TenantStatus;
import io.unityfoundation.auth.entities.User;
import io.unityfoundation.auth.entities.UserRepo;
import java.util.Collections;
import java.util.List;
import java.util.Optional;

@Secured(SecurityRule.IS_AUTHENTICATED)
@Controller("/api")
public class AuthController {

  private final UserRepo userRepo;
  private final ServiceRepo serviceRepo;

  public AuthController(UserRepo userRepo, ServiceRepo serviceRepo) {
    this.userRepo = userRepo;
    this.serviceRepo = serviceRepo;
  }

  /**
   * Checks if a user has permission based on the given request.
   *
   * @param requestDTO      the request object containing the necessary information
   * @param subtenant       the flag indicating if the permission is for a subtenant (optional)
   * @param authentication the user's authentication information
   * @return true if the user has the permission, false otherwise
   */
  @Post("/hasPermission{?subtenant}")
  public boolean hasPermission(@Body HasPermissionRequest requestDTO,
      @Nullable @QueryValue("subtenant") Boolean subtenant, Authentication authentication) {
    User user = userRepo.findByEmail(authentication.getName()).orElse(null);
    if (user == null || user.getStatus() != User.UserStatus.ENABLED) {
      return false;
    }

    if (requestDTO.tenantId() == null) {
      return false;
    }

    Optional<Tenant> t = user.getTenants().stream()
        .filter(tenant -> requestDTO.tenantId().equals(tenant.getId()))
        .findFirst();

    if (!(t.isPresent() && TenantStatus.ACTIVE.equals(t.get().getStatus()))) {
      return false;
    }

    return hasPermissionForScope(requestDTO, subtenant, user, t.get());
  }

  private boolean hasPermissionForScope(HasPermissionRequest requestDTO, Boolean subtenant,
      User user, Tenant tenant) {
    PermissionScope scope;
    if (subtenant != null && subtenant) {
      Optional<Service> service = serviceRepo.findByTenantId(requestDTO.serviceId(),
          requestDTO.tenantId());
      if (service.isEmpty()) {
        return false;
      }
      scope = PermissionScope.SUBTENANT;
    } else {
      scope = (tenant.getName().equals("SYSTEM")) ? PermissionScope.SYSTEM : PermissionScope.TENANT;
    }

    return permissionExists(requestDTO.permissions(),
        userRepo.getPermission(user.getId(), tenant.getId(), scope));
  }


  private static boolean permissionExists(List<String> requestedPermission,
      List<String> definedPermissions) {
    return !Collections.disjoint(requestedPermission, definedPermissions);
  }
}
