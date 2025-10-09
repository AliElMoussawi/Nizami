import { Component } from '@angular/core';
import {ForgotPasswordFormComponent} from '../forgot-password-form/forgot-password-form.component';
import {NgIcon} from '@ng-icons/core';
import {RouterLink} from '@angular/router';

@Component({
  selector: 'app-forgot-password',
  imports: [
    ForgotPasswordFormComponent,
    NgIcon,
    RouterLink
  ],
  templateUrl: './forgot-password.component.html',
  styleUrl: './forgot-password.component.scss'
})
export class ForgotPasswordComponent {

}
