import type { AxiosInstance } from 'axios';
import { BaseObservable } from '../EventBus/EventBus';
import type { CompleteLoginResponse, UnityAuthServiceProps } from './shared';
import {
	CompleteLoginResponseSchema,
	UnityAuthLoginResponseSchema,
	UnityAuthServicePropsSchema
} from './shared';
import axios from 'axios';
import { browser } from '$app/environment';

export type UnityAuthEventMap = {
	login: CompleteLoginResponse;
	logout: void;
};

export type UnityAuthService = BaseObservable<UnityAuthEventMap> & {
	login(email: string, password: string): Promise<CompleteLoginResponse>;
	getLoginData(): CompleteLoginResponse | undefined;
	logout(): void;
};

export class UnityAuthServiceImpl
	extends BaseObservable<UnityAuthEventMap>
	implements UnityAuthService
{
	private loginDataKey: string = 'loginData';
	private axiosInstance: AxiosInstance;
	private loginData: CompleteLoginResponse | undefined;
	private constructor(props: UnityAuthServiceProps) {
		super();
		UnityAuthServicePropsSchema.parse(props);
		this.axiosInstance = axios.create({ baseURL: props.baseURL });

		this.loginData = this.retrieveLoginData();
		this.publish('logout', undefined);
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
}

export function unityAuthServiceFactory(props: UnityAuthServiceProps): UnityAuthService {
	return UnityAuthServiceImpl.create(props);
}
