import { z } from 'zod';
import type { TenantsResolver } from '../TenantsResolver/TenantsResolver';
import { TenantSchema } from '../TenantsResolver/shared';
import { TenantUserSchema } from '$lib/context/TenantUsersContext/TenantUsers';

export const UnityAuthServicePropsSchema = z.object({
	baseURL: z.string()
});

export type UnityAuthServiceProps = z.infer<typeof UnityAuthServicePropsSchema> & {
	tenantsResolver: TenantsResolver;
};

export const UnityAuthLoginResponseSchema = z.object({
	access_token: z.string(),
	token_type: z.string(),
	expires_in: z.number(),
	username: z.string(),
	tenants: z.array(TenantSchema).optional()
});

export type UnityAuthLoginResponse = z.infer<typeof UnityAuthLoginResponseSchema>;

export const CompleteLoginResponseSchema = UnityAuthLoginResponseSchema;

export type CompleteLoginResponse = z.infer<typeof CompleteLoginResponseSchema>;

export const GetTenantUsersResponseSchema = z.array(TenantUserSchema);
export type GetTenantUsersResponse = z.infer<typeof GetTenantUsersResponseSchema>;

export type TenantUsersResponse = {
	tenantUsers: GetTenantUsersResponse;
};
