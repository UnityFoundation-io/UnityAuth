<script lang="ts">
	import { Button, List } from 'stwui';
	import { createEventDispatcher } from 'svelte';

	const dispatch = createEventDispatcher();

	export let tenants;
</script>

{#if tenants}
	<div class="h-full">
		<List divided={false}>
			{#each tenants as tenant}
				<List.Item class="m-2 rounded-md py-0">
					<Button
						class="flex w-full justify-start"
						on:click={() => dispatch('selectTenant', tenant)}
					>
						{tenant.name}
					</Button>
				</List.Item>
			{/each}
		</List>
	</div>
{/if}
