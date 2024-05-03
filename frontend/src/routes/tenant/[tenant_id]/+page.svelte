<script lang="ts">
	import { onMount } from 'svelte';
	import { useUnityAuthService } from '$lib/context/UnityAuthContext';
	import { page } from '$app/stores';
	import { type TenantUser } from '$lib/context/TenantUsersContext/TenantUsers';
	import TenantUsersList from '$lib/components/TenantUsersList/TenantUsersList.svelte';

	const unityAuthService = useUnityAuthService();

	let tenantUsers: TenantUser[];

	async function getTenantUserList() {
		tenantUsers = await unityAuthService.getTenantUsers($page.params.tenant_id);
	}

	onMount(async () => {
		await getTenantUserList();
	});
</script>

<section class="h-full w-full">
	{#if tenantUsers}
		<div class="flex h-full items-center justify-center">
			<TenantUsersList {tenantUsers} />
		</div>
	{/if}
</section>

<style>
	section {
		background-color: hsl(var(--background));
	}
</style>
