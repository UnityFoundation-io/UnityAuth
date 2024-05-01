<script lang="ts">
	import SideBarMainContentLayout from '$lib/components/SideBarMainContentLayout/SideBarMainContentLayout.svelte';
</script>

<SideBarMainContentLayout>
	<slot slot="side-bar" />
	<div slot="main-content" class="relative flex h-full" id="main-content"></div>
</SideBarMainContentLayout>

<style>
	#main-content {
		background-color: hsl(var(--background));
	}
</style>
