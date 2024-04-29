<script lang="ts">
	import '../app.pcss';
	import {
		asAsyncFailure,
		asAsyncSuccess,
		ASYNC_IN_PROGRESS,
		type AsyncResult
	} from '$lib/services/http/http';
	import { type UnityAuthContextProviderProps } from '$lib/context/UnityAuthContext';
	import UnityAuthContextProvider from '$lib/context/UnityAuthContextProvider.svelte';
	import { getModeFromEnv, type Mode } from '$lib/services/mode/mode';
	import User from '$lib/components/User/User.svelte';

	let contextProviderProps: AsyncResult<UnityAuthContextProviderProps> = ASYNC_IN_PROGRESS;

	async function initLibre311ContextProps() {
		try {
			const mode: Mode = getModeFromEnv(import.meta.env);
			const unityAuthBaseURL = String(import.meta.env.VITE_BACKEND_URL ?? '') || '/api';

			const ctxProps: UnityAuthContextProviderProps = {
				mode: mode,
				unityAuthServiceProps: { baseURL: unityAuthBaseURL }
			};

			console.log({ ctxProps });

			contextProviderProps = asAsyncSuccess(ctxProps);
		} catch (error) {
			console.error(error);
			contextProviderProps = asAsyncFailure(error);
		}
	}

	initLibre311ContextProps();
</script>

{#if contextProviderProps.type == 'success'}
	<UnityAuthContextProvider props={contextProviderProps.value}>
		<header class="flex items-center justify-center">
			<div class="flex gap-4">
				<h1>{'Admin'}</h1>
			</div>

			<User />
		</header>
		<main>
			<slot />
		</main>
	</UnityAuthContextProvider>
{:else if contextProviderProps.type == 'inProgress'}
	<!-- <SplashLoading /> -->
{:else}
	<!-- <SomethingWentWrong /> -->
{/if}

<style>
	:global(:root) {
		--header-height: 4rem;
	}
	header {
		height: var(--header-height);
		background-color: hsl(var(--primary));
		color: hsl(var(--primary-content));
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0 1rem;
	}
	main {
		height: calc(100dvh - var(--header-height));
	}
	h1 {
		font-size: clamp(1.5rem, -0.875rem + 8.333333vw, 2.5rem);
	}
</style>
