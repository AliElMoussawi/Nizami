import {Injectable} from "@angular/core";
import {HttpEvent, HttpHandler, HttpInterceptor, HttpRequest} from '@angular/common/http';
import {AuthService} from '../../auth/services/auth.service';
import {Router} from '@angular/router';
import {catchError, Observable} from 'rxjs';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  constructor(private authService: AuthService, private router: Router) {
  }

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    if (!this.authService.isAuthenticated()) {
      return next.handle(req);
    }

    return next.handle(req).pipe(
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
