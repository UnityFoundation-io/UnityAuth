import { getContext, setContext } from 'svelte';
import { type UnityAuthService, unityAuthServiceFactory } from '$lib/services/UnityAuth/UnityAuth';
import { type Mode } from '$lib/services/mode/mode';
import { writable, type Readable, type Writable } from 'svelte/store';
import type { UnityAuthAlert } from './UnityAuthAlertStore';
import {
	checkHasMessage,
	extractFirstErrorMessage,
	isHateoasErrorResponse,
	isUnityAuthServerErrorResponse
} from '$lib/services/ServerErrors/ServerErrors';
import { isAxiosError } from 'axios';
import type { CompleteLoginResponse, UnityAuthServiceProps } from '$lib/services/UnityAuth/shared';
import { TenantsResolverImpl } from '$lib/services/TenantsResolver/TenantsResolver';

const unityAuthCtxKey = Symbol();

export type UserInfo = CompleteLoginResponse | undefined;

export type UnityAuthContext = {
	unityAuthService: UnityAuthService;
	mode: Mode;
	user: Readable<UserInfo>;
	alertError: (unknown: unknown) => void;
} & UnityAuthAlert;

export type UnityAuthContextProviderProps = {
	unityAuthServiceProps: Omit<UnityAuthServiceProps, 'tenantsResolver'>;
	mode: Mode;
};

export function createUnityAuthContext(props: UnityAuthContextProviderProps & UnityAuthAlert) {
	const tenantsResolver = new TenantsResolverImpl({
		libreBaseUrl: props.unityAuthServiceProps.baseURL
	});

	const unityAuthService = unityAuthServiceFactory({
		tenantsResolver,
		...props.unityAuthServiceProps
	});

	unityAuthService.setAuthInfo(unityAuthService.getLoginData());
	const user: Writable<UserInfo> = writable(unityAuthService.getLoginData());
	unityAuthService.subscribe('login', (args) => user.set(args));
	unityAuthService.subscribe('logout', () => user.set(undefined));
	unityAuthService.subscribe('login', (args) => unityAuthService.setAuthInfo(args));
	unityAuthService.subscribe('logout', () => unityAuthService.setAuthInfo(undefined));

	function alertError(unknown: unknown) {
		console.error(unknown);
		if (isAxiosError(unknown)) {
			if (isUnityAuthServerErrorResponse(unknown.response?.data)) {
				const libre311ServerError = unknown.response.data;
				props.alert({
					type: 'error',
					title: libre311ServerError.message,
					description: `${extractFirstErrorMessage(libre311ServerError)} \n logref: ${libre311ServerError.logref}`
				});
				return;
			} else if (isHateoasErrorResponse(unknown.response?.data)) {
				const hateoasErrorResponse = unknown.response.data;
				props.alert({
					type: 'error',
					title: hateoasErrorResponse.message,
					description: extractFirstErrorMessage(hateoasErrorResponse)
				});
				return;
			}
		}

		if (checkHasMessage(unknown)) {
			props.alert({
				type: 'error',
				title: 'Error',
				description: unknown.message
			});
		} else {
			props.alert({
				type: 'error',
				title: 'Something unexpected happened',
				description: 'The complete error has been logged in the console'
			});
		}
	}

	const ctx: UnityAuthContext = {
		...props,
		unityAuthService,
		user,
		alertError
	};
	setContext(unityAuthCtxKey, ctx);
	return ctx;
}

export function useUnityAuthContext(): UnityAuthContext {
	return getContext<UnityAuthContext>(unityAuthCtxKey);
}

export function useUnityAuthService(): UnityAuthService {
	return getContext<UnityAuthContext>(unityAuthCtxKey).unityAuthService;
}
