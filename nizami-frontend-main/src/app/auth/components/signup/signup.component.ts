import {Component} from '@angular/core';
import {AuthTemplateComponent} from '../auth-template/auth-template.component';
import {SignupFormComponent} from '../signup-form/signup-form.component';
import {UntilDestroy, untilDestroyed} from '@ngneat/until-destroy';
import {take} from 'rxjs';

@UntilDestroy()
@Component({
  selector: 'app-signup',
  imports: [
    AuthTemplateComponent,
    SignupFormComponent
  ],
  templateUrl: './signup.component.html',
  styleUrl: './signup.component.scss'
})
export class SignupComponent {
  constructor() {
  }
}
