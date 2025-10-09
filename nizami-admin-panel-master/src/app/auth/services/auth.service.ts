import {Injectable, signal} from '@angular/core';
import {environment} from '../../../environments/environment';
import {HttpClient, HttpErrorResponse} from '@angular/common/http';
import {LoginResponse} from '../models/login.response';
import {catchError, EMPTY, map} from 'rxjs';
import {Router} from '@angular/router';
import {UserModel} from '../../common/models/user.model';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  user = signal<UserModel | null>(null);
  token = signal<string | null>(null);
  isAuthenticated = signal<boolean>(this.hasToken());
  private authTokenKey = 'authToken'; // Key for storing token

  constructor(
    private http: HttpClient,
    private router: Router,
  ) {
  }

  login(data: any) {
    return this.http.post<LoginResponse>(
      environment.apiUrl + '/v1/auth/login', data
    ).pipe(
      map((response) => {
        let remember_me = data.remember_me ?? false;

        const token = response.access_token;
        if (token) {
          if (response.user.role != 'admin') {
            throw "Invalid User";
          }

          this.storeToken(token, remember_me);
          this.isAuthenticated.set(true);
          this.user.set(response.user);
        }

        return response;
      }),
    );
  }

  logout(): void {
    this.clearToken();

    this.router.navigate(['/login']);
  }

  loadToken() {
    this.token.set(localStorage.getItem(this.authTokenKey) || sessionStorage.getItem(this.authTokenKey));
    this.isAuthenticated.set(this.hasToken());
  }

  getToken(): string | null {
    return this.token();
  }

  loadProfile() {
    return this.http.get<UserModel>(
      environment.apiUrl + '/v1/auth/profile',
      {
        headers: {
          'Authorization': 'Bearer ' + this.getToken()!,
        },
      },
    ).pipe(
      map((response) => {
        if (response.role != 'admin') {
          throw "Invalid User";
        }

        this.user.set(response);
      }),
      catchError((e, c) => {
        if (e instanceof HttpErrorResponse && e.status === 401) {
          this.clearToken();
          this.router.navigateByUrl('/');
          return EMPTY;
        }

        return e;
      }),
    );
  }

  signup(data: any) {
    return this.http.post<LoginResponse>(
      environment.apiUrl + '/v1/auth/sign-up', data
    ).pipe(
      map((response) => {
        const token = response.access_token;
        if (token) {
          this.storeToken(token);
          this.isAuthenticated.set(true);
          this.user.set(response.user);
        }
      }),
    );
  }

  forgotPassword(data: any) {
    return this.http.post<any>(
      environment.apiUrl + '/v1/auth/forgot-password', data
    );
  }

  resetPassword(data: any) {
    return this.http.post<LoginResponse>(
      environment.apiUrl + '/v1/auth/reset-password', data
    )
      .pipe(
        map((response) => {
          const token = response.access_token;
          if (token) {
            if (response.user.role != 'admin') {
              throw "Invalid User";
            }

            this.storeToken(token);
            this.isAuthenticated.set(true);
            this.user.set(response.user);
          }
        }),
      );
  }

  private clearToken() {
    localStorage.removeItem(this.authTokenKey);
    sessionStorage.removeItem(this.authTokenKey);
    this.isAuthenticated.set(false);
  }

  private hasToken(): boolean {
    return !!this.token();
  }

  private storeToken(token: string, remember_me = true): void {
    if (remember_me) {
      localStorage.setItem(this.authTokenKey, token);
    } else {
      sessionStorage.setItem(this.authTokenKey, token);
    }

    this.token.set(token);
  }
}
