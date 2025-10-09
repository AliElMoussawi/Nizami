import {Injectable} from "@angular/core";
import {HttpEvent, HttpHandler, HttpInterceptor, HttpRequest} from '@angular/common/http';
import {catchError, Observable} from 'rxjs';
import {ToastrService} from 'ngx-toastr';
import {Router} from '@angular/router';

@Injectable()
export class ErrorInterceptor implements HttpInterceptor {
  constructor(
    private toastr: ToastrService,
    private router: Router,
  ) {
  }

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    return next.handle(req);
  }

  private handleAutoRefresh(err: any) {
    this.router.navigateByUrl('/chat');
    this.toastr.error(err.error.message ?? "Something went wrong, refreshing now!");
    setTimeout(() => {
      window.location.reload();
    }, 3000);
  }
}
