<script lang="ts">
	import { Avatar, Dropdown } from 'stwui';
	import { useUnityAuthContext } from '$lib/context/UnityAuthContext';
	import { goto } from '$app/navigation';

	const unityAuthService = useUnityAuthContext().unityAuthService;
	const user = undefined; // unityAuthService.user; 	//	TODO

	let isUserDropdownVisible: boolean = false;

	function toggleDropdown() {
		isUserDropdownVisible = !isUserDropdownVisible;
	}

	function logout() {
		isUserDropdownVisible = false;
		unityAuthService.logout();
		goto('/');
	}
</script>

<Dropdown bind:visible={isUserDropdownVisible}>
	<button slot="trigger" on:click={toggleDropdown}>
		<!-- <Avatar initials={$user?.username.charAt(0).toUpperCase()} /> -->
		<Avatar initials={user} />
	</button>
	<Dropdown.Items slot="items">
		<Dropdown.Items.Item on:click={logout} label="Logout"></Dropdown.Items.Item>
	</Dropdown.Items>
</Dropdown>
