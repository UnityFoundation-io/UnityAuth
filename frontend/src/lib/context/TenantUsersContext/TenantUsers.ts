import { z } from 'zod';

const StatusSchema = z.union([z.literal('ENABLED'), z.literal('DISABLED')]);

export const TenantUserSchema = z.object({
	id: z.number(),
	email: z.string(),
	password: z.string(),
	status: StatusSchema,
	first_name: z.string(),
	last_name: z.string()
});

export type TenantUser = z.infer<typeof TenantUserSchema>;
