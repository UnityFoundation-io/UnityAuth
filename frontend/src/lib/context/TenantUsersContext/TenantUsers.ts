import { z } from 'zod';

// const StatusSchema = z.union([z.literal('ENABLED'), z.literal('DISABLED')]);

export const TenantUserSchema = z.object({
	id: z.number(),
	email: z.string(),
	// password: z.string(),
	// status: StatusSchema,
	firstName: z.string(),
	lastName: z.string()
});

export type TenantUser = z.infer<typeof TenantUserSchema>;
