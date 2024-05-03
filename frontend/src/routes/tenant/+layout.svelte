<script lang="ts">
	import SideBarMainContentLayout from '$lib/components/SideBarMainContentLayout/SideBarMainContentLayout.svelte';
	import { useUnityAuthContext } from '$lib/context/UnityAuthContext';
	import Tenants from '$lib/components/Tenants/Tenants.svelte';

	const unityAuthContext = useUnityAuthContext();
	const user = unityAuthContext.user;
</script>

<SideBarMainContentLayout>
	<div slot="side-bar" id="side-bar">
		{#if $user && $user.tenants}
			<Tenants tenants={$user.tenants} />
		{/if}
	</div>

	<slot slot="main-content" id="main-content" class="relative flex h-full" />
</SideBarMainContentLayout>

<style>
	#side-bar {
		background-color: hsl(var(--secondary));
	}

	#main-content {
		background-color: hsl(var(--background));
	}
</style>
