<script lang="ts">
	import { createInput, emailValidator } from '$lib/utils/validation';
	import { useUnityAuthService } from '$lib/context/UnityAuthContext';
	import { goto } from '$app/navigation';
	import { checkHasMessage, isHateoasErrorResponse } from '$lib/services/ServerErrors/ServerErrors';
	import { isAxiosError } from 'axios';
	import Login from '$lib/components/Login/Login.svelte';
	import type { EventDispatchTypeMap } from '$lib/components/Login/login';

	const authService = useUnityAuthService();

	let emailInput = createInput('');
	let passwordInput = createInput('');
	let errorMessage: string | undefined;

	function handleChange(e: CustomEvent<EventDispatchTypeMap['inputChange']>) {
		if (e.detail.type == 'email') {
			emailInput.value = e.detail.value;
			emailInput = emailInput;
		} else {
			passwordInput.value = e.detail.value;
			passwordInput = passwordInput;
		}
	}

	async function login() {
		emailInput = emailValidator(emailInput);

		if (emailInput.value && passwordInput.value) {
			try {
				await authService.login(emailInput.value, passwordInput.value);
				goto('/tenant');
			} catch (error: unknown) {
				if (isAxiosError(error) && isHateoasErrorResponse(error.response?.data)) {
					const hateoasError = error.response.data;
					errorMessage = hateoasError.message;
				} else if (checkHasMessage(error)) {
					errorMessage = error.message;
				} else {
					errorMessage = new String(error).toString();
				}
			}
		}
	}
</script>

<div
	class="flex h-full w-full items-center justify-center"
	style="background-color: hsl(var(--primary));"
>
	<Login
		{emailInput}
		{passwordInput}
		{errorMessage}
		on:inputChange={handleChange}
		on:login={login}
	/>
</div>
