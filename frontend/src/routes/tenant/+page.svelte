<script lang="ts">
	import Tenant from '$lib/components/Tenant/Tenant.svelte';
	import { useUnityAuthContext } from '$lib/context/UnityAuthContext';

	const unityAuthContext = useUnityAuthContext();
	const user = unityAuthContext.user;
</script>

<h1>Tenants</h1>

{#if $user && $user.tenants}
	<ul>
		{#each $user.tenants as tenant}
			<li>
				<Tenant {tenant} />
			</li>
		{/each}
	</ul>
{/if}
