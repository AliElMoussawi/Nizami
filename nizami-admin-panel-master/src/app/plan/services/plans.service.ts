import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {environment} from '../../../environments/environment';
import {AuthService} from '../../auth/services/auth.service';
import {DataTableResponse} from '../../common/models/data-table.response';
import {PlanModel} from '../../common/models/plan.model';

@Injectable({
  providedIn: 'root'
})
export class PlansService {

  constructor(
    private http: HttpClient,
    private auth: AuthService,
  ) {
  }

  list(dataTablesParameters: any) {
    return this.http.get<any>(
      environment.apiUrl + '/v1/admin/plans/',
      {
        params: dataTablesParameters,
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }

  create(payload: any) {
    return this.http.post<PlanModel>(
      environment.apiUrl + '/v1/admin/plans/create/',
      payload,
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }

  update(uuid: string, payload: Partial<PlanModel>) {
    return this.http.put<PlanModel>(
      environment.apiUrl + '/v1/admin/plans/' + uuid + '/',
      payload,
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }

  get(uuid: string) {
    // Use admin endpoint so admins can edit even deleted plans
    return this.http.get<PlanModel>(
      environment.apiUrl + '/v1/admin/plans/' + uuid + '/',
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }

  activate(uuid: string) {
    return this.http.post<{message: string}>(
      environment.apiUrl + '/v1/admin/plans/activate/',
      { uuid },
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }

  deactivate(uuid: string) {
    return this.http.post<{message: string}>(
      environment.apiUrl + '/v1/admin/plans/deactivate/',
      { uuid },
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }
}


