<script lang="ts">
	import { type TableColumn } from 'stwui/types';
	import { Card, Table } from 'stwui';
	export let tenantUsers;

	let orderBy: string;
	let order: 'asc' | 'desc';

	const columns: TableColumn[] = [
		{
			column: 'user_name',
			label: 'User Name',
			placement: 'left',
			class: 'w-[50%]'
		},
		{
			column: 'email',
			label: 'Email',
			placement: 'left',
			class: 'w-[50%]'
		}
	];
</script>

<Card bordered={false} class="w-[90%]">
	<Card.Content slot="content" class="p-0 sm:p-0">
		<Table class="h-full overflow-hidden rounded-md" {columns}>
			<Table.Header slot="header" {order} {orderBy} />
			<Table.Body slot="body">
				{#each tenantUsers as user}
					<Table.Body.Row id={user.id}>
						<Table.Body.Row.Cell column={0}
							>{user.firstName + ' ' + user.lastName}</Table.Body.Row.Cell
						>
						<Table.Body.Row.Cell column={1}>{user.email}</Table.Body.Row.Cell>
					</Table.Body.Row>
				{/each}
			</Table.Body>
		</Table>
	</Card.Content>
</Card>
