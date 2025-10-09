import {Routes} from '@angular/router';
import {ChatComponent} from './chat/components/chat/chat.component';
import {LoginComponent} from './auth/components/login/login.component';
import {AuthenticatedGuard} from './auth/guards/authenticated.guard';
import {GuestGuard} from './auth/guards/guest.guard';
import {SignupComponent} from './auth/components/signup/signup.component';
import {ForgotPasswordComponent} from './auth/components/forgot-password/forgot-password.component';
import {ResetPasswordComponent} from './auth/components/reset-password/reset-password.component';
import {
  ProfileSettingsMobileComponent
} from './profile/components/profile-settings-mobile/profile-settings-mobile.component';

export const routes: Routes = [
  {
    path: 'login',
    component: LoginComponent,
    canActivate: [GuestGuard],
  },
  {
    path: 'sign-up',
    component: SignupComponent,
    canActivate: [GuestGuard],
  },
  {
    path: 'forgot-password',
    component: ForgotPasswordComponent,
    canActivate: [GuestGuard],
  },
  {
    path: 'reset-password',
    component: ResetPasswordComponent,
    canActivate: [GuestGuard],
  },
  {
    path: 'chat',
    redirectTo: 'chat/',
    pathMatch: 'full',
  },
  {
    path: 'chat/:id',
    component: ChatComponent,
    canActivate: [AuthenticatedGuard],
  },
  {
    path: 'profile-settings',
    component: ProfileSettingsMobileComponent,
    canActivate: [AuthenticatedGuard],
  },
  {
    path: '**',
    redirectTo: 'login',
  },
];
