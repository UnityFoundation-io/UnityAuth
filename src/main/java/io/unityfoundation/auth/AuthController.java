package io.unityfoundation.auth;

import io.micronaut.core.annotation.Nullable;
import io.micronaut.http.annotation.Body;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;
import io.micronaut.http.annotation.QueryValue;
import io.micronaut.security.annotation.Secured;
import io.micronaut.security.authentication.Authentication;
import io.micronaut.security.rules.SecurityRule;
import io.unityfoundation.auth.entities.Tenant;
import io.unityfoundation.auth.entities.Tenant.TenantStatus;
import io.unityfoundation.auth.entities.User;
import io.unityfoundation.auth.entities.UserRepo;
import java.util.Optional;

@Secured(SecurityRule.IS_AUTHENTICATED)
@Controller("/api")
public class AuthController {

  private final UserRepo userRepo;

  public AuthController(UserRepo userRepo) {
    this.userRepo = userRepo;
  }

  @Post("/hasPermission/{tenantId}/{serviceId}{?subtenant}")
  public boolean hasPermission(@Body HasPermissionRequest requestDTO, @Nullable @QueryValue("subtenant") Boolean subtenant, Authentication authentication) {
    User user = userRepo.findByEmail(authentication.getName()).orElseThrow(IllegalArgumentException::new);
    if (user.getStatus() == User.UserStatus.ENABLED) {
      Optional<Tenant> t = user.getTenants().stream()
          .filter(tenant -> requestDTO.tenantId().equals(tenant.getId()))
          .findFirst();
      if (t.isPresent() && TenantStatus.ACTIVE.equals(t.get().getStatus())) {

        return true;
      }
    }
    return false;
  }
}
