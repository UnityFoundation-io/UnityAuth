<script lang="ts">
	import { onMount } from 'svelte';
	import { useUnityAuthService } from '$lib/context/UnityAuthContext';
	import { page } from '$app/stores';
	import type { TenantUser } from '$lib/context/TenantUsersContext/TenantUsers';

	const unityAuthService = useUnityAuthService();

	let users: TenantUser;

	async function getTenantUserList() {
		users = await unityAuthService.getTenantUsers($page.params.tenant_id);
	}

	onMount(async () => {
		await getTenantUserList();
	});
</script>

<section class="h-full">
	{#if users}
		<ul>
			{#each users as user}
				<li>{user.email}</li>
			{/each}
		</ul>
	{/if}
</section>

<style>
	section {
		background-color: hsl(var(--background));
	}
</style>
