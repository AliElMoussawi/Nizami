import { Component } from '@angular/core';
import {AuthTemplateComponent} from '../auth-template/auth-template.component';
import {LoginFormComponent} from '../login-form/login-form.component';

@Component({
  selector: 'app-login',
  imports: [
    AuthTemplateComponent,
    LoginFormComponent
  ],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss'
})
export class LoginComponent {

}
