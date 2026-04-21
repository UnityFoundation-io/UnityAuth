package io.unityfoundation.auth;

import io.unityfoundation.auth.PermissionsService.TenantPermission;
import io.unityfoundation.auth.entities.Permission.PermissionScope;
import io.unityfoundation.auth.entities.Tenant;
import io.unityfoundation.auth.entities.User;
import io.unityfoundation.auth.entities.UserRepo;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

import java.util.Collections;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

/**
 * Unit tests for PermissionsService.
 * Tests permission checking logic across different scopes (SYSTEM, TENANT, SUBTENANT).
 */
class PermissionsServiceTest {

    private UserRepo userRepo;
    private PermissionsService permissionsService;
    private User testUser;
    private Tenant testTenant;

    @BeforeEach
    void setUp() {
        userRepo = mock(UserRepo.class);
        permissionsService = new PermissionsService(userRepo);

        testUser = new User();
        testUser.setId(1L);
        testUser.setEmail("test@example.com");

        testTenant = new Tenant();
        testTenant.setId(100L);
        testTenant.setName("Test Tenant");
    }

    @Nested
    class GetPermissionsFor {

        @Test
        void returnsSystemScopePermissions_regardlessOfTenant() {
            List<TenantPermission> permissions = List.of(
                    new TenantPermission(999L, "SYSTEM_ADMIN", PermissionScope.SYSTEM)
            );
            when(userRepo.getTenantPermissionsFor(testUser.getId())).thenReturn(permissions);

            List<String> result = permissionsService.getPermissionsFor(testUser, testTenant);

            assertEquals(1, result.size());
            assertTrue(result.contains("SYSTEM_ADMIN"));
        }

        @Test
        void returnsTenantScopePermissions_whenBelongsToTenant() {
            List<TenantPermission> permissions = List.of(
                    new TenantPermission(100L, "TENANT_MANAGE", PermissionScope.TENANT)
            );
            when(userRepo.getTenantPermissionsFor(testUser.getId())).thenReturn(permissions);

            List<String> result = permissionsService.getPermissionsFor(testUser, testTenant);

            assertEquals(1, result.size());
            assertTrue(result.contains("TENANT_MANAGE"));
        }

        @Test
        void excludesTenantScopePermissions_whenBelongsToDifferentTenant() {
            List<TenantPermission> permissions = List.of(
                    new TenantPermission(200L, "TENANT_MANAGE", PermissionScope.TENANT)
            );
            when(userRepo.getTenantPermissionsFor(testUser.getId())).thenReturn(permissions);

            List<String> result = permissionsService.getPermissionsFor(testUser, testTenant);

            assertTrue(result.isEmpty());
        }

        @Test
        void returnsSubtenantScopePermissions_whenBelongsToTenant() {
            List<TenantPermission> permissions = List.of(
                    new TenantPermission(100L, "SUBTENANT_READ", PermissionScope.SUBTENANT)
            );
            when(userRepo.getTenantPermissionsFor(testUser.getId())).thenReturn(permissions);

            List<String> result = permissionsService.getPermissionsFor(testUser, testTenant);

            assertEquals(1, result.size());
            assertTrue(result.contains("SUBTENANT_READ"));
        }

        @Test
        void excludesSubtenantScopePermissions_whenBelongsToDifferentTenant() {
            List<TenantPermission> permissions = List.of(
                    new TenantPermission(200L, "SUBTENANT_READ", PermissionScope.SUBTENANT)
            );
            when(userRepo.getTenantPermissionsFor(testUser.getId())).thenReturn(permissions);

            List<String> result = permissionsService.getPermissionsFor(testUser, testTenant);

            assertTrue(result.isEmpty());
        }

        @Test
        void returnsMixedScopePermissions_withCorrectFiltering() {
            List<TenantPermission> permissions = List.of(
                    new TenantPermission(999L, "SYSTEM_ADMIN", PermissionScope.SYSTEM),
                    new TenantPermission(100L, "TENANT_MANAGE", PermissionScope.TENANT),
                    new TenantPermission(200L, "OTHER_TENANT_MANAGE", PermissionScope.TENANT),
                    new TenantPermission(100L, "SUBTENANT_READ", PermissionScope.SUBTENANT),
                    new TenantPermission(300L, "OTHER_SUBTENANT_READ", PermissionScope.SUBTENANT)
            );
            when(userRepo.getTenantPermissionsFor(testUser.getId())).thenReturn(permissions);

            List<String> result = permissionsService.getPermissionsFor(testUser, testTenant);

            assertEquals(3, result.size());
            assertTrue(result.contains("SYSTEM_ADMIN"));
            assertTrue(result.contains("TENANT_MANAGE"));
            assertTrue(result.contains("SUBTENANT_READ"));
            assertFalse(result.contains("OTHER_TENANT_MANAGE"));
            assertFalse(result.contains("OTHER_SUBTENANT_READ"));
        }

        @Test
        void returnsEmptyList_whenUserHasNoPermissions() {
            when(userRepo.getTenantPermissionsFor(testUser.getId())).thenReturn(Collections.emptyList());

            List<String> result = permissionsService.getPermissionsFor(testUser, testTenant);

            assertTrue(result.isEmpty());
        }

        @Test
        void returnsMultipleSystemPermissions() {
            List<TenantPermission> permissions = List.of(
                    new TenantPermission(1L, "SYSTEM_ADMIN", PermissionScope.SYSTEM),
                    new TenantPermission(2L, "SYSTEM_READ", PermissionScope.SYSTEM),
                    new TenantPermission(3L, "SYSTEM_WRITE", PermissionScope.SYSTEM)
            );
            when(userRepo.getTenantPermissionsFor(testUser.getId())).thenReturn(permissions);

            List<String> result = permissionsService.getPermissionsFor(testUser, testTenant);

            assertEquals(3, result.size());
            assertTrue(result.containsAll(List.of("SYSTEM_ADMIN", "SYSTEM_READ", "SYSTEM_WRITE")));
        }
    }

    @Nested
    class CheckUserPermission {

        @Test
        void returnsMatchingPermissions_whenUserHasRequestedPermissions() {
            List<TenantPermission> userPermissions = List.of(
                    new TenantPermission(100L, "READ_USERS", PermissionScope.TENANT),
                    new TenantPermission(100L, "WRITE_USERS", PermissionScope.TENANT)
            );
            when(userRepo.getTenantPermissionsFor(testUser.getId())).thenReturn(userPermissions);

            List<String> requestedPermissions = List.of("READ_USERS", "DELETE_USERS");
            List<String> result = permissionsService.checkUserPermission(testUser, testTenant, requestedPermissions);

            assertEquals(1, result.size());
            assertTrue(result.contains("READ_USERS"));
            assertFalse(result.contains("DELETE_USERS"));
        }

        @Test
        void returnsEmptyList_whenUserHasNoneOfRequestedPermissions() {
            List<TenantPermission> userPermissions = List.of(
                    new TenantPermission(100L, "READ_USERS", PermissionScope.TENANT)
            );
            when(userRepo.getTenantPermissionsFor(testUser.getId())).thenReturn(userPermissions);

            List<String> requestedPermissions = List.of("DELETE_USERS", "ADMIN");
            List<String> result = permissionsService.checkUserPermission(testUser, testTenant, requestedPermissions);

            assertTrue(result.isEmpty());
        }

        @Test
        void returnsAllRequestedPermissions_whenUserHasAll() {
            List<TenantPermission> userPermissions = List.of(
                    new TenantPermission(100L, "READ_USERS", PermissionScope.TENANT),
                    new TenantPermission(100L, "WRITE_USERS", PermissionScope.TENANT),
                    new TenantPermission(100L, "DELETE_USERS", PermissionScope.TENANT)
            );
            when(userRepo.getTenantPermissionsFor(testUser.getId())).thenReturn(userPermissions);

            List<String> requestedPermissions = List.of("READ_USERS", "WRITE_USERS");
            List<String> result = permissionsService.checkUserPermission(testUser, testTenant, requestedPermissions);

            assertEquals(2, result.size());
            assertTrue(result.containsAll(requestedPermissions));
        }

        @Test
        void includesSystemScopePermissions_inPermissionCheck() {
            List<TenantPermission> userPermissions = List.of(
                    new TenantPermission(999L, "SYSTEM_ADMIN", PermissionScope.SYSTEM)
            );
            when(userRepo.getTenantPermissionsFor(testUser.getId())).thenReturn(userPermissions);

            List<String> requestedPermissions = List.of("SYSTEM_ADMIN", "TENANT_ADMIN");
            List<String> result = permissionsService.checkUserPermission(testUser, testTenant, requestedPermissions);

            assertEquals(1, result.size());
            assertTrue(result.contains("SYSTEM_ADMIN"));
        }

        @Test
        void excludesOtherTenantPermissions_fromCheck() {
            List<TenantPermission> userPermissions = List.of(
                    new TenantPermission(200L, "READ_USERS", PermissionScope.TENANT)
            );
            when(userRepo.getTenantPermissionsFor(testUser.getId())).thenReturn(userPermissions);

            List<String> requestedPermissions = List.of("READ_USERS");
            List<String> result = permissionsService.checkUserPermission(testUser, testTenant, requestedPermissions);

            assertTrue(result.isEmpty());
        }

        @Test
        void returnsEmptyList_whenRequestedPermissionsListIsEmpty() {
            List<TenantPermission> userPermissions = List.of(
                    new TenantPermission(100L, "READ_USERS", PermissionScope.TENANT)
            );
            when(userRepo.getTenantPermissionsFor(testUser.getId())).thenReturn(userPermissions);

            List<String> result = permissionsService.checkUserPermission(testUser, testTenant, Collections.emptyList());

            assertTrue(result.isEmpty());
        }
    }

    @Nested
    class CheckUserPermissionsAcrossAllTenants {

        @Test
        void returnsMatchingPermissions_fromAllTenants() {
            List<TenantPermission> userPermissions = List.of(
                    new TenantPermission(100L, "READ_USERS", PermissionScope.TENANT),
                    new TenantPermission(200L, "WRITE_USERS", PermissionScope.TENANT),
                    new TenantPermission(300L, "DELETE_USERS", PermissionScope.TENANT)
            );
            when(userRepo.getTenantPermissionsFor(testUser.getId())).thenReturn(userPermissions);

            List<String> requestedPermissions = List.of("READ_USERS", "WRITE_USERS", "ADMIN");
            List<String> result = permissionsService.checkUserPermissionsAcrossAllTenants(testUser, requestedPermissions);

            assertEquals(2, result.size());
            assertTrue(result.contains("READ_USERS"));
            assertTrue(result.contains("WRITE_USERS"));
        }

        @Test
        void includesSystemScopePermissions() {
            List<TenantPermission> userPermissions = List.of(
                    new TenantPermission(1L, "SYSTEM_ADMIN", PermissionScope.SYSTEM),
                    new TenantPermission(100L, "TENANT_READ", PermissionScope.TENANT)
            );
            when(userRepo.getTenantPermissionsFor(testUser.getId())).thenReturn(userPermissions);

            List<String> requestedPermissions = List.of("SYSTEM_ADMIN", "TENANT_READ");
            List<String> result = permissionsService.checkUserPermissionsAcrossAllTenants(testUser, requestedPermissions);

            assertEquals(2, result.size());
            assertTrue(result.containsAll(requestedPermissions));
        }

        @Test
        void includesSubtenantScopePermissions() {
            List<TenantPermission> userPermissions = List.of(
                    new TenantPermission(100L, "SUBTENANT_READ", PermissionScope.SUBTENANT),
                    new TenantPermission(200L, "SUBTENANT_WRITE", PermissionScope.SUBTENANT)
            );
            when(userRepo.getTenantPermissionsFor(testUser.getId())).thenReturn(userPermissions);

            List<String> requestedPermissions = List.of("SUBTENANT_READ", "SUBTENANT_WRITE", "OTHER");
            List<String> result = permissionsService.checkUserPermissionsAcrossAllTenants(testUser, requestedPermissions);

            assertEquals(2, result.size());
            assertTrue(result.contains("SUBTENANT_READ"));
            assertTrue(result.contains("SUBTENANT_WRITE"));
        }

        @Test
        void returnsEmptyList_whenNoPermissionsMatch() {
            List<TenantPermission> userPermissions = List.of(
                    new TenantPermission(100L, "READ_USERS", PermissionScope.TENANT)
            );
            when(userRepo.getTenantPermissionsFor(testUser.getId())).thenReturn(userPermissions);

            List<String> requestedPermissions = List.of("ADMIN", "SUPER_ADMIN");
            List<String> result = permissionsService.checkUserPermissionsAcrossAllTenants(testUser, requestedPermissions);

            assertTrue(result.isEmpty());
        }

        @Test
        void returnsEmptyList_whenUserHasNoPermissions() {
            when(userRepo.getTenantPermissionsFor(testUser.getId())).thenReturn(Collections.emptyList());

            List<String> requestedPermissions = List.of("READ_USERS");
            List<String> result = permissionsService.checkUserPermissionsAcrossAllTenants(testUser, requestedPermissions);

            assertTrue(result.isEmpty());
        }

        @Test
        void returnsEmptyList_whenRequestedPermissionsIsEmpty() {
            List<TenantPermission> userPermissions = List.of(
                    new TenantPermission(100L, "READ_USERS", PermissionScope.TENANT)
            );
            when(userRepo.getTenantPermissionsFor(testUser.getId())).thenReturn(userPermissions);

            List<String> result = permissionsService.checkUserPermissionsAcrossAllTenants(testUser, Collections.emptyList());

            assertTrue(result.isEmpty());
        }

        @Test
        void handlesDuplicatePermissionNames_acrossDifferentTenants() {
            // Same permission name from different tenants should appear in results
            List<TenantPermission> userPermissions = List.of(
                    new TenantPermission(100L, "READ_USERS", PermissionScope.TENANT),
                    new TenantPermission(200L, "READ_USERS", PermissionScope.TENANT),
                    new TenantPermission(300L, "READ_USERS", PermissionScope.TENANT)
            );
            when(userRepo.getTenantPermissionsFor(testUser.getId())).thenReturn(userPermissions);

            List<String> requestedPermissions = List.of("READ_USERS");
            List<String> result = permissionsService.checkUserPermissionsAcrossAllTenants(testUser, requestedPermissions);

            // All instances of READ_USERS should match, but result may contain duplicates
            // based on current implementation (no distinct)
            assertFalse(result.isEmpty());
            assertTrue(result.stream().allMatch("READ_USERS"::equals));
        }
    }

    @Nested
    class TenantPermissionRecord {

        @Test
        void createsRecordWithCorrectValues() {
            TenantPermission permission = new TenantPermission(100L, "TEST_PERMISSION", PermissionScope.TENANT);

            assertEquals(100L, permission.tenantId());
            assertEquals("TEST_PERMISSION", permission.permissionName());
            assertEquals(PermissionScope.TENANT, permission.permissionScope());
        }

        @Test
        void recordsWithSameValuesAreEqual() {
            TenantPermission permission1 = new TenantPermission(100L, "TEST", PermissionScope.SYSTEM);
            TenantPermission permission2 = new TenantPermission(100L, "TEST", PermissionScope.SYSTEM);

            assertEquals(permission1, permission2);
            assertEquals(permission1.hashCode(), permission2.hashCode());
        }

        @Test
        void recordsWithDifferentValuesAreNotEqual() {
            TenantPermission permission1 = new TenantPermission(100L, "TEST", PermissionScope.SYSTEM);
            TenantPermission permission2 = new TenantPermission(200L, "TEST", PermissionScope.SYSTEM);
            TenantPermission permission3 = new TenantPermission(100L, "OTHER", PermissionScope.SYSTEM);
            TenantPermission permission4 = new TenantPermission(100L, "TEST", PermissionScope.TENANT);

            assertNotEquals(permission1, permission2);
            assertNotEquals(permission1, permission3);
            assertNotEquals(permission1, permission4);
        }
    }

    @Nested
    class EdgeCases {

        @Test
        void handlesNullUserId_gracefully() {
            User userWithNullId = new User();
            userWithNullId.setId(null);
            when(userRepo.getTenantPermissionsFor(null)).thenReturn(Collections.emptyList());

            List<String> result = permissionsService.getPermissionsFor(userWithNullId, testTenant);

            assertTrue(result.isEmpty());
            verify(userRepo).getTenantPermissionsFor(null);
        }

        @Test
        void handlesVeryLargePermissionsList() {
            List<TenantPermission> manyPermissions = java.util.stream.IntStream.range(0, 1000)
                    .mapToObj(i -> new TenantPermission(100L, "PERMISSION_" + i, PermissionScope.TENANT))
                    .toList();
            when(userRepo.getTenantPermissionsFor(testUser.getId())).thenReturn(manyPermissions);

            List<String> result = permissionsService.getPermissionsFor(testUser, testTenant);

            assertEquals(1000, result.size());
        }

        @Test
        void handlesPermissionsWithSpecialCharacters() {
            List<TenantPermission> permissions = List.of(
                    new TenantPermission(100L, "permission:read:users", PermissionScope.TENANT),
                    new TenantPermission(100L, "permission.write.users", PermissionScope.TENANT),
                    new TenantPermission(100L, "permission-delete-users", PermissionScope.TENANT)
            );
            when(userRepo.getTenantPermissionsFor(testUser.getId())).thenReturn(permissions);

            List<String> requestedPermissions = List.of("permission:read:users", "permission.write.users");
            List<String> result = permissionsService.checkUserPermission(testUser, testTenant, requestedPermissions);

            assertEquals(2, result.size());
            assertTrue(result.contains("permission:read:users"));
            assertTrue(result.contains("permission.write.users"));
        }

        @Test
        void verifyUserRepoCalledWithCorrectUserId() {
            when(userRepo.getTenantPermissionsFor(anyLong())).thenReturn(Collections.emptyList());

            permissionsService.getPermissionsFor(testUser, testTenant);

            verify(userRepo, times(1)).getTenantPermissionsFor(1L);
        }

        @Test
        void cachesRepoCallPerMethod_notAcrossMethods() {
            when(userRepo.getTenantPermissionsFor(testUser.getId())).thenReturn(Collections.emptyList());

            permissionsService.getPermissionsFor(testUser, testTenant);
            permissionsService.checkUserPermission(testUser, testTenant, List.of("TEST"));
            permissionsService.checkUserPermissionsAcrossAllTenants(testUser, List.of("TEST"));

            // Each method call should call the repo
            verify(userRepo, times(3)).getTenantPermissionsFor(testUser.getId());
        }
    }

    @Nested
    class ScopeBoundaryTests {

        @Test
        void systemScope_matchesForAnyTenantId() {
            // SYSTEM scope should match regardless of tenantId in the permission
            Tenant differentTenant = new Tenant();
            differentTenant.setId(999L);

            List<TenantPermission> permissions = List.of(
                    new TenantPermission(1L, "SYSTEM_ADMIN", PermissionScope.SYSTEM)
            );
            when(userRepo.getTenantPermissionsFor(testUser.getId())).thenReturn(permissions);

            List<String> result = permissionsService.getPermissionsFor(testUser, differentTenant);

            assertEquals(1, result.size());
            assertTrue(result.contains("SYSTEM_ADMIN"));
        }

        @Test
        void tenantScope_requiresExactTenantMatch() {
            Tenant tenant1 = new Tenant();
            tenant1.setId(100L);
            Tenant tenant2 = new Tenant();
            tenant2.setId(101L);

            List<TenantPermission> permissions = List.of(
                    new TenantPermission(100L, "TENANT_PERMISSION", PermissionScope.TENANT)
            );
            when(userRepo.getTenantPermissionsFor(testUser.getId())).thenReturn(permissions);

            List<String> resultTenant1 = permissionsService.getPermissionsFor(testUser, tenant1);
            List<String> resultTenant2 = permissionsService.getPermissionsFor(testUser, tenant2);

            assertEquals(1, resultTenant1.size());
            assertTrue(resultTenant1.contains("TENANT_PERMISSION"));
            assertTrue(resultTenant2.isEmpty());
        }

        @Test
        void subtenantScope_requiresExactTenantMatch() {
            Tenant tenant1 = new Tenant();
            tenant1.setId(100L);
            Tenant tenant2 = new Tenant();
            tenant2.setId(101L);

            List<TenantPermission> permissions = List.of(
                    new TenantPermission(100L, "SUBTENANT_PERMISSION", PermissionScope.SUBTENANT)
            );
            when(userRepo.getTenantPermissionsFor(testUser.getId())).thenReturn(permissions);

            List<String> resultTenant1 = permissionsService.getPermissionsFor(testUser, tenant1);
            List<String> resultTenant2 = permissionsService.getPermissionsFor(testUser, tenant2);

            assertEquals(1, resultTenant1.size());
            assertTrue(resultTenant1.contains("SUBTENANT_PERMISSION"));
            assertTrue(resultTenant2.isEmpty());
        }

        @Test
        void allScopesInSingleQuery_filteredCorrectly() {
            List<TenantPermission> permissions = List.of(
                    new TenantPermission(1L, "SYS1", PermissionScope.SYSTEM),
                    new TenantPermission(2L, "SYS2", PermissionScope.SYSTEM),
                    new TenantPermission(100L, "TENANT1", PermissionScope.TENANT),
                    new TenantPermission(200L, "TENANT2", PermissionScope.TENANT),
                    new TenantPermission(100L, "SUB1", PermissionScope.SUBTENANT),
                    new TenantPermission(300L, "SUB2", PermissionScope.SUBTENANT)
            );
            when(userRepo.getTenantPermissionsFor(testUser.getId())).thenReturn(permissions);

            List<String> result = permissionsService.getPermissionsFor(testUser, testTenant);

            assertEquals(4, result.size());
            assertTrue(result.containsAll(List.of("SYS1", "SYS2", "TENANT1", "SUB1")));
            assertFalse(result.contains("TENANT2"));
            assertFalse(result.contains("SUB2"));
        }
    }
}
