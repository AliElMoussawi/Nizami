import {Component, input} from '@angular/core';
import {TranslatePipe} from '@ngx-translate/core';

@Component({
  selector: 'app-password-validation-error',
  imports: [
    TranslatePipe
  ],
  templateUrl: './password-validation-error.component.html',
  styleUrl: './password-validation-error.component.scss'
})
export class PasswordValidationErrorComponent {
  hasError = input<boolean>(false);
  validation = input.required<{ name: string; message: string }>();
}
