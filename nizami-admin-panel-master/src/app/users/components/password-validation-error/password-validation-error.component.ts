import {Component, input} from '@angular/core';

@Component({
  selector: 'app-password-validation-error',
  imports: [],
  templateUrl: './password-validation-error.component.html',
  styleUrl: './password-validation-error.component.scss'
})
export class PasswordValidationErrorComponent {
  hasError = input<boolean>(false);
  validation = input.required<{ name: string; message: string }>();
}
