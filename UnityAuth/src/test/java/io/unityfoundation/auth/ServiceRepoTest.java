package io.unityfoundation.auth;

import io.micronaut.context.annotation.Property;
import io.micronaut.test.extensions.junit5.annotation.MicronautTest;
import io.unityfoundation.auth.entities.Service;
import io.unityfoundation.auth.entities.ServiceRepo;
import jakarta.inject.Inject;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Integration tests for ServiceRepo complex JOIN queries.
 * Tests service retrieval based on tenant relationships.
 *
 * Test data reference (from afterMigrate.sql):
 * - service 1 (Libre311): ENABLED, linked to tenant 2 via tenant_service
 * - service 2 (Application2): ENABLED, not linked to any tenant
 * - tenant 1 (SYSTEM): ENABLED, no services linked
 * - tenant 2 (acme): ENABLED, has service 1 (Libre311) with status ENABLED
 */
@Property(name = "jwk.primary", value = "{\"p\":\"_OZyH1Mk3wR0oXw1C31t4kWOcaHFB6Njro1cYx52REnPiznn_JTtwvlAMpvV6LVCIZPgKMzdIEMY1gYs1LsO-5IFqWwegXmYJ0iKXbRrZshfWBCzRLK3QK5fER1le1XUBDhtDk7KIW_Xg-SZF4pf_LUEVKMnyUpspGI5F77jlJ8\",\"kty\":\"RSA\",\"q\":\"s9wvl7z8vkHQvo9xOUp-z0a2Z7LFBDil2uIjPh1FQzs34gFXH8dQPRox83TuN5d4KzdLPqQNQAfMXU9_KmxihNb_qDQahYugeELmcem04munxXqBdyZqWhWCy5YmujYqn44irwvoTbw6_RkMqjCmINPTPadptlPivsZ6RhKn8zk\",\"d\":\"ok3wmhOy8NZEHAotnFiH6ecFD6xf_9x33_fMRkqa3_KE8NZM7vmvNgElox2UvcP_2K5E7jOdL2XQdJCTIW3Qlj66yE2a84SYlbvxIc4hDrIog0XNt4FhavvshxxUIfDQo6Q8qXDR5v7nwt6SCopYC3t3KVRdJh08GzKoVxysd7afJjxXxx178gY29uMRqnwxFN1OGnWaiBr-xGKb1frJ6jOI1zvuuCaljZ4aZjc9vOR4y9ZmobgrzkMFnpDAmQZ7MWcVMyodRMOA2dEOckywPhg-dIVNiVIqzJqe5Yg1ilNookjwtqj2TpNU7Z9gPqzYB73PmQ2p5LMDheAPxcOmEQ\",\"e\":\"AQAB\",\"use\":\"sig\",\"kid\":\"e3be37177a7c42bcbadd7cc63715f216\",\"qi\":\"r--nAtaYPAgJq_8R1-kynpd53E17n-loDUgtVWBCx_RmdORX4Auilv1S83dD1mbcnYCbV_LmxiEjOiz-4gS_E0qVGqakAqQrO1hVUvJa_Y2uftDgwFmuJNGbpRU-K4Td_uUzdm48za8yJCgOdYsWp6PNMCcmQgiInzkR3XYV83I\",\"dp\":\"oQUcvmMSw8gzdin-IB2xW_MLecAVEgLu0dGBdD6N8HbKZQvub_xm0dAfFtnvvWXDAFwFyhR96i-uXX67Bos_Q9-6KSAE4E0KGmDucDESfPOw-QJREbl0QgOD1gLQfVGtVy6SCR0TR2zNXFWtP7bD3MNoSXdEOr5fI97CGSNaBWM\",\"alg\":\"RS256\",\"dq\":\"DM-WJDy10-dkMu6MpgQEXEcxHtnA5rgSODD7SaVUFaHWLSbjScQslu2SuUCO5y7GxG0_0spklzb2-356FE98BPI7a4Oqj_COEYLSXzLCS45XeN1s80utL5Vwp4eeYo0RJCQ_nDBA76iEmxp5qHWmn5f25-FQykfXUrdYZj1V8SE\",\"n\":\"sa6m2i-iNvj6ZSTdSHZaBrnv6DId4AqAXhOyl0yA5fNWYe6r51h24SXqk7DsGYHHh74ii74tP1lTpmy6RD67tCK-tbN-d6yc4Z6FfM8R83v2QZUfaAixgHGtw0n2toqsiHf6EloDV-B8q4GYyKDD6cLecoaIuTmMBTY3kts59U2t9W10YoLGsmFqLSz8qNF5HkahzB6_--2DiBfVGUKAXHC-SICGZCi-8efOetv6pt9vFiWEgwU_DgjRNYzLFt1SEmbGFUU4kbjQ7tNTMkHfzfwcT6qLt4kVKy2FNYsEMk24keWtCvW_RyO_fisZc0W9smX7WtYjEXhcAjDeqHgEZw\"}")
@Property(name = "jwk.secondary", value = "{\"p\":\"4qJ9RNlu6SuDT_MLArfzimvKEwmet_j12Z9EQeb5nMjZIOHTcWw__duebUytfWwxsRHhtSVXeMt-EryQAOulm2p1bfiVuparq93z9P5cPnb0oArFaw3eFNFEmX5U-lY8PzUTTsFxO4aVQYAKXD6DP7p5uPzuwpHFuNc71nNIXZE\",\"kty\":\"RSA\",\"q\":\"v4OhkWMbS_nq77HFanwZAT_obfJuQfOFOQBORL4ATAHGUXm2y4YqLNExZs7Wj1MA_6ya6Y00s2JBM7fWq_fPe4d9xo5aGrPdcp0G8W21kkfh9vuVPlHVQTgSP7FQ9qahvXxNwK_11yNr3p1HBmScJ5mHlMBpIJsFcvHA-uXe0Ps\",\"d\":\"EunrjnQ1-jJPSCrt2L94PUpDrakup8a4pXys52YSkJY-W6XidM0roOS6kr06P3G6VQgc6AL_BkvTQ_XS0oXHbXVprDQ5Syam5p9oxHBhhW_vSqIMgUOfm28uyB3Mtw9rBxdUxW3yElHioaR8a-exYhhyVXb1QEhxL_rcnthmhAkM2NcHi2UnxGKFTsC0abQ2MuQc1OAuW5veDiIF2hfdC41qE0_d8vB6FDWbblgUpbwB6uSZaViPs15Buq2oX9dCCw54-PgzkfehDt7lyqgupktbV1psnVVhL86shzt4QFnhd3k7VpFbjCNFtiJTrufV-XBWT0pl2w3VR9wrHJ1bYQ\",\"e\":\"AQAB\",\"use\":\"sig\",\"kid\":\"0794e938379540dc8eaa559508524a79\",\"qi\":\"jy-TNyXVy_44_n4KGAwIbZO2C4r6uNWuEdehBfQKkPhiP90myG1KZVfOoKNOK9bCv2mvZJcBz4c1ArElgpuSCV4-KFac1ZzQo_ic5aoIej8Qa80y2ogc-_Yv6_ZLHC1S76M-lm4jayk2-rvuBpy2pUvHbW6Srhs_szwz7ZfSkLg\",\"dp\":\"ApqdV9ortRAj7Ro8ySY17SQ56SgWI8T_hiWXUi6GNa_1FrShik8VGSSZ2GWmJKfGlmM_NaadL60e4LY77VbHy1ZYzQ-rIL60cEAXmnwFsU4Kl4AoLoe1QoX5BM53yXyOKqfAdgow898i_eKru82YEnZhCagWUjP8kpgefuNKNJE\",\"alg\":\"RS256\",\"dq\":\"bFF78WoXh0pMCdQHL2oPDnjh8kWa_OxKHmpA2nqIWnTqgSyRKd2xPvX2tgooqpmsx-8NEymNdCQPcrv4y_z2OgzxI3tiFRZEGs4bnjOJ7bmAYZv71mqcbi3TjHiyrT6j3jNPGrurFUpweVGFWWVQOMmKOKT3ELz9QPzhREb9Vj8\",\"n\":\"qYvDpV8DRU5hx9eXpE4Ms8nUXicEwrxUUz5gb5gkXpIeY82mqfQKKCP6PSFnkKYtRFTOUSm9cgGGfOd7O4NFsIsxLwXCj34X7ORr19eXKBLvG3bZJLxqRlbYuQshDMkQOui1sDBxvYnj5p4iHne6l2btH5grHOCShUWG-bKps5Y8bKNHod1pIOOBabVCmn3sUVUkZw8nyXkQqZbv-c8x6z0TEfhNOPOIt2AmmlNgrE_8g7-dnCvqfJnhv0c7qkOJzsb7OMmvVwsQNiM59D6uaWZr-vdANo6NggiZmCKUS3tpUvdXW7ec9WMPJWhrVEkRcbWXQnZ_C7pXFrz7rLeNKw\"}")
@MicronautTest
class ServiceRepoTest {

    @Inject
    ServiceRepo serviceRepo;

    @Nested
    @DisplayName("findByTenantId() - Service-tenant relationship JOIN query")
    class FindByTenantIdTests {

        @Test
        @DisplayName("Returns service when linked to tenant and not disabled")
        void findByTenantId_serviceLinkedToTenant_returnsService() {
            // Service 1 (Libre311) is linked to tenant 2 with status ENABLED
            Optional<Service> service = serviceRepo.findByTenantId(1L, 2L);

            assertTrue(service.isPresent(), "Service should be found for tenant");
            assertEquals(1L, service.get().getId());
            assertEquals("Libre311", service.get().getName());
            assertEquals("Libre311", service.get().getDescription());
        }

        @Test
        @DisplayName("Returns correct service details")
        void findByTenantId_returnsCorrectServiceDetails() {
            Optional<Service> service = serviceRepo.findByTenantId(1L, 2L);

            assertTrue(service.isPresent());
            assertEquals(Service.ServiceStatus.ENABLED, service.get().getStatus());
        }

        @Test
        @DisplayName("Returns empty when service is not linked to tenant")
        void findByTenantId_serviceNotLinkedToTenant_returnsEmpty() {
            // Service 2 (Application2) is not linked to any tenant
            Optional<Service> service = serviceRepo.findByTenantId(2L, 2L);

            assertTrue(service.isEmpty(), "Service not linked to tenant should not be found");
        }

        @Test
        @DisplayName("Returns empty when tenant has no services")
        void findByTenantId_tenantWithNoServices_returnsEmpty() {
            // Tenant 1 (SYSTEM) has no services linked
            Optional<Service> service = serviceRepo.findByTenantId(1L, 1L);

            assertTrue(service.isEmpty(), "Tenant with no services should return empty");
        }

        @Test
        @DisplayName("Returns empty for non-existent service")
        void findByTenantId_nonExistentService_returnsEmpty() {
            Optional<Service> service = serviceRepo.findByTenantId(999L, 2L);

            assertTrue(service.isEmpty(), "Non-existent service should return empty");
        }

        @Test
        @DisplayName("Returns empty for non-existent tenant")
        void findByTenantId_nonExistentTenant_returnsEmpty() {
            Optional<Service> service = serviceRepo.findByTenantId(1L, 999L);

            assertTrue(service.isEmpty(), "Non-existent tenant should return empty");
        }

        @Test
        @DisplayName("Parameter order is serviceId first, then tenantId")
        void findByTenantId_verifyParameterOrder() {
            // The method signature is findByTenantId(Long serviceId, Long tenantId)
            // which is somewhat confusing but let's verify the behavior

            // This should work: service 1, tenant 2
            Optional<Service> correct = serviceRepo.findByTenantId(1L, 2L);
            assertTrue(correct.isPresent(), "Should find service 1 for tenant 2");

            // This should not work: service 2, tenant 1 (neither exists in relationship)
            Optional<Service> incorrect = serviceRepo.findByTenantId(2L, 1L);
            assertTrue(incorrect.isEmpty(), "Should not find service 2 for tenant 1");
        }
    }

    @Nested
    @DisplayName("CrudRepository methods - Basic CRUD operations")
    class BasicCrudTests {

        @Test
        @DisplayName("findById returns service when exists")
        void findById_existingService_returnsService() {
            Optional<Service> service = serviceRepo.findById(1L);

            assertTrue(service.isPresent());
            assertEquals("Libre311", service.get().getName());
        }

        @Test
        @DisplayName("findById returns empty for non-existent service")
        void findById_nonExistentService_returnsEmpty() {
            Optional<Service> service = serviceRepo.findById(999L);

            assertTrue(service.isEmpty());
        }

        @Test
        @DisplayName("findAll returns all services")
        void findAll_returnAllServices() {
            Iterable<Service> services = serviceRepo.findAll();

            assertNotNull(services);
            List<Service> serviceList = new ArrayList<>();
            services.forEach(serviceList::add);
            assertEquals(2, serviceList.size(), "Should have 2 services in test data");
        }

        @Test
        @DisplayName("existsById returns true for existing service")
        void existsById_existingService_returnsTrue() {
            boolean exists = serviceRepo.existsById(1L);

            assertTrue(exists);
        }

        @Test
        @DisplayName("existsById returns false for non-existent service")
        void existsById_nonExistentService_returnsFalse() {
            boolean exists = serviceRepo.existsById(999L);

            assertFalse(exists);
        }

        @Test
        @DisplayName("count returns correct number of services")
        void count_returnsCorrectCount() {
            long count = serviceRepo.count();

            assertEquals(2, count, "Should have 2 services in test data");
        }
    }
}
