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
  void testHasPermission() {
    UsernamePasswordCredentials creds = new UsernamePasswordCredentials("wilsonj@unityfoundation.io", "test");
    HttpRequest<?> request = HttpRequest.POST("/login", creds);
    HttpResponse<BearerAccessRefreshToken> rsp = client.toBlocking()
        .exchange(request, BearerAccessRefreshToken.class);
    assertEquals(HttpStatus.OK, rsp.getStatus());
    BearerAccessRefreshToken bearer = rsp.body();
    String accessToken = bearer.getAccessToken();
    HttpRequest<?> hasPermissionRequest = HttpRequest.POST("/api/hasPermission/1/1", new HasPermissionRequest(1L, 1L, List.of("LIBRE311_REQUEST_EDIT-TENANT")))
        .bearerAuth(accessToken);
    HttpResponse<Boolean> response = client.toBlocking()
        .exchange(hasPermissionRequest, Boolean.class);
    assertEquals(HttpStatus.OK, response.getStatus());
    assertEquals(Boolean.TRUE, response.getBody().get());


/*
    BearerAccessRefreshToken bearerAccessRefreshToken = rsp.body();
    assertEquals("sherlock", bearerAccessRefreshToken.getUsername());
    assertNotNull(bearerAccessRefreshToken.getAccessToken());
    assertTrue(JWTParser.parse(bearerAccessRefreshToken.getAccessToken()) instanceof SignedJWT);

    String accessToken = bearerAccessRefreshToken.getAccessToken();
    HttpRequest<?> requestWithAuthorization = HttpRequest.GET("/")
        .accept(TEXT_PLAIN)
        .bearerAuth(accessToken);
    HttpResponse<String> response = client.toBlocking()
        .exchange(requestWithAuthorization, String.class);

    assertEquals(OK, rsp.getStatus());
    assertEquals("sherlock", response.body());
*/
  }

}

