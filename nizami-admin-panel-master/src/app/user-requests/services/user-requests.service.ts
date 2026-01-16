import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Observable} from 'rxjs';
import {map} from 'rxjs/operators';
import {environment} from '../../../environments/environment';
import {AuthService} from '../../auth/services/auth.service';

export interface UserRequest {
  id: number;
  user: number;
  user_email: string;
  user_phone: string | null;
  chat: number;
  chat_title: string;
  chat_summary: string;
  status: 'new' | 'in_progress' | 'closed';
  created_at_ts: string;
  in_progress_ts: string | null;
  closed_at_ts: string | null;
}

interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

@Injectable({
  providedIn: 'root',
})
export class UserRequestsService {
  constructor(
    private http: HttpClient,
    private auth: AuthService,
  ) {
  }

  getUserRequests(): Observable<UserRequest[]> {
    return this.http.get<PaginatedResponse<UserRequest>>(
      environment.apiUrl + '/v1/user-requests/admin/',
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    ).pipe(
      map((response) => response.results || [])
    );
  }

  updateUserRequestStatus(id: number, status: 'new' | 'in_progress' | 'closed'): Observable<UserRequest> {
    return this.http.patch<UserRequest>(
      environment.apiUrl + `/v1/user-requests/admin/${id}/`,
      {status},
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      },
    );
  }
}
