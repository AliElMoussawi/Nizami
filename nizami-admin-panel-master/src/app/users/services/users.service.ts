import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {environment} from '../../../environments/environment';
import {DataTableResponse} from '../../common/models/data-table.response';
import {UserModel} from '../../common/models/user.model';
import {AuthService} from '../../auth/services/auth.service';

@Injectable({
  providedIn: 'root'
})
export class UsersService {

  constructor(
    private http: HttpClient,
    private auth: AuthService,
  ) {
  }

  getUsers(dataTablesParameters: any) {
    return this.http.post<DataTableResponse<any>>(
      environment.apiUrl + '/v1/admin/users/get',
      dataTablesParameters,
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }

  createUser(data: any) {
    return this.http.post<any>(
      environment.apiUrl + '/v1/admin/users/',
      data,
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }

  loadUser(id: any) {
    return this.http.get<UserModel>(
      environment.apiUrl + '/v1/admin/users/' + id + '/get',
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }

  updateUser(id: any, value: any) {
    return this.http.put<any>(
      environment.apiUrl + '/v1/admin/users/' + id + '/edit',
      value,
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }

  updateUserPassword(id: any, value: any) {
    return this.http.put<any>(
      environment.apiUrl + '/v1/admin/users/' + id + '/edit-password',
      value,
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }

  deleteUser(id: any) {
    return this.http.delete<any>(
      environment.apiUrl + '/v1/admin/users/' + id,
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }

  changeStatus(id: any, value: any) {
    return this.http.put<any>(
      environment.apiUrl + '/v1/admin/users/' + id + '/update-status',
      value,
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }

  resetPassword(id: any, value: any) {
    return this.http.put<any>(
      environment.apiUrl + '/v1/admin/users/' + id + '/update-password',
      value,
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }
}
