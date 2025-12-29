import { Component } from '@angular/core';
import {NgIcon} from '@ng-icons/core';
import {RouterLink} from '@angular/router';
import {ResetPasswordFormComponent} from '../reset-password-form/reset-password-form.component';
import {TranslatePipe} from '@ngx-translate/core';

@Component({
  selector: 'app-reset-password',
  imports: [
    NgIcon,
    RouterLink,
    ResetPasswordFormComponent,
    TranslatePipe
  ],
  templateUrl: './reset-password.component.html',
  styleUrl: './reset-password.component.scss'
})
export class ResetPasswordComponent {

}
