import axios from 'axios';
import type { UnityAuthLoginResponse } from '../UnityAuth/shared';
import { TenantsResponseSchema, type TenantsResponse } from './shared';

export type TenantsResolver = {
	getTenants(loginRes: UnityAuthLoginResponse): Promise<TenantsResponse>;
};

export class TenantsResolverImpl implements TenantsResolver {
	constructor(private props: { libreBaseUrl: string }) {}

	async getTenants(loginRes: UnityAuthLoginResponse): Promise<TenantsResponse> {
		const res = await axios.get<unknown>(this.props.libreBaseUrl + `/tenants`, {
			headers: {
				Authorization: `Bearer ${loginRes.access_token}`
			}
		});
		return TenantsResponseSchema.parse(res.data);
	}
}
