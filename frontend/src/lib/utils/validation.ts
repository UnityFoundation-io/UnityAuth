import { z, ZodError } from 'zod';

// Types

export type UnvalidatedInput<T> = {
	type: 'unvalidated';
	value?: T;
	error: undefined;
};

export type ValidInput<T> = {
	type: 'valid';
	value: T;
	error: undefined;
};

export type InvalidInput<T> = {
	type: 'invalid';
	value?: T;
	error: string;
};

export type ValidatedInput<T> = ValidInput<T> | InvalidInput<T>;

export type FormInputValue<T> = UnvalidatedInput<T> | ValidatedInput<T>;

export type InputValidator<T> = (value: FormInputValue<T>) => ValidatedInput<T>;

// Functions

export function createInput<T>(startingValue: T | undefined = undefined): FormInputValue<T> {
	return {
		type: 'unvalidated',
		value: startingValue,
		error: undefined
	};
}

export function inputValidatorFactory<T>(schema: z.ZodType<T, z.ZodTypeDef, T>): InputValidator<T> {
	const validator: InputValidator<T> = (input: FormInputValue<T>): ValidatedInput<T> => {
		try {
			const parsedValue = schema.parse(input.value);
			return { error: undefined, type: 'valid', value: parsedValue };
		} catch (error) {
			const zodError = error as ZodError;
			const firstIssue = zodError.errors[0];
			return {
				type: 'invalid',
				value: input.value,
				error: firstIssue?.message ?? zodError.message
			};
		}
	};

	return validator;
}

export const emailValidator: InputValidator<string> = inputValidatorFactory(z.string().email());
