import type { AxiosInstance } from 'axios';
import { BaseObservable } from '../EventBus/EventBus';
import type {
	CompleteLoginResponse,
	GetTenantUsersResponse,
	UnityAuthServiceProps
} from './shared';
import {
	CompleteLoginResponseSchema,
	GetTenantUsersResponseSchema,
	UnityAuthLoginResponseSchema,
	UnityAuthServicePropsSchema
} from './shared';
import axios from 'axios';
import { browser } from '$app/environment';
import { isTenantsSuccessResponse } from '../TenantsResolver/shared';
import type { TenantsResolver } from '../TenantsResolver/TenantsResolver';

export type UnityAuthEventMap = {
	login: CompleteLoginResponse;
	logout: void;
};

export type UnityAuthService = BaseObservable<UnityAuthEventMap> & {
	login(email: string, password: string): Promise<CompleteLoginResponse>;
	getLoginData(): CompleteLoginResponse | undefined;
	logout(): void;
	getTenantUsers(id: number): Promise<GetTenantUsersResponse>;
};

export class UnityAuthServiceImpl
	extends BaseObservable<UnityAuthEventMap>
	implements UnityAuthService
{
	private loginDataKey: string = 'loginData';
	private axiosInstance: AxiosInstance;
	private tenantsResolver: TenantsResolver;
	private loginData: CompleteLoginResponse | undefined;
	private constructor(props: UnityAuthServiceProps) {
		super();
		UnityAuthServicePropsSchema.parse(props);
		this.axiosInstance = axios.create({ baseURL: props.baseURL });

		this.loginData = this.retrieveLoginData();
		this.publish('logout', undefined);

		this.tenantsResolver = props.tenantsResolver;
	}

	public static create(props: UnityAuthServiceProps) {
		return new UnityAuthServiceImpl({ ...props });
	}

	getLoginData(): CompleteLoginResponse | undefined {
		return this.loginData;
	}

	async login(email: string, password: string): Promise<CompleteLoginResponse> {
		const res = await this.axiosInstance.post('/api/login', {
			username: email,
			password: password
		});

		const loginRes = UnityAuthLoginResponseSchema.parse(res.data);

		const completeLoginRes: CompleteLoginResponse = { ...loginRes };

		try {
			const tenantsRes = await this.tenantsResolver.getTenants(loginRes);
			if (!isTenantsSuccessResponse(tenantsRes)) {
				throw new Error(tenantsRes.errorMessage);
			}

			completeLoginRes.tenants = tenantsRes;
		} catch (e) {
			console.log(e); // ignore users that do not belong to a tenant
		}

		this.loginData = completeLoginRes;

		this.publish('login', completeLoginRes);
		if (browser) sessionStorage.setItem(this.loginDataKey, JSON.stringify(completeLoginRes));
		return completeLoginRes;
	}

	logout() {
		if (browser) sessionStorage.removeItem(this.loginDataKey);
		this.publish('logout', undefined);
	}

	private retrieveLoginData(): CompleteLoginResponse | undefined {
		if (browser) {
			const loginInfo = sessionStorage.getItem(this.loginDataKey);
			if (!loginInfo) {
				return;
			}
			return CompleteLoginResponseSchema.parse(JSON.parse(loginInfo));
		}
	}

	async getTenantUsers(id: number): Promise<GetTenantUsersResponse> {
		const res = await this.axiosInstance.post(`/api/tenants/${id}/users`);
		return GetTenantUsersResponseSchema.parse(res);
	}
}

export function unityAuthServiceFactory(props: UnityAuthServiceProps): UnityAuthService {
	return UnityAuthServiceImpl.create(props);
}
