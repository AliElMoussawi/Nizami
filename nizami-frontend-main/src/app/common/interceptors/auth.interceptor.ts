import {Injectable} from "@angular/core";
import {HttpEvent, HttpHandler, HttpInterceptor, HttpRequest} from '@angular/common/http';
import {AuthService} from '../../auth/services/auth.service';
import {Router} from '@angular/router';
import {catchError, Observable} from 'rxjs';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  constructor(
    private authService: AuthService,
    private router: Router,
  ) {
  }

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Get the token from auth service
    const token = this.authService.getToken();

    // Clone the request and add the Authorization header if token exists
    let authReq = req;
    if (token && this.authService.isAuthenticated()) {
      authReq = req.clone({
        setHeaders: {
          Authorization: `Bearer ${token}`
        }
      });
    }

    return next.handle(authReq).pipe(
      catchError((err) => {
        if (err.status === 401) {  // Unauthorized error
          this.authService.logout();  // Log the user out
          this.router.navigate(['/login']);  // Redirect to login
        }
        throw err;
      })
    );
  }
}
