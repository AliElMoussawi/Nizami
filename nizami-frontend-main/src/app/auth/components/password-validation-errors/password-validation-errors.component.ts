import {Component, input} from '@angular/core';
import {FormControl} from '@angular/forms';
import {PasswordValidationErrorComponent} from '../password-validation-error/password-validation-error.component';
import {marker} from '@colsen1991/ngx-translate-extract-marker';

@Component({
  selector: 'app-password-validation-errors',
  imports: [
    PasswordValidationErrorComponent
  ],
  templateUrl: './password-validation-errors.component.html',
  styleUrl: './password-validation-errors.component.scss'
})
export class PasswordValidationErrorsComponent {
  control = input.required<FormControl>();
  validations = [
    {
      name: 'minlength',
      message: marker('Must be at least 8 characters.'),
    },
    {
      name: 'pattern',
      message: marker('Must contain one special character.'),
    },
  ];
}
