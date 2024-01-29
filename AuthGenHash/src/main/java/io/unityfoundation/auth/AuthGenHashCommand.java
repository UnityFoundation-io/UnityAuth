package io.unityfoundation.auth;

import io.micronaut.configuration.picocli.PicocliRunner;
import io.micronaut.context.ApplicationContext;

import jakarta.inject.Inject;
import picocli.CommandLine;
import picocli.CommandLine.Command;
import picocli.CommandLine.Option;
import picocli.CommandLine.Parameters;

@Command(name = "AuthGenHash", description = "This executable will generate a hashed password.",
        mixinStandardHelpOptions = true)
public class AuthGenHashCommand implements Runnable {

    @Inject
    BCryptPasswordEncoder bCryptPasswordEncoder;

    @Option(names = {"-v", "--verbose"}, description = "...")
    boolean verbose;

    @Option(names = {"-p", "--password"}, description = "Passphrase", interactive = true, required = true)
    String password;

    public static void main(String[] args) throws Exception {
        PicocliRunner.run(AuthGenHashCommand.class, args);
    }

    public void run() {
        System.out.println(bCryptPasswordEncoder.encode(password));
    }
}
