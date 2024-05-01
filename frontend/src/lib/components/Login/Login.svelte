<script lang="ts">
	import { Button, Card, Input } from 'stwui';
	import { createEventDispatcher } from 'svelte';
	import { type FormInputValue } from '$lib/utils/validation';
	import { dispatchEventFunctionFactory, type EventDispatchTypeMap } from './login';

	const dispatch = createEventDispatcher<EventDispatchTypeMap>();

	export let emailInput: FormInputValue<string | undefined>;
	export let passwordInput: FormInputValue<string | undefined>;
	export let errorMessage: string | undefined;

	const { onChange, onSubmit } = dispatchEventFunctionFactory(dispatch);
</script>

<Card class="w-3/4 sm:w-1/2 lg:w-1/3">
	{#if errorMessage}
		<div class="flex justify-center rounded-t-md bg-red-500 p-2 text-white">
			<span>{errorMessage}</span>
		</div>
	{/if}

	<div class="m-4 flex flex-col items-center">
		<h1 class="text-lg">{'Login'}</h1>
	</div>

	<div class="m-4">
		<Input
			allowClear
			id="email-desktop"
			type="email"
			name="email-desktop"
			placeholder={'example@email.com'}
			error={emailInput.error}
			value={emailInput.value}
			on:change={(e) => onChange(e, 'email')}
		>
			<Input.Label slot="label">{'Email'}</Input.Label>
		</Input>
	</div>

	<div class="m-4">
		<Input
			allowClear
			id="password-desktop"
			type="password"
			name="password-desktop"
			showPasswordToggle={true}
			placeholder={'password'}
			error={passwordInput.error}
			value={passwordInput.value}
			on:change={(e) => onChange(e, 'password')}
		>
			<Input.Label slot="label">{'Password'}</Input.Label>
		</Input>
	</div>

	<div class="m-4">
		<Button type="primary" on:click={onSubmit}>
			{'Submit'}
		</Button>
	</div>
</Card>
