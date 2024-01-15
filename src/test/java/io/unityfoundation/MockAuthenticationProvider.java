package io.unityfoundation;

import io.micronaut.core.annotation.Nullable;
import io.micronaut.http.HttpRequest;
import io.micronaut.security.authentication.AuthenticationProvider;
import io.micronaut.security.authentication.AuthenticationRequest;
import io.micronaut.security.authentication.AuthenticationResponse;
import jakarta.inject.Singleton;
import org.reactivestreams.Publisher;
import reactor.core.publisher.Flux;
import reactor.core.publisher.FluxSink;

@Singleton
public class MockAuthenticationProvider implements AuthenticationProvider<HttpRequest<?>> {

  @Override
  public Publisher<AuthenticationResponse> authenticate(@Nullable HttpRequest<?> httpRequest,
      AuthenticationRequest<?, ?> authenticationRequest) {
    return Flux.create(emitter -> {
      if (authenticationRequest.getIdentity().equals("wilsonj@unityfoundation.io") &&
          authenticationRequest.getSecret().equals("test")) {
        emitter.next(AuthenticationResponse.success((String) authenticationRequest.getIdentity()));
        emitter.complete();
      } else {
        emitter.error(AuthenticationResponse.exception());
      }
    }, FluxSink.OverflowStrategy.ERROR);
  }
}

