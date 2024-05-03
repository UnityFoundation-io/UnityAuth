<script lang="ts">
	import { Button, List } from 'stwui';
	import { goto } from '$app/navigation';

	export let tenants;
</script>

{#if tenants}
	<List divided={false}>
		{#each tenants as tenant}
			<List.Item class="m-2 rounded-md py-0">
				<Button class="flex w-full justify-start" on:click={() => goto(`/tenant/${tenant.id}`)}>
					{tenant.name}
				</Button>
			</List.Item>
		{/each}
	</List>
{/if}
