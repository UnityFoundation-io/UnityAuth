import { z } from 'zod';
import type { TenantsResolver } from '../TenantsResolver/TenantsResolver';
import { TenantSchema } from '../TenantsResolver/shared';

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
