import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {environment} from '../../../environments/environment';
import {AuthService} from '../../auth/services/auth.service';
import {Plan, PaginatedResponse} from '../../subscriptions/types/subscription.types';

@Injectable({
  providedIn: 'root'
})
export class PlansService {

  constructor(
    private http: HttpClient,
    private auth: AuthService,
  ) {
  }

  getPlans() {
    return this.http.get<PaginatedResponse<Plan>>(
      environment.apiUrl + '/v1/admin/plans/',
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }
}
