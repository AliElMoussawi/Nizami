import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {environment} from '../../../environments/environment';
import {AuthService} from '../../auth/services/auth.service';
import {
  UserSubscription,
  CreateSubscriptionRequest,
  UpdateSubscriptionRequest,
  DataTableResponse
} from '../types/subscription.types';

// Export UserSubscriptionModel as an alias for UserSubscription
export type UserSubscriptionModel = UserSubscription;

@Injectable({
  providedIn: 'root'
})
export class SubscriptionsService {

  constructor(
    private http: HttpClient,
    private auth: AuthService,
  ) {
  }

  getSubscriptions(dataTablesParameters: any) {
    return this.http.post<DataTableResponse<UserSubscription>>(
      environment.apiUrl + '/v1/admin/subscriptions/get',
      dataTablesParameters,
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }

  createSubscription(data: CreateSubscriptionRequest) {
    return this.http.post<UserSubscription>(
      environment.apiUrl + '/v1/admin/subscriptions/',
      data,
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }

  loadSubscription(uuid: string) {
    return this.http.get<UserSubscription>(
      environment.apiUrl + '/v1/admin/subscriptions/' + uuid + '/get',
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }

  updateSubscription(uuid: string, data: UpdateSubscriptionRequest) {
    return this.http.put<UserSubscription>(
      environment.apiUrl + '/v1/admin/subscriptions/' + uuid + '/edit',
      data,
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }

  activateSubscription(uuid: string) {
    return this.http.post<{message: string; subscription: UserSubscription}>(
      environment.apiUrl + '/v1/admin/subscriptions/' + uuid + '/activate',
      {},
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }

  deactivateSubscription(uuid: string) {
    return this.http.post<{message: string; subscription: UserSubscription}>(
      environment.apiUrl + '/v1/admin/subscriptions/' + uuid + '/deactivate',
      {},
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }

}
