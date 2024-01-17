package io.unityfoundation.auth.entities;


import io.micronaut.data.annotation.GeneratedValue;
import io.micronaut.data.annotation.Id;
import io.micronaut.data.annotation.MappedEntity;
import io.micronaut.data.annotation.Relation;
import io.micronaut.data.annotation.sql.JoinColumn;
import io.micronaut.data.annotation.sql.JoinTable;
import jakarta.validation.constraints.NotNull;
import java.util.Set;

@MappedEntity
public class User {
  @Id
  @GeneratedValue
  private Long id;

  @NotNull
  private String email;

  private UserStatus status;

  private String password;

  @Relation(Relation.Kind.MANY_TO_MANY)
  @JoinTable(
      name = "user_role",
      joinColumns = @JoinColumn(name = "user_id"),
      inverseJoinColumns = @JoinColumn(name = "tenant_id"))
  private Set<Tenant> tenants;

  public Set<Tenant> getTenants() {
    return tenants;
  }

  public void setTenants(Set<Tenant> tenants) {
    this.tenants = tenants;
  }

  public String getPassword() {
    return password;
  }

  public void setPassword(String password) {
    this.password = password;
  }

  public enum UserStatus {
    ENABLED, DISABLED
  }

  public Long getId() {
    return id;
  }

  public void setId(Long id) {
    this.id = id;
  }

  public String getEmail() {
    return email;
  }

  public void setEmail(String email) {
    this.email = email;
  }

  public UserStatus getStatus() {
    return status;
  }

  public void setStatus(UserStatus status) {
    this.status = status;
  }
}
