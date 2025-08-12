import { z } from 'zod';

export const TenantSchema = z.object({
	id: z.number(),
	name: z.string()
});

export type Tenant = z.infer<typeof TenantSchema>;

export const TenantsSuccessResponseSchema = z.array(TenantSchema);

export type TenantsSuccessResponse = z.infer<typeof TenantsSuccessResponseSchema>;

export function isTenantsSuccessResponse(unknown: unknown): unknown is TenantsSuccessResponse {
	return TenantsSuccessResponseSchema.safeParse(unknown).success;
}

export const TenantsFailureResponseSchema = z.object({
	errorMessage: z.string()
});

export type TenantsFailureResponse = z.infer<typeof TenantsFailureResponseSchema>;

export const TenantsResponseSchema = z.union([
	TenantsSuccessResponseSchema,
	TenantsFailureResponseSchema
]);

export type TenantsResponse = z.infer<typeof TenantsResponseSchema>;
