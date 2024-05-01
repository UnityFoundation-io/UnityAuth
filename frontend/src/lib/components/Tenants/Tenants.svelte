<script lang="ts">
	import { Button, List } from 'stwui';

	export let tenants;
</script>

{#if tenants}
	<div class="h-full">
		<List divided={false}>
			{#each tenants as tenant}
				<List.Item class="m-2 rounded-md py-0">
					<Button class="flex w-full justify-start" on:click={() => alert('TODO')}>
						{tenant.name}
					</Button>
				</List.Item>
			{/each}
		</List>
	</div>
{/if}
