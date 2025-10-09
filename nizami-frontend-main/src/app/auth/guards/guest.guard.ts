import {AuthService} from '../services/auth.service';
import {CanActivate, CanActivateChild, Router} from '@angular/router';
import {Injectable} from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class GuestGuard implements CanActivate, CanActivateChild {
  constructor(private authService: AuthService, private router: Router) {
  }

  canActivateChild() {
    return this.canActivate();
  }

  canActivate(): boolean {
    if (!this.authService.isAuthenticated()) {
      return true;
    }

    this.router.navigate(['/chat']);
    return false;
  }
}
