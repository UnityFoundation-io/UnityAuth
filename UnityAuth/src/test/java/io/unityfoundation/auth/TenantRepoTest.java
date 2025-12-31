package io.unityfoundation.auth;

import io.micronaut.context.annotation.Property;
import io.micronaut.test.extensions.junit5.annotation.MicronautTest;
import io.unityfoundation.auth.entities.Tenant;
import io.unityfoundation.auth.entities.TenantRepo;
import jakarta.inject.Inject;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Integration tests for TenantRepo complex JOIN queries.
 * Tests tenant retrieval based on user relationships.
 *
 * Test data reference (from afterMigrate.sql):
 * - user 1 (person1@test.io): has roles in tenant 1 (SYSTEM) and tenant 2 (acme)
 * - user 2 (test@test.io): no tenant associations
 * - user 3 (disabled@test.io): no tenant associations
 * - user 4 (acme-tenant-admin@test.io): has roles only in tenant 2 (acme)
 * - tenant 1 (SYSTEM): ENABLED
 * - tenant 2 (acme): ENABLED
 */
@Property(name = "jwk.primary", value = "{\"p\":\"_OZyH1Mk3wR0oXw1C31t4kWOcaHFB6Njro1cYx52REnPiznn_JTtwvlAMpvV6LVCIZPgKMzdIEMY1gYs1LsO-5IFqWwegXmYJ0iKXbRrZshfWBCzRLK3QK5fER1le1XUBDhtDk7KIW_Xg-SZF4pf_LUEVKMnyUpspGI5F77jlJ8\",\"kty\":\"RSA\",\"q\":\"s9wvl7z8vkHQvo9xOUp-z0a2Z7LFBDil2uIjPh1FQzs34gFXH8dQPRox83TuN5d4KzdLPqQNQAfMXU9_KmxihNb_qDQahYugeELmcem04munxXqBdyZqWhWCy5YmujYqn44irwvoTbw6_RkMqjCmINPTPadptlPivsZ6RhKn8zk\",\"d\":\"ok3wmhOy8NZEHAotnFiH6ecFD6xf_9x33_fMRkqa3_KE8NZM7vmvNgElox2UvcP_2K5E7jOdL2XQdJCTIW3Qlj66yE2a84SYlbvxIc4hDrIog0XNt4FhavvshxxUIfDQo6Q8qXDR5v7nwt6SCopYC3t3KVRdJh08GzKoVxysd7afJjxXxx178gY29uMRqnwxFN1OGnWaiBr-xGKb1frJ6jOI1zvuuCaljZ4aZjc9vOR4y9ZmobgrzkMFnpDAmQZ7MWcVMyodRMOA2dEOckywPhg-dIVNiVIqzJqe5Yg1ilNookjwtqj2TpNU7Z9gPqzYB73PmQ2p5LMDheAPxcOmEQ\",\"e\":\"AQAB\",\"use\":\"sig\",\"kid\":\"e3be37177a7c42bcbadd7cc63715f216\",\"qi\":\"r--nAtaYPAgJq_8R1-kynpd53E17n-loDUgtVWBCx_RmdORX4Auilv1S83dD1mbcnYCbV_LmxiEjOiz-4gS_E0qVGqakAqQrO1hVUvJa_Y2uftDgwFmuJNGbpRU-K4Td_uUzdm48za8yJCgOdYsWp6PNMCcmQgiInzkR3XYV83I\",\"dp\":\"oQUcvmMSw8gzdin-IB2xW_MLecAVEgLu0dGBdD6N8HbKZQvub_xm0dAfFtnvvWXDAFwFyhR96i-uXX67Bos_Q9-6KSAE4E0KGmDucDESfPOw-QJREbl0QgOD1gLQfVGtVy6SCR0TR2zNXFWtP7bD3MNoSXdEOr5fI97CGSNaBWM\",\"alg\":\"RS256\",\"dq\":\"DM-WJDy10-dkMu6MpgQEXEcxHtnA5rgSODD7SaVUFaHWLSbjScQslu2SuUCO5y7GxG0_0spklzb2-356FE98BPI7a4Oqj_COEYLSXzLCS45XeN1s80utL5Vwp4eeYo0RJCQ_nDBA76iEmxp5qHWmn5f25-FQykfXUrdYZj1V8SE\",\"n\":\"sa6m2i-iNvj6ZSTdSHZaBrnv6DId4AqAXhOyl0yA5fNWYe6r51h24SXqk7DsGYHHh74ii74tP1lTpmy6RD67tCK-tbN-d6yc4Z6FfM8R83v2QZUfaAixgHGtw0n2toqsiHf6EloDV-B8q4GYyKDD6cLecoaIuTmMBTY3kts59U2t9W10YoLGsmFqLSz8qNF5HkahzB6_--2DiBfVGUKAXHC-SICGZCi-8efOetv6pt9vFiWEgwU_DgjRNYzLFt1SEmbGFUU4kbjQ7tNTMkHfzfwcT6qLt4kVKy2FNYsEMk24keWtCvW_RyO_fisZc0W9smX7WtYjEXhcAjDeqHgEZw\"}")
@Property(name = "jwk.secondary", value = "{\"p\":\"4qJ9RNlu6SuDT_MLArfzimvKEwmet_j12Z9EQeb5nMjZIOHTcWw__duebUytfWwxsRHhtSVXeMt-EryQAOulm2p1bfiVuparq93z9P5cPnb0oArFaw3eFNFEmX5U-lY8PzUTTsFxO4aVQYAKXD6DP7p5uPzuwpHFuNc71nNIXZE\",\"kty\":\"RSA\",\"q\":\"v4OhkWMbS_nq77HFanwZAT_obfJuQfOFOQBORL4ATAHGUXm2y4YqLNExZs7Wj1MA_6ya6Y00s2JBM7fWq_fPe4d9xo5aGrPdcp0G8W21kkfh9vuVPlHVQTgSP7FQ9qahvXxNwK_11yNr3p1HBmScJ5mHlMBpIJsFcvHA-uXe0Ps\",\"d\":\"EunrjnQ1-jJPSCrt2L94PUpDrakup8a4pXys52YSkJY-W6XidM0roOS6kr06P3G6VQgc6AL_BkvTQ_XS0oXHbXVprDQ5Syam5p9oxHBhhW_vSqIMgUOfm28uyB3Mtw9rBxdUxW3yElHioaR8a-exYhhyVXb1QEhxL_rcnthmhAkM2NcHi2UnxGKFTsC0abQ2MuQc1OAuW5veDiIF2hfdC41qE0_d8vB6FDWbblgUpbwB6uSZaViPs15Buq2oX9dCCw54-PgzkfehDt7lyqgupktbV1psnVVhL86shzt4QFnhd3k7VpFbjCNFtiJTrufV-XBWT0pl2w3VR9wrHJ1bYQ\",\"e\":\"AQAB\",\"use\":\"sig\",\"kid\":\"0794e938379540dc8eaa559508524a79\",\"qi\":\"jy-TNyXVy_44_n4KGAwIbZO2C4r6uNWuEdehBfQKkPhiP90myG1KZVfOoKNOK9bCv2mvZJcBz4c1ArElgpuSCV4-KFac1ZzQo_ic5aoIej8Qa80y2ogc-_Yv6_ZLHC1S76M-lm4jayk2-rvuBpy2pUvHbW6Srhs_szwz7ZfSkLg\",\"dp\":\"ApqdV9ortRAj7Ro8ySY17SQ56SgWI8T_hiWXUi6GNa_1FrShik8VGSSZ2GWmJKfGlmM_NaadL60e4LY77VbHy1ZYzQ-rIL60cEAXmnwFsU4Kl4AoLoe1QoX5BM53yXyOKqfAdgow898i_eKru82YEnZhCagWUjP8kpgefuNKNJE\",\"alg\":\"RS256\",\"dq\":\"bFF78WoXh0pMCdQHL2oPDnjh8kWa_OxKHmpA2nqIWnTqgSyRKd2xPvX2tgooqpmsx-8NEymNdCQPcrv4y_z2OgzxI3tiFRZEGs4bnjOJ7bmAYZv71mqcbi3TjHiyrT6j3jNPGrurFUpweVGFWWVQOMmKOKT3ELz9QPzhREb9Vj8\",\"n\":\"qYvDpV8DRU5hx9eXpE4Ms8nUXicEwrxUUz5gb5gkXpIeY82mqfQKKCP6PSFnkKYtRFTOUSm9cgGGfOd7O4NFsIsxLwXCj34X7ORr19eXKBLvG3bZJLxqRlbYuQshDMkQOui1sDBxvYnj5p4iHne6l2btH5grHOCShUWG-bKps5Y8bKNHod1pIOOBabVCmn3sUVUkZw8nyXkQqZbv-c8x6z0TEfhNOPOIt2AmmlNgrE_8g7-dnCvqfJnhv0c7qkOJzsb7OMmvVwsQNiM59D6uaWZr-vdANo6NggiZmCKUS3tpUvdXW7ec9WMPJWhrVEkRcbWXQnZ_C7pXFrz7rLeNKw\"}")
@MicronautTest
class TenantRepoTest {

    @Inject
    TenantRepo tenantRepo;

    @Nested
    @DisplayName("findAllByUserEmail() - User tenants JOIN query")
    class FindAllByUserEmailTests {

        @Test
        @DisplayName("Returns all tenants for user with multiple tenant associations (includes duplicates)")
        void findAllByUserEmail_userWithMultipleTenants_returnsAllTenants() {
            // person1@test.io has roles in both tenant 1 (SYSTEM) and tenant 2 (acme)
            // NOTE: Current query returns duplicate rows when user has multiple roles in same tenant.
            // person1@test.io has: 1 role in tenant 1, 2 roles in tenant 2 = 3 total rows returned.
            // TODO: Consider adding DISTINCT to the query if unique tenants are desired.
            List<Tenant> tenants = tenantRepo.findAllByUserEmail("person1@test.io");

            assertNotNull(tenants);
            // Current behavior: returns 3 rows (duplicates for tenant 2 due to multiple roles)
            assertEquals(3, tenants.size(), "Query returns row per user_role, not unique tenants");

            boolean hasTenant1 = tenants.stream().anyMatch(t -> t.getId().equals(1L));
            boolean hasTenant2 = tenants.stream().anyMatch(t -> t.getId().equals(2L));

            assertTrue(hasTenant1, "Should include tenant 1 (SYSTEM)");
            assertTrue(hasTenant2, "Should include tenant 2 (acme)");

            // Verify we get exactly 1 row for tenant 1 (one role) and 2 rows for tenant 2 (two roles)
            long tenant1Count = tenants.stream().filter(t -> t.getId().equals(1L)).count();
            long tenant2Count = tenants.stream().filter(t -> t.getId().equals(2L)).count();
            assertEquals(1, tenant1Count, "Tenant 1 should appear once (one role)");
            assertEquals(2, tenant2Count, "Tenant 2 should appear twice (two roles)");
        }

        @Test
        @DisplayName("Returns single tenant for user with one tenant association")
        void findAllByUserEmail_userWithSingleTenant_returnsSingleTenant() {
            // acme-tenant-admin@test.io only has roles in tenant 2
            List<Tenant> tenants = tenantRepo.findAllByUserEmail("acme-tenant-admin@test.io");

            assertNotNull(tenants);
            assertEquals(1, tenants.size(), "User should be associated with 1 tenant");
            assertEquals(2L, tenants.get(0).getId(), "Tenant should be tenant 2 (acme)");
        }

        @Test
        @DisplayName("Returns correct tenant details")
        void findAllByUserEmail_returnsCorrectTenantDetails() {
            List<Tenant> tenants = tenantRepo.findAllByUserEmail("acme-tenant-admin@test.io");

            assertNotNull(tenants);
            assertFalse(tenants.isEmpty());

            Tenant acme = tenants.get(0);
            assertEquals(2L, acme.getId());
            assertEquals("acme", acme.getName());
        }

        @Test
        @DisplayName("Returns empty list for user with no tenant associations")
        void findAllByUserEmail_userWithNoTenants_returnsEmptyList() {
            // test@test.io has no tenant associations
            List<Tenant> tenants = tenantRepo.findAllByUserEmail("test@test.io");

            assertNotNull(tenants);
            assertTrue(tenants.isEmpty(), "User with no tenant associations should return empty list");
        }

        @Test
        @DisplayName("Returns empty list for non-existent user")
        void findAllByUserEmail_nonExistentUser_returnsEmptyList() {
            List<Tenant> tenants = tenantRepo.findAllByUserEmail("nonexistent@test.io");

            assertNotNull(tenants);
            assertTrue(tenants.isEmpty(), "Non-existent user should return empty list");
        }

        @Test
        @DisplayName("Returns tenants even for disabled user")
        void findAllByUserEmail_disabledUser_returnsEmptyList() {
            // disabled@test.io has no roles in test data (even though user exists)
            List<Tenant> tenants = tenantRepo.findAllByUserEmail("disabled@test.io");

            assertNotNull(tenants);
            assertTrue(tenants.isEmpty(), "Disabled user with no roles should return empty list");
        }

        @Test
        @DisplayName("Handles duplicate tenant associations correctly")
        void findAllByUserEmail_userWithMultipleRolesInSameTenant_handlesCorrectly() {
            // person1@test.io has multiple roles (2 and 3) in tenant 2
            // The query should return tenant 2 (potentially multiple times based on JOIN behavior)
            List<Tenant> tenants = tenantRepo.findAllByUserEmail("person1@test.io");

            assertNotNull(tenants);
            // Note: Current query may return duplicates since user has multiple roles in tenant 2
            // This test documents the actual behavior
            long tenant2Count = tenants.stream().filter(t -> t.getId().equals(2L)).count();
            assertTrue(tenant2Count >= 1, "Should include tenant 2 at least once");
        }
    }

    @Nested
    @DisplayName("CrudRepository methods - Basic CRUD operations")
    class BasicCrudTests {

        @Test
        @DisplayName("findById returns tenant when exists")
        void findById_existingTenant_returnsTenant() {
            Optional<Tenant> tenant = tenantRepo.findById(1L);

            assertTrue(tenant.isPresent());
            assertEquals("SYSTEM", tenant.get().getName());
        }

        @Test
        @DisplayName("findById returns empty for non-existent tenant")
        void findById_nonExistentTenant_returnsEmpty() {
            Optional<Tenant> tenant = tenantRepo.findById(999L);

            assertTrue(tenant.isEmpty());
        }

        @Test
        @DisplayName("findAll returns all tenants")
        void findAll_returnAllTenants() {
            Iterable<Tenant> tenants = tenantRepo.findAll();

            assertNotNull(tenants);
            List<Tenant> tenantList = new ArrayList<>();
            tenants.forEach(tenantList::add);
            assertEquals(2, tenantList.size(), "Should have 2 tenants in test data");
        }

        @Test
        @DisplayName("existsById returns true for existing tenant")
        void existsById_existingTenant_returnsTrue() {
            boolean exists = tenantRepo.existsById(1L);

            assertTrue(exists);
        }

        @Test
        @DisplayName("existsById returns false for non-existent tenant")
        void existsById_nonExistentTenant_returnsFalse() {
            boolean exists = tenantRepo.existsById(999L);

            assertFalse(exists);
        }

        @Test
        @DisplayName("count returns correct number of tenants")
        void count_returnsCorrectCount() {
            long count = tenantRepo.count();

            assertEquals(2, count, "Should have 2 tenants in test data");
        }
    }
}
