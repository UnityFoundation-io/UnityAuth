package io.unityfoundation.auth;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Unit tests for NullOrNotBlankValidator.
 * Tests the custom validation constraint that allows null but rejects blank strings.
 */
class NullOrNotBlankValidatorTest {

    private NullOrNotBlankValidator validator;

    @BeforeEach
    void setUp() {
        validator = new NullOrNotBlankValidator();
    }

    @Test
    void isValid_returnsTrueForNull() {
        boolean result = validator.isValid(null, null);

        assertTrue(result, "Null should be valid");
    }

    @ParameterizedTest
    @ValueSource(strings = {"a", "valid", "valid value", "  valid with leading spaces", "valid with trailing spaces  "})
    void isValid_returnsTrueForNonBlankStrings(String value) {
        boolean result = validator.isValid(value, null);

        assertTrue(result, "Non-blank string should be valid: '" + value + "'");
    }

    @Test
    void isValid_returnsFalseForEmptyString() {
        boolean result = validator.isValid("", null);

        assertFalse(result, "Empty string should be invalid");
    }

    @ParameterizedTest
    @ValueSource(strings = {" ", "  ", "\t", "\n", "\r", "\t\n\r ", "   \t   "})
    void isValid_returnsFalseForWhitespaceOnlyStrings(String value) {
        boolean result = validator.isValid(value, null);

        assertFalse(result, "Whitespace-only string should be invalid: '" + value.replace("\t", "\\t").replace("\n", "\\n").replace("\r", "\\r") + "'");
    }

    @Test
    void isValid_returnsTrueForStringWithContent() {
        assertTrue(validator.isValid("x", null), "Single character should be valid");
        assertTrue(validator.isValid("hello world", null), "Normal string should be valid");
        assertTrue(validator.isValid("  hello  ", null), "String with content and surrounding whitespace should be valid");
    }

    @Test
    void isValid_returnsTrueForSpecialCharacters() {
        assertTrue(validator.isValid("!@#$%^&*()", null), "Special characters should be valid");
        assertTrue(validator.isValid("123", null), "Numbers should be valid");
        assertTrue(validator.isValid("日本語", null), "Unicode characters should be valid");
    }
}
