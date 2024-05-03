<script lang="ts">
	import { page } from '$app/stores';
	import { useUnityAuthService } from '$lib/context/UnityAuthContext';
	import { createTenantUsersContext, type TenantUsersContext } from './TenantUsersContext';
	import { type UnityAuthService } from '$lib/services/UnityAuth/UnityAuth';

	let unityAuthService: UnityAuthService;
	let tenantUsersContext: TenantUsersContext;

	unityAuthService = useUnityAuthService();
	tenantUsersContext = createTenantUsersContext(unityAuthService, page);
</script>

<slot {tenantUsersContext} />
