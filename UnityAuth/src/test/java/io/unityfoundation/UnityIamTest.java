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
import io.unityfoundation.auth.AuthController.HasPermissionResponse;
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
  void testUserDisabled() {
    String accessToken = login("disabled@test.io");
    HttpRequest<?> hasPermissionRequest = HttpRequest.POST("/api/hasPermission", new HasPermissionRequest("SYSTEM", "Libre311", List.of("AUTH_SERVICE_EDIT-SYSTEM")))
        .bearerAuth(accessToken);
    HttpResponse<HasPermissionResponse> response = client.toBlocking()
        .exchange(hasPermissionRequest, HasPermissionResponse.class);
    assertEquals("The user’s account has been disabled!", response.getBody().get().errorMessage());
    assertEquals(Boolean.FALSE, response.getBody().get().hasPermission());
  }

  @Test
  void testHasSystemPermission() {
    String accessToken = login("person1@test.io");
    HttpRequest<?> hasPermissionRequest = HttpRequest.POST("/api/hasPermission", new HasPermissionRequest("SYSTEM", "Libre311", List.of("AUTH_SERVICE_EDIT-SYSTEM")))
        .bearerAuth(accessToken);
    HttpResponse<HasPermissionResponse> response = client.toBlocking()
        .exchange(hasPermissionRequest, HasPermissionResponse.class);
    assertEquals(Boolean.TRUE, response.getBody().get().hasPermission());
  }

  @Test
  void testHasNoSystemPermission() {
    String accessToken = login("test@test.io");
    HttpRequest<?> hasPermissionRequest = HttpRequest.POST("/api/hasPermission", new HasPermissionRequest("SYSTEM", "Libre311", List.of("AUTH_SERVICE_EDIT-SYSTEM")))
        .bearerAuth(accessToken);
    HttpResponse<HasPermissionResponse> response = client.toBlocking()
        .exchange(hasPermissionRequest, HasPermissionResponse.class);
    assertEquals("The requested service is not enabled for the requested tenant!", response.getBody().get().errorMessage());
    assertEquals(Boolean.FALSE, response.getBody().get().hasPermission());
  }

  @Test
  void testHasTenantPermission() {
    String accessToken = login("person1@test.io");
    HttpRequest<?> hasPermissionRequest = HttpRequest.POST("/api/hasPermission", new HasPermissionRequest("acme", "Libre311", List.of("LIBRE311_REQUEST_EDIT-TENANT")))
        .bearerAuth(accessToken);
    HttpResponse<HasPermissionResponse> response = client.toBlocking()
        .exchange(hasPermissionRequest, HasPermissionResponse.class);
    assertEquals(Boolean.TRUE, response.getBody().get().hasPermission());
  }

  @Test
  void testHasNoTenantPermission() {
    String accessToken = login("person1@test.io");
    HttpRequest<?> hasPermissionRequest = HttpRequest.POST("/api/hasPermission", new HasPermissionRequest("acme", "Libre311", List.of("LIBRE311_REQUEST_VIEW-TENANT")))
        .bearerAuth(accessToken);
    HttpResponse<HasPermissionResponse> response = client.toBlocking()
        .exchange(hasPermissionRequest, HasPermissionResponse.class);
    assertEquals("The user does not have permission!", response.getBody().get().errorMessage());
    assertEquals(Boolean.FALSE, response.getBody().get().hasPermission());
  }

  @Test
  void testHasSubtenantPermission() {
    String accessToken = login("person1@test.io");
    HttpRequest<?> hasPermissionRequest = HttpRequest.POST("/api/hasPermission", new HasPermissionRequest("acme", "Libre311", List.of("LIBRE311_REQUEST_EDIT-SUBTENANT")))
        .bearerAuth(accessToken);
    HttpResponse<HasPermissionResponse> response = client.toBlocking()
        .exchange(hasPermissionRequest, HasPermissionResponse.class);
    assertEquals(Boolean.TRUE, response.getBody().get().hasPermission());
  }

  @Test
  void testHasNoSubtenantPermission() {
    String accessToken = login("person1@test.io");
    HttpRequest<?> hasPermissionRequest = HttpRequest.POST("/api/hasPermission", new HasPermissionRequest("acme", "Application2", List.of("LIBRE311_REQUEST_EDIT-SUBTENANT")))
        .bearerAuth(accessToken);
    HttpResponse<HasPermissionResponse> response = client.toBlocking()
        .exchange(hasPermissionRequest, HasPermissionResponse.class);
    assertEquals(Boolean.FALSE, response.getBody().get().hasPermission());
    assertEquals("The requested service is not enabled for the requested tenant!", response.getBody().get().errorMessage());
  }

  private String login(String username) {
    UsernamePasswordCredentials creds = new UsernamePasswordCredentials(username, "test");
    HttpRequest<?> request = HttpRequest.POST("/api/login", creds);
    HttpResponse<BearerAccessRefreshToken> rsp = client.toBlocking()
        .exchange(request, BearerAccessRefreshToken.class);
    assertEquals(HttpStatus.OK, rsp.getStatus());
    BearerAccessRefreshToken bearer = rsp.body();
    return bearer.getAccessToken();
  }



}

