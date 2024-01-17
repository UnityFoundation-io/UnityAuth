package io.unityfoundation;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.micronaut.http.HttpRequest;
import io.micronaut.http.HttpResponse;
import io.micronaut.http.HttpStatus;
import io.micronaut.http.client.HttpClient;
import io.micronaut.http.client.annotation.Client;
import io.micronaut.security.authentication.UsernamePasswordCredentials;
import io.micronaut.security.token.render.BearerAccessRefreshToken;
import io.micronaut.test.extensions.junit5.annotation.MicronautTest;
import io.unityfoundation.auth.HasPermissionRequest;
import jakarta.inject.Inject;
import java.util.List;
import org.junit.jupiter.api.Test;

@MicronautTest
class UnityIamTest {

  @Inject
  @Client("/")
  HttpClient client;

  @Test
  void testHasSystemPermission() {
    String accessToken = login("person1@test.io");
    HttpRequest<?> hasPermissionRequest = HttpRequest.POST("/api/hasPermission", new HasPermissionRequest(1L, null, List.of("AUTH_SERVICE_EDIT-SYSTEM")))
        .bearerAuth(accessToken);
    HttpResponse<Boolean> response = client.toBlocking()
        .exchange(hasPermissionRequest, Boolean.class);
    assertEquals(HttpStatus.OK, response.getStatus());
    assertEquals(Boolean.TRUE, response.getBody().get());
  }

  @Test
  void testHasNoSystemPermission() {
    String accessToken = login("test@test.io");
    HttpRequest<?> hasPermissionRequest = HttpRequest.POST("/api/hasPermission", new HasPermissionRequest(1L, null, List.of("AUTH_SERVICE_EDIT-SYSTEM")))
        .bearerAuth(accessToken);
    HttpResponse<Boolean> response = client.toBlocking()
        .exchange(hasPermissionRequest, Boolean.class);
    assertEquals(HttpStatus.OK, response.getStatus());
    assertEquals(Boolean.FALSE, response.getBody().get());
  }

  @Test
  void testHasTenantPermission() {
    String accessToken = login("person1@test.io");
    HttpRequest<?> hasPermissionRequest = HttpRequest.POST("/api/hasPermission", new HasPermissionRequest(2L, null, List.of("LIBRE311_REQUEST_EDIT-TENANT")))
        .bearerAuth(accessToken);
    HttpResponse<Boolean> response = client.toBlocking()
        .exchange(hasPermissionRequest, Boolean.class);
    assertEquals(HttpStatus.OK, response.getStatus());
    assertEquals(Boolean.TRUE, response.getBody().get());
  }

  @Test
  void testHasNoTenantPermission() {
    String accessToken = login("person1@test.io");
    HttpRequest<?> hasPermissionRequest = HttpRequest.POST("/api/hasPermission", new HasPermissionRequest(2L, 1L, List.of("LIBRE311_REQUEST_VIEW-TENANT")))
        .bearerAuth(accessToken);
    HttpResponse<Boolean> response = client.toBlocking()
        .exchange(hasPermissionRequest, Boolean.class);
    assertEquals(HttpStatus.OK, response.getStatus());
    assertEquals(Boolean.FALSE, response.getBody().get());
  }

  @Test
  void testHasSubtenantPermission() {
    String accessToken = login("person1@test.io");
    HttpRequest<?> hasPermissionRequest = HttpRequest.POST("/api/hasPermission?subtenant=true", new HasPermissionRequest(2L, 1L, List.of("LIBRE311_REQUEST_EDIT-SUBTENANT")))
        .bearerAuth(accessToken);
    HttpResponse<Boolean> response = client.toBlocking()
        .exchange(hasPermissionRequest, Boolean.class);
    assertEquals(HttpStatus.OK, response.getStatus());
    assertEquals(Boolean.TRUE, response.getBody().get());
  }

  @Test
  void testHasNoSubtenantPermission() {
    String accessToken = login("person1@test.io");
    HttpRequest<?> hasPermissionRequest = HttpRequest.POST("/api/hasPermission?subtenant=true", new HasPermissionRequest(2L, 2L, List.of("LIBRE311_REQUEST_EDIT-SUBTENANT")))
        .bearerAuth(accessToken);
    HttpResponse<Boolean> response = client.toBlocking()
        .exchange(hasPermissionRequest, Boolean.class);
    assertEquals(HttpStatus.OK, response.getStatus());
    assertEquals(Boolean.FALSE, response.getBody().get());
  }

  @Test
  void testHasNoSubtenantFlag() {
    String accessToken = login("person1@test.io");
    HttpRequest<?> hasPermissionRequest = HttpRequest.POST("/api/hasPermission", new HasPermissionRequest(2L, 1L, List.of("LIBRE311_REQUEST_EDIT-SUBTENANT")))
        .bearerAuth(accessToken);
    HttpResponse<Boolean> response = client.toBlocking()
        .exchange(hasPermissionRequest, Boolean.class);
    assertEquals(HttpStatus.OK, response.getStatus());
    assertEquals(Boolean.FALSE, response.getBody().get());
  }

  private String login(String username) {
    UsernamePasswordCredentials creds = new UsernamePasswordCredentials(username, "test");
    HttpRequest<?> request = HttpRequest.POST("/login", creds);
    HttpResponse<BearerAccessRefreshToken> rsp = client.toBlocking()
        .exchange(request, BearerAccessRefreshToken.class);
    assertEquals(HttpStatus.OK, rsp.getStatus());
    BearerAccessRefreshToken bearer = rsp.body();
    String accessToken = bearer.getAccessToken();
    return accessToken;
  }



}

