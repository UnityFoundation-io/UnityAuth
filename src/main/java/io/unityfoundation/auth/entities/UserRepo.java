package io.unityfoundation.auth.entities;


import io.micronaut.data.annotation.Join;
import io.micronaut.data.annotation.Query;
import io.micronaut.data.jdbc.annotation.JdbcRepository;
import io.micronaut.data.model.query.builder.sql.Dialect;
import io.micronaut.data.repository.CrudRepository;
import io.unityfoundation.auth.entities.Permission.PermissionScope;
import java.util.List;
import java.util.Optional;

@JdbcRepository(dialect = Dialect.MYSQL)
public interface UserRepo extends CrudRepository<User, Long> {

  @Join(value = "tenants")
  Optional<User> findByEmail(String email);

  @Query("""
      select p.name
from user_role ur
         inner join role_permission rp on rp.role_id = ur.role_id
         inner join permission p on p.id = rp.permission_id
where ur.tenant_id = :tenantId
  and ur.user_id = :userId
  and p.scope = :permissionScope
""")
  List<String> getPermission(Long userId, Long tenantId, PermissionScope permissionScope);
}
