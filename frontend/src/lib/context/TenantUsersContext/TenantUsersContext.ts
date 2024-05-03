import type { UnityAuthService } from '$lib/services/UnityAuth/UnityAuth';
import { writable, type Readable } from 'svelte/store';
import type { TenantUser } from './TenantUsers';
import type { Maybe } from '$lib/utils/types';
import {
	ASYNC_IN_PROGRESS,
	asAsyncFailure,
	asAsyncSuccess,
	type AsyncResult
} from '$lib/services/http/http';
import { getContext, setContext } from 'svelte';
import type { GetTenantUsersResponse } from '$lib/services/UnityAuth/shared';
import { page } from '$app/stores';
import type { Page } from '@sveltejs/kit';

const key = Symbol();

export type TenantUsersContext = {
	selectedTenantUser: Readable<Maybe<TenantUser>>;
	tenantUsersResponse: Readable<AsyncResult<GetTenantUsersResponse>>;
};

export function createTenantUsersContext(
	unityAythService: UnityAuthService,
	page: Readable<Page<Record<string, string>, string | null>>
) {
	const selectedTenantUser = writable<Maybe<TenantUser>>();
	const tenantUsersResponse = writable<AsyncResult<GetTenantUsersResponse>>(ASYNC_IN_PROGRESS);

	async function handleTenantPage() {
		try {
			const id = 1; // TODO
			const res = await unityAythService.getTenantUsers(id);

			tenantUsersResponse.set(asAsyncSuccess(res));
		} catch (error) {
			tenantUsersResponse.set(asAsyncFailure(error));
		}
	}

	page.subscribe(async (page: Page<Record<string, string>, string | null>) => {
		if (page.route.id?.includes('tenants')) {
			await handleTenantPage();
		}
	});

	const ctx: TenantUsersContext = {
		selectedTenantUser,
		tenantUsersResponse
	};

	setContext(key, ctx);

	return ctx;
}

export function useTenantUsersContext(): TenantUsersContext {
	return getContext<TenantUsersContext>(key);
}

export function useSelectedServiceRequestStore(): TenantUsersContext['selectedTenantUser'] {
	return useTenantUsersContext().selectedTenantUser;
}

export function useServiceRequestsResponseStore(): TenantUsersContext['tenantUsersResponse'] {
	return useTenantUsersContext().tenantUsersResponse;
}
