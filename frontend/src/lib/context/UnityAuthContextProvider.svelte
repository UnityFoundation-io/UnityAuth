<script lang="ts">
	import Alert from '$lib/components/Alert/Alert.svelte';
	import { createAlertStore } from './UnityAuthAlertStore';
	import { createUnityAuthContext, type UnityAuthContextProviderProps } from './UnityAuthContext';
	export let props: UnityAuthContextProviderProps;

	const alertStore = createAlertStore();
	const currentAlert = alertStore.currentAlert;
	const unityAuthContext = createUnityAuthContext({ ...props, ...alertStore });
</script>

<svelte:head></svelte:head>

<slot {unityAuthContext} />

{#if $currentAlert}
	<Alert
		on:close={() => alertStore.close()}
		type={$currentAlert.type}
		title={$currentAlert.title}
		description={$currentAlert.description}
	></Alert>
{/if}
