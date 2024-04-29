import { z } from 'zod';

export const UnityAuthServicePropsSchema = z.object({
	baseURL: z.string()
});

export type UnityAuthServiceProps = z.infer<typeof UnityAuthServicePropsSchema>;

export const UnityAuthLoginResponseSchema = z.object({
	access_token: z.string(),
	token_type: z.string(),
	expires_in: z.number(),
	username: z.string()
});

export type UnityAuthLoginResponse = z.infer<typeof UnityAuthLoginResponseSchema>;

export const CompleteLoginResponseSchema = UnityAuthLoginResponseSchema;

export type CompleteLoginResponse = z.infer<typeof CompleteLoginResponseSchema>;
