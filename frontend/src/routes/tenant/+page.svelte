<script lang="ts">
	import { useUnityAuthContext } from '$lib/context/UnityAuthContext';
	import Tenants from '$lib/components/Tenants/Tenants.svelte';

	const unityAuthContext = useUnityAuthContext();
	const user = unityAuthContext.user;

	function selectTenant(e: CustomEvent) {
		console.log(e.detail);
	}
</script>

{#if $user && $user.tenants}
	<Tenants tenants={$user.tenants} on:selectTenant={selectTenant} />
{/if}
