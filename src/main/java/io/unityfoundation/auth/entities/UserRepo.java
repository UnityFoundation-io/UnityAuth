package io.unityfoundation.auth.entities;


import io.micronaut.data.annotation.Join;
import io.micronaut.data.jdbc.annotation.JdbcRepository;
import io.micronaut.data.model.query.builder.sql.Dialect;
import io.micronaut.data.repository.CrudRepository;
import java.util.Optional;

@JdbcRepository(dialect = Dialect.MYSQL)
public interface UserRepo extends CrudRepository<User, Long> {

  @Join(value = "tenants")
  Optional<User> findByEmail(String email);
}
