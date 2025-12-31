package io.unityfoundation.auth;

import io.micronaut.context.annotation.Property;
import io.micronaut.test.extensions.junit5.annotation.MicronautTest;
import io.unityfoundation.auth.entities.Permission;
import io.unityfoundation.auth.entities.User;
import io.unityfoundation.auth.entities.UserRepo;
import jakarta.inject.Inject;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Integration tests for UserRepo complex JOIN queries.
 * Tests the permission aggregation, tenant relationship, and role verification queries.
 *
 * Test data reference (from afterMigrate.sql):
 * - user 1 (person1@test.io): Unity Admin (role 1) in tenant 1, Tenant role (role 2) and Subtenant role (role 3) in tenant 2
 * - user 2 (test@test.io): No roles
 * - user 3 (disabled@test.io): DISABLED status, no roles
 * - user 4 (acme-tenant-admin@test.io): Tenant role (role 2) in tenant 2
 * - tenant 1 (SYSTEM): ENABLED
 * - tenant 2 (acme): ENABLED, has service 1 (Libre311)
 * - service 1 (Libre311): ENABLED
 * - service 2 (Application2): ENABLED (not linked to any tenant)
 */
@Property(name = "jwk.primary", value = "{\"p\":\"_OZyH1Mk3wR0oXw1C31t4kWOcaHFB6Njro1cYx52REnPiznn_JTtwvlAMpvV6LVCIZPgKMzdIEMY1gYs1LsO-5IFqWwegXmYJ0iKXbRrZshfWBCzRLK3QK5fER1le1XUBDhtDk7KIW_Xg-SZF4pf_LUEVKMnyUpspGI5F77jlJ8\",\"kty\":\"RSA\",\"q\":\"s9wvl7z8vkHQvo9xOUp-z0a2Z7LFBDil2uIjPh1FQzs34gFXH8dQPRox83TuN5d4KzdLPqQNQAfMXU9_KmxihNb_qDQahYugeELmcem04munxXqBdyZqWhWCy5YmujYqn44irwvoTbw6_RkMqjCmINPTPadptlPivsZ6RhKn8zk\",\"d\":\"ok3wmhOy8NZEHAotnFiH6ecFD6xf_9x33_fMRkqa3_KE8NZM7vmvNgElox2UvcP_2K5E7jOdL2XQdJCTIW3Qlj66yE2a84SYlbvxIc4hDrIog0XNt4FhavvshxxUIfDQo6Q8qXDR5v7nwt6SCopYC3t3KVRdJh08GzKoVxysd7afJjxXxx178gY29uMRqnwxFN1OGnWaiBr-xGKb1frJ6jOI1zvuuCaljZ4aZjc9vOR4y9ZmobgrzkMFnpDAmQZ7MWcVMyodRMOA2dEOckywPhg-dIVNiVIqzJqe5Yg1ilNookjwtqj2TpNU7Z9gPqzYB73PmQ2p5LMDheAPxcOmEQ\",\"e\":\"AQAB\",\"use\":\"sig\",\"kid\":\"e3be37177a7c42bcbadd7cc63715f216\",\"qi\":\"r--nAtaYPAgJq_8R1-kynpd53E17n-loDUgtVWBCx_RmdORX4Auilv1S83dD1mbcnYCbV_LmxiEjOiz-4gS_E0qVGqakAqQrO1hVUvJa_Y2uftDgwFmuJNGbpRU-K4Td_uUzdm48za8yJCgOdYsWp6PNMCcmQgiInzkR3XYV83I\",\"dp\":\"oQUcvmMSw8gzdin-IB2xW_MLecAVEgLu0dGBdD6N8HbKZQvub_xm0dAfFtnvvWXDAFwFyhR96i-uXX67Bos_Q9-6KSAE4E0KGmDucDESfPOw-QJREbl0QgOD1gLQfVGtVy6SCR0TR2zNXFWtP7bD3MNoSXdEOr5fI97CGSNaBWM\",\"alg\":\"RS256\",\"dq\":\"DM-WJDy10-dkMu6MpgQEXEcxHtnA5rgSODD7SaVUFaHWLSbjScQslu2SuUCO5y7GxG0_0spklzb2-356FE98BPI7a4Oqj_COEYLSXzLCS45XeN1s80utL5Vwp4eeYo0RJCQ_nDBA76iEmxp5qHWmn5f25-FQykfXUrdYZj1V8SE\",\"n\":\"sa6m2i-iNvj6ZSTdSHZaBrnv6DId4AqAXhOyl0yA5fNWYe6r51h24SXqk7DsGYHHh74ii74tP1lTpmy6RD67tCK-tbN-d6yc4Z6FfM8R83v2QZUfaAixgHGtw0n2toqsiHf6EloDV-B8q4GYyKDD6cLecoaIuTmMBTY3kts59U2t9W10YoLGsmFqLSz8qNF5HkahzB6_--2DiBfVGUKAXHC-SICGZCi-8efOetv6pt9vFiWEgwU_DgjRNYzLFt1SEmbGFUU4kbjQ7tNTMkHfzfwcT6qLt4kVKy2FNYsEMk24keWtCvW_RyO_fisZc0W9smX7WtYjEXhcAjDeqHgEZw\"}")
@Property(name = "jwk.secondary", value = "{\"p\":\"4qJ9RNlu6SuDT_MLArfzimvKEwmet_j12Z9EQeb5nMjZIOHTcWw__duebUytfWwxsRHhtSVXeMt-EryQAOulm2p1bfiVuparq93z9P5cPnb0oArFaw3eFNFEmX5U-lY8PzUTTsFxO4aVQYAKXD6DP7p5uPzuwpHFuNc71nNIXZE\",\"kty\":\"RSA\",\"q\":\"v4OhkWMbS_nq77HFanwZAT_obfJuQfOFOQBORL4ATAHGUXm2y4YqLNExZs7Wj1MA_6ya6Y00s2JBM7fWq_fPe4d9xo5aGrPdcp0G8W21kkfh9vuVPlHVQTgSP7FQ9qahvXxNwK_11yNr3p1HBmScJ5mHlMBpIJsFcvHA-uXe0Ps\",\"d\":\"EunrjnQ1-jJPSCrt2L94PUpDrakup8a4pXys52YSkJY-W6XidM0roOS6kr06P3G6VQgc6AL_BkvTQ_XS0oXHbXVprDQ5Syam5p9oxHBhhW_vSqIMgUOfm28uyB3Mtw9rBxdUxW3yElHioaR8a-exYhhyVXb1QEhxL_rcnthmhAkM2NcHi2UnxGKFTsC0abQ2MuQc1OAuW5veDiIF2hfdC41qE0_d8vB6FDWbblgUpbwB6uSZaViPs15Buq2oX9dCCw54-PgzkfehDt7lyqgupktbV1psnVVhL86shzt4QFnhd3k7VpFbjCNFtiJTrufV-XBWT0pl2w3VR9wrHJ1bYQ\",\"e\":\"AQAB\",\"use\":\"sig\",\"kid\":\"0794e938379540dc8eaa559508524a79\",\"qi\":\"jy-TNyXVy_44_n4KGAwIbZO2C4r6uNWuEdehBfQKkPhiP90myG1KZVfOoKNOK9bCv2mvZJcBz4c1ArElgpuSCV4-KFac1ZzQo_ic5aoIej8Qa80y2ogc-_Yv6_ZLHC1S76M-lm4jayk2-rvuBpy2pUvHbW6Srhs_szwz7ZfSkLg\",\"dp\":\"ApqdV9ortRAj7Ro8ySY17SQ56SgWI8T_hiWXUi6GNa_1FrShik8VGSSZ2GWmJKfGlmM_NaadL60e4LY77VbHy1ZYzQ-rIL60cEAXmnwFsU4Kl4AoLoe1QoX5BM53yXyOKqfAdgow898i_eKru82YEnZhCagWUjP8kpgefuNKNJE\",\"alg\":\"RS256\",\"dq\":\"bFF78WoXh0pMCdQHL2oPDnjh8kWa_OxKHmpA2nqIWnTqgSyRKd2xPvX2tgooqpmsx-8NEymNdCQPcrv4y_z2OgzxI3tiFRZEGs4bnjOJ7bmAYZv71mqcbi3TjHiyrT6j3jNPGrurFUpweVGFWWVQOMmKOKT3ELz9QPzhREb9Vj8\",\"n\":\"qYvDpV8DRU5hx9eXpE4Ms8nUXicEwrxUUz5gb5gkXpIeY82mqfQKKCP6PSFnkKYtRFTOUSm9cgGGfOd7O4NFsIsxLwXCj34X7ORr19eXKBLvG3bZJLxqRlbYuQshDMkQOui1sDBxvYnj5p4iHne6l2btH5grHOCShUWG-bKps5Y8bKNHod1pIOOBabVCmn3sUVUkZw8nyXkQqZbv-c8x6z0TEfhNOPOIt2AmmlNgrE_8g7-dnCvqfJnhv0c7qkOJzsb7OMmvVwsQNiM59D6uaWZr-vdANo6NggiZmCKUS3tpUvdXW7ec9WMPJWhrVEkRcbWXQnZ_C7pXFrz7rLeNKw\"}")
@MicronautTest(environments = "test")
class UserRepoTest {

    @Inject
    UserRepo userRepo;

    @Nested
    @DisplayName("getTenantPermissionsFor() - Permission aggregation JOIN query")
    class GetTenantPermissionsForTests {

        @Test
        @DisplayName("Returns all permissions for Unity Admin user across tenants")
        void getTenantPermissionsFor_unityAdmin_returnsSystemAndTenantPermissions() {
            // user 1 has: Unity Admin (tenant 1), Tenant role (tenant 2), Subtenant role (tenant 2)
            List<PermissionsService.TenantPermission> permissions = userRepo.getTenantPermissionsFor(1L);

            assertNotNull(permissions);
            assertFalse(permissions.isEmpty());

            // Should have SYSTEM scope permissions from Unity Admin role
            boolean hasSystemPermission = permissions.stream()
                    .anyMatch(p -> p.permissionScope() == Permission.PermissionScope.SYSTEM);
            assertTrue(hasSystemPermission, "Unity Admin should have SYSTEM scope permissions");

            // Should have TENANT scope permissions from Tenant role
            boolean hasTenantPermission = permissions.stream()
                    .anyMatch(p -> p.permissionScope() == Permission.PermissionScope.TENANT);
            assertTrue(hasTenantPermission, "User should have TENANT scope permissions");

            // Should have SUBTENANT scope permissions from Subtenant role
            boolean hasSubtenantPermission = permissions.stream()
                    .anyMatch(p -> p.permissionScope() == Permission.PermissionScope.SUBTENANT);
            assertTrue(hasSubtenantPermission, "User should have SUBTENANT scope permissions");
        }

        @Test
        @DisplayName("Returns correct tenant IDs with permissions")
        void getTenantPermissionsFor_unityAdmin_returnCorrectTenantIds() {
            List<PermissionsService.TenantPermission> permissions = userRepo.getTenantPermissionsFor(1L);

            // SYSTEM permission should be associated with tenant 1
            boolean hasSystemInTenant1 = permissions.stream()
                    .anyMatch(p -> p.tenantId() == 1L && p.permissionScope() == Permission.PermissionScope.SYSTEM);
            assertTrue(hasSystemInTenant1, "SYSTEM permission should be in tenant 1");

            // TENANT permission should be associated with tenant 2
            boolean hasTenantInTenant2 = permissions.stream()
                    .anyMatch(p -> p.tenantId() == 2L && p.permissionScope() == Permission.PermissionScope.TENANT);
            assertTrue(hasTenantInTenant2, "TENANT permission should be in tenant 2");
        }

        @Test
        @DisplayName("Returns correct permission names")
        void getTenantPermissionsFor_unityAdmin_returnsCorrectPermissionNames() {
            List<PermissionsService.TenantPermission> permissions = userRepo.getTenantPermissionsFor(1L);

            // Check for specific permission names
            boolean hasAuthServiceEdit = permissions.stream()
                    .anyMatch(p -> "AUTH_SERVICE_EDIT-SYSTEM".equals(p.permissionName()));
            assertTrue(hasAuthServiceEdit, "Should have AUTH_SERVICE_EDIT-SYSTEM permission");

            boolean hasLibre311RequestEditTenant = permissions.stream()
                    .anyMatch(p -> "LIBRE311_REQUEST_EDIT-TENANT".equals(p.permissionName()));
            assertTrue(hasLibre311RequestEditTenant, "Should have LIBRE311_REQUEST_EDIT-TENANT permission");

            boolean hasLibre311RequestEditSubtenant = permissions.stream()
                    .anyMatch(p -> "LIBRE311_REQUEST_EDIT-SUBTENANT".equals(p.permissionName()));
            assertTrue(hasLibre311RequestEditSubtenant, "Should have LIBRE311_REQUEST_EDIT-SUBTENANT permission");
        }

        @Test
        @DisplayName("Returns permissions only for tenant admin user")
        void getTenantPermissionsFor_tenantAdmin_returnsTenantPermissionsOnly() {
            // user 4 (acme-tenant-admin) only has Tenant role in tenant 2
            List<PermissionsService.TenantPermission> permissions = userRepo.getTenantPermissionsFor(4L);

            assertNotNull(permissions);
            assertFalse(permissions.isEmpty());

            // Should only have TENANT scope permission
            assertTrue(permissions.stream()
                    .allMatch(p -> p.permissionScope() == Permission.PermissionScope.TENANT),
                    "Tenant admin should only have TENANT scope permissions");

            // All permissions should be for tenant 2
            assertTrue(permissions.stream()
                    .allMatch(p -> p.tenantId() == 2L),
                    "All permissions should be for tenant 2");
        }

        @Test
        @DisplayName("Returns empty list for user with no roles")
        void getTenantPermissionsFor_userWithNoRoles_returnsEmptyList() {
            // user 2 (test@test.io) has no roles in the test data
            List<PermissionsService.TenantPermission> permissions = userRepo.getTenantPermissionsFor(2L);

            assertNotNull(permissions);
            assertTrue(permissions.isEmpty(), "User with no roles should have no permissions");
        }

        @Test
        @DisplayName("Returns empty list for non-existent user")
        void getTenantPermissionsFor_nonExistentUser_returnsEmptyList() {
            List<PermissionsService.TenantPermission> permissions = userRepo.getTenantPermissionsFor(999L);

            assertNotNull(permissions);
            assertTrue(permissions.isEmpty(), "Non-existent user should have no permissions");
        }
    }

    @Nested
    @DisplayName("isServiceAvailable() - Service availability JOIN query")
    class IsServiceAvailableTests {

        @Test
        @DisplayName("Returns true when service is enabled for user's tenant")
        void isServiceAvailable_enabledServiceForUserTenant_returnsTrue() {
            // user 1 has roles in tenant 2, which has service 1 (Libre311) enabled
            Boolean result = userRepo.isServiceAvailable(1L, 1L);

            assertTrue(result, "Service 1 should be available for user 1");
        }

        @Test
        @DisplayName("Returns true for tenant admin with enabled service")
        void isServiceAvailable_tenantAdminWithEnabledService_returnsTrue() {
            // user 4 (acme-tenant-admin) is in tenant 2, which has service 1 enabled
            Boolean result = userRepo.isServiceAvailable(4L, 1L);

            assertTrue(result, "Service 1 should be available for user 4");
        }

        @Test
        @DisplayName("Returns false when service is not linked to user's tenant")
        void isServiceAvailable_serviceNotLinkedToTenant_returnsFalse() {
            // Service 2 (Application2) is not linked to any tenant
            Boolean result = userRepo.isServiceAvailable(1L, 2L);

            assertFalse(result, "Service 2 should not be available (not linked to any tenant)");
        }

        @Test
        @DisplayName("Returns false for user with no tenant associations")
        void isServiceAvailable_userWithNoTenantAssociations_returnsFalse() {
            // user 2 (test@test.io) has no tenant associations
            Boolean result = userRepo.isServiceAvailable(2L, 1L);

            assertFalse(result, "Service should not be available for user with no tenant");
        }

        @Test
        @DisplayName("Returns false for non-existent user")
        void isServiceAvailable_nonExistentUser_returnsFalse() {
            Boolean result = userRepo.isServiceAvailable(999L, 1L);

            assertFalse(result, "Service should not be available for non-existent user");
        }

        @Test
        @DisplayName("Returns false for non-existent service")
        void isServiceAvailable_nonExistentService_returnsFalse() {
            Boolean result = userRepo.isServiceAvailable(1L, 999L);

            assertFalse(result, "Non-existent service should not be available");
        }
    }

    @Nested
    @DisplayName("existsByEmailAndTenantId() - User-tenant existence JOIN query")
    class ExistsByEmailAndTenantIdTests {

        @Test
        @DisplayName("Returns true when user exists in tenant")
        void existsByEmailAndTenantId_userExistsInTenant_returnsTrue() {
            // person1@test.io has roles in tenant 1
            boolean result = userRepo.existsByEmailAndTenantId("person1@test.io", 1L);

            assertTrue(result, "User should exist in tenant 1");
        }

        @Test
        @DisplayName("Returns true when user exists in different tenant")
        void existsByEmailAndTenantId_userExistsInDifferentTenant_returnsTrue() {
            // person1@test.io also has roles in tenant 2
            boolean result = userRepo.existsByEmailAndTenantId("person1@test.io", 2L);

            assertTrue(result, "User should exist in tenant 2");
        }

        @Test
        @DisplayName("Returns false when user does not exist in tenant")
        void existsByEmailAndTenantId_userNotInTenant_returnsFalse() {
            // test@test.io has no tenant associations
            boolean result = userRepo.existsByEmailAndTenantId("test@test.io", 1L);

            assertFalse(result, "User without tenant association should not exist in tenant");
        }

        @Test
        @DisplayName("Returns false for non-existent email")
        void existsByEmailAndTenantId_nonExistentEmail_returnsFalse() {
            boolean result = userRepo.existsByEmailAndTenantId("nonexistent@test.io", 1L);

            assertFalse(result, "Non-existent email should return false");
        }

        @Test
        @DisplayName("Returns false for non-existent tenant")
        void existsByEmailAndTenantId_nonExistentTenant_returnsFalse() {
            boolean result = userRepo.existsByEmailAndTenantId("person1@test.io", 999L);

            assertFalse(result, "Non-existent tenant should return false");
        }
    }

    @Nested
    @DisplayName("existsByEmailAndTenantEqualsAndIsTenantAdmin() - Tenant admin check JOIN query")
    class ExistsByEmailAndTenantAdminTests {

        @Test
        @DisplayName("Returns false when user is Unity Admin but not Tenant Administrator role")
        void existsByEmailAndTenantEqualsAndIsTenantAdmin_unityAdminNotTenantAdmin_returnsFalse() {
            // person1@test.io is Unity Admin in tenant 1, not "Tenant Administrator" role
            boolean result = userRepo.existsByEmailAndTenantEqualsAndIsTenantAdmin("person1@test.io", 1L);

            // Unity Administrator is different from Tenant Administrator
            assertFalse(result, "Unity Admin role is not the same as Tenant Administrator role");
        }

        @Test
        @DisplayName("Returns false for user without Tenant Administrator role")
        void existsByEmailAndTenantEqualsAndIsTenantAdmin_userWithTenantRole_returnsFalse() {
            // acme-tenant-admin@test.io has "Tenant role" in tenant 2, but not "Tenant Administrator"
            boolean result = userRepo.existsByEmailAndTenantEqualsAndIsTenantAdmin("acme-tenant-admin@test.io", 2L);

            // The role is "Tenant role" not "Tenant Administrator"
            assertFalse(result, "Tenant role is not the same as Tenant Administrator");
        }

        @Test
        @DisplayName("Returns false for user with no roles")
        void existsByEmailAndTenantEqualsAndIsTenantAdmin_userWithNoRoles_returnsFalse() {
            boolean result = userRepo.existsByEmailAndTenantEqualsAndIsTenantAdmin("test@test.io", 1L);

            assertFalse(result, "User with no roles is not a Tenant Administrator");
        }

        @Test
        @DisplayName("Returns false for non-existent email")
        void existsByEmailAndTenantEqualsAndIsTenantAdmin_nonExistentEmail_returnsFalse() {
            boolean result = userRepo.existsByEmailAndTenantEqualsAndIsTenantAdmin("nonexistent@test.io", 1L);

            assertFalse(result, "Non-existent email should return false");
        }
    }

    @Nested
    @DisplayName("existsByEmailAndRoleEqualsUnityAdmin() - Unity admin check JOIN query")
    class ExistsByEmailAndUnityAdminTests {

        @Test
        @DisplayName("Returns true for Unity Administrator")
        void existsByEmailAndRoleEqualsUnityAdmin_unityAdmin_returnsTrue() {
            // person1@test.io has Unity Administrator role
            boolean result = userRepo.existsByEmailAndRoleEqualsUnityAdmin("person1@test.io");

            assertTrue(result, "User with Unity Administrator role should return true");
        }

        @Test
        @DisplayName("Returns false for non-Unity Administrator")
        void existsByEmailAndRoleEqualsUnityAdmin_tenantAdmin_returnsFalse() {
            // acme-tenant-admin@test.io only has Tenant role, not Unity Administrator
            boolean result = userRepo.existsByEmailAndRoleEqualsUnityAdmin("acme-tenant-admin@test.io");

            assertFalse(result, "User without Unity Administrator role should return false");
        }

        @Test
        @DisplayName("Returns false for user with no roles")
        void existsByEmailAndRoleEqualsUnityAdmin_userWithNoRoles_returnsFalse() {
            boolean result = userRepo.existsByEmailAndRoleEqualsUnityAdmin("test@test.io");

            assertFalse(result, "User with no roles should return false");
        }

        @Test
        @DisplayName("Returns false for non-existent email")
        void existsByEmailAndRoleEqualsUnityAdmin_nonExistentEmail_returnsFalse() {
            boolean result = userRepo.existsByEmailAndRoleEqualsUnityAdmin("nonexistent@test.io");

            assertFalse(result, "Non-existent email should return false");
        }
    }

    @Nested
    @DisplayName("findAllByTenantId() - Users by tenant JOIN query")
    class FindAllByTenantIdTests {

        @Test
        @DisplayName("Returns all users in a tenant (includes duplicates for multiple roles)")
        void findAllByTenantId_tenantWithUsers_returnsUserList() {
            // Tenant 2 (acme) has user 1 and user 4
            // NOTE: Current query returns duplicate rows when user has multiple roles in same tenant.
            // user 1 has 2 roles in tenant 2 (role 2 and role 3), user 4 has 1 role = 3 total rows.
            // TODO: Consider adding DISTINCT to the query if unique users are desired.
            List<User> users = userRepo.findAllByTenantId(2L);

            assertNotNull(users);
            // Current behavior: returns 3 rows (user 1 appears twice due to multiple roles)
            assertEquals(3, users.size(), "Query returns row per user_role, not unique users");

            // Verify both users are present
            boolean hasUser1 = users.stream().anyMatch(u -> u.getId().equals(1L));
            boolean hasUser4 = users.stream().anyMatch(u -> u.getId().equals(4L));

            assertTrue(hasUser1, "User 1 should be in tenant 2");
            assertTrue(hasUser4, "User 4 should be in tenant 2");

            // Verify user 1 appears twice (has 2 roles), user 4 appears once (has 1 role)
            long user1Count = users.stream().filter(u -> u.getId().equals(1L)).count();
            long user4Count = users.stream().filter(u -> u.getId().equals(4L)).count();
            assertEquals(2, user1Count, "User 1 should appear twice (two roles in tenant 2)");
            assertEquals(1, user4Count, "User 4 should appear once (one role in tenant 2)");
        }

        @Test
        @DisplayName("Returns single user for tenant with one user")
        void findAllByTenantId_tenantWithOneUser_returnsSingleUser() {
            // Tenant 1 (SYSTEM) only has user 1
            List<User> users = userRepo.findAllByTenantId(1L);

            assertNotNull(users);
            assertEquals(1, users.size(), "Tenant 1 should have 1 user");
            assertEquals(1L, users.get(0).getId(), "The user should be user 1");
        }

        @Test
        @DisplayName("Returns correct user details")
        void findAllByTenantId_returnsCorrectUserDetails() {
            List<User> users = userRepo.findAllByTenantId(2L);

            Optional<User> acmeAdmin = users.stream()
                    .filter(u -> u.getId().equals(4L))
                    .findFirst();

            assertTrue(acmeAdmin.isPresent());
            assertEquals("acme-tenant-admin@test.io", acmeAdmin.get().getEmail());
            assertEquals("Acme Tenant", acmeAdmin.get().getFirstName());
            assertEquals("Admin", acmeAdmin.get().getLastName());
        }

        @Test
        @DisplayName("Returns empty list for non-existent tenant")
        void findAllByTenantId_nonExistentTenant_returnsEmptyList() {
            List<User> users = userRepo.findAllByTenantId(999L);

            assertNotNull(users);
            assertTrue(users.isEmpty(), "Non-existent tenant should return empty list");
        }
    }

    @Nested
    @DisplayName("getUserRolesByUserId() - User roles query")
    class GetUserRolesByUserIdTests {

        @Test
        @DisplayName("Returns all role IDs for user with multiple roles")
        void getUserRolesByUserId_userWithMultipleRoles_returnsAllRoleIds() {
            // user 1 has roles 1, 2, and 3
            List<Long> roleIds = userRepo.getUserRolesByUserId(1L);

            assertNotNull(roleIds);
            assertEquals(3, roleIds.size(), "User 1 should have 3 roles");

            assertTrue(roleIds.contains(1L), "Should have role 1 (Unity Administrator)");
            assertTrue(roleIds.contains(2L), "Should have role 2 (Tenant role)");
            assertTrue(roleIds.contains(3L), "Should have role 3 (Subtenant role)");
        }

        @Test
        @DisplayName("Returns single role for user with one role")
        void getUserRolesByUserId_userWithSingleRole_returnsSingleRoleId() {
            // user 4 only has role 2
            List<Long> roleIds = userRepo.getUserRolesByUserId(4L);

            assertNotNull(roleIds);
            assertEquals(1, roleIds.size(), "User 4 should have 1 role");
            assertEquals(2L, roleIds.get(0), "The role should be role 2");
        }

        @Test
        @DisplayName("Returns empty list for user with no roles")
        void getUserRolesByUserId_userWithNoRoles_returnsEmptyList() {
            // user 2 has no roles
            List<Long> roleIds = userRepo.getUserRolesByUserId(2L);

            assertNotNull(roleIds);
            assertTrue(roleIds.isEmpty(), "User with no roles should return empty list");
        }

        @Test
        @DisplayName("Returns empty list for non-existent user")
        void getUserRolesByUserId_nonExistentUser_returnsEmptyList() {
            List<Long> roleIds = userRepo.getUserRolesByUserId(999L);

            assertNotNull(roleIds);
            assertTrue(roleIds.isEmpty(), "Non-existent user should return empty list");
        }
    }

    @Nested
    @DisplayName("findByEmail() - Basic email lookup")
    class FindByEmailTests {

        @Test
        @DisplayName("Returns user when email exists")
        void findByEmail_existingEmail_returnsUser() {
            Optional<User> user = userRepo.findByEmail("person1@test.io");

            assertTrue(user.isPresent());
            assertEquals(1L, user.get().getId());
            assertEquals("Person", user.get().getFirstName());
            assertEquals("One", user.get().getLastName());
        }

        @Test
        @DisplayName("Returns empty for non-existent email")
        void findByEmail_nonExistentEmail_returnsEmpty() {
            Optional<User> user = userRepo.findByEmail("nonexistent@test.io");

            assertTrue(user.isEmpty());
        }
    }

    @Nested
    @DisplayName("findUserForAuthentication() - Authentication lookup")
    class FindUserForAuthenticationTests {

        @Test
        @DisplayName("Returns user with password for authentication")
        void findUserForAuthentication_existingUser_returnsUserWithPassword() {
            Optional<User> user = userRepo.findUserForAuthentication("person1@test.io");

            assertTrue(user.isPresent());
            assertEquals(1L, user.get().getId());
            assertNotNull(user.get().getPassword(), "Password should be included for authentication");
            assertTrue(user.get().getPassword().startsWith("$2a$"), "Password should be BCrypt hash");
        }

        @Test
        @DisplayName("Returns user status for disabled user check")
        void findUserForAuthentication_disabledUser_returnsUserWithDisabledStatus() {
            Optional<User> user = userRepo.findUserForAuthentication("disabled@test.io");

            assertTrue(user.isPresent());
            assertEquals(User.UserStatus.DISABLED, user.get().getStatus());
        }

        @Test
        @DisplayName("Returns empty for non-existent user")
        void findUserForAuthentication_nonExistentUser_returnsEmpty() {
            Optional<User> user = userRepo.findUserForAuthentication("nonexistent@test.io");

            assertTrue(user.isEmpty());
        }
    }
}
