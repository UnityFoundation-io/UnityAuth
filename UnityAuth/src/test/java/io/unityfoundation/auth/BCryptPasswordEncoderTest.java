package io.unityfoundation.auth;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Unit tests for BCryptPasswordEncoder.
 * Tests password encoding and verification functionality.
 */
class BCryptPasswordEncoderTest {

    private BCryptPasswordEncoder encoder;

    @BeforeEach
    void setUp() {
        encoder = new BCryptPasswordEncoder();
    }

    @Test
    void encode_producesValidBCryptHash() {
        String rawPassword = "testPassword123";

        String encoded = encoder.encode(rawPassword);

        assertNotNull(encoded);
        assertTrue(encoded.startsWith("$2a$"), "Should produce BCrypt hash with $2a$ prefix");
        assertEquals(60, encoded.length(), "BCrypt hash should be 60 characters");
    }

    @Test
    void encode_producesUniqueHashesForSamePassword() {
        String rawPassword = "testPassword123";

        String encoded1 = encoder.encode(rawPassword);
        String encoded2 = encoder.encode(rawPassword);

        assertNotEquals(encoded1, encoded2, "Same password should produce different hashes due to salt");
    }

    @Test
    void matches_returnsTrueForCorrectPassword() {
        String rawPassword = "testPassword123";
        String encoded = encoder.encode(rawPassword);

        boolean matches = encoder.matches(rawPassword, encoded);

        assertTrue(matches, "Should match when raw password is correct");
    }

    @Test
    void matches_returnsFalseForIncorrectPassword() {
        String rawPassword = "testPassword123";
        String wrongPassword = "wrongPassword456";
        String encoded = encoder.encode(rawPassword);

        boolean matches = encoder.matches(wrongPassword, encoded);

        assertFalse(matches, "Should not match when raw password is incorrect");
    }

    @Test
    void matches_returnsFalseForEmptyPassword() {
        String rawPassword = "testPassword123";
        String encoded = encoder.encode(rawPassword);

        boolean matches = encoder.matches("", encoded);

        assertFalse(matches, "Should not match empty password");
    }

    @Test
    void matches_isCaseSensitive() {
        String rawPassword = "TestPassword123";
        String encoded = encoder.encode(rawPassword);

        assertFalse(encoder.matches("testpassword123", encoded), "Should be case sensitive");
        assertFalse(encoder.matches("TESTPASSWORD123", encoded), "Should be case sensitive");
        assertTrue(encoder.matches("TestPassword123", encoded), "Exact match should work");
    }

    @ParameterizedTest
    @ValueSource(strings = {"a", "short", "mediumPassword", "aVeryLongPasswordThatExceeds72Characters123456789012345678901234567890"})
    void encode_handlesVariousPasswordLengths(String password) {
        String encoded = encoder.encode(password);

        assertNotNull(encoded);
        assertTrue(encoder.matches(password, encoded), "Should match for password: " + password);
    }

    @Test
    void encode_handlesSpecialCharacters() {
        String specialPassword = "p@$$w0rd!#$%^&*()_+-=[]{}|;':\",./<>?";

        String encoded = encoder.encode(specialPassword);

        assertNotNull(encoded);
        assertTrue(encoder.matches(specialPassword, encoded), "Should handle special characters");
    }

    @Test
    void encode_handlesUnicodeCharacters() {
        String unicodePassword = "密码パスワード🔐";

        String encoded = encoder.encode(unicodePassword);

        assertNotNull(encoded);
        assertTrue(encoder.matches(unicodePassword, encoded), "Should handle unicode characters");
    }

    @Test
    void matches_handlesWhitespace() {
        String passwordWithSpaces = "password with spaces";
        String encoded = encoder.encode(passwordWithSpaces);

        assertTrue(encoder.matches(passwordWithSpaces, encoded));
        assertFalse(encoder.matches("passwordwithspaces", encoded), "Should preserve whitespace");
        assertFalse(encoder.matches(" password with spaces", encoded), "Should preserve leading whitespace");
    }

    @Test
    void matches_worksWithKnownBCryptHash() {
        // Pre-computed BCrypt hash for "test" (from test data in afterMigrate.sql)
        String knownHash = "$2a$10$YJetsyoS.EzlVlb249w07uBR8uSqgtlqVH9Hl7bsHtvvwdKAhJp82";

        assertTrue(encoder.matches("test", knownHash), "Should verify against known hash from test data");
        assertFalse(encoder.matches("wrong", knownHash), "Should not verify incorrect password against known hash");
    }
}
