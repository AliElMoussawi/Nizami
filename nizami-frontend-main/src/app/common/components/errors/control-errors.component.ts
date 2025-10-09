import {Component, input, viewChildren} from '@angular/core';
import {ErrorComponent} from '../error/error.component';
import {FormControl} from '@angular/forms';
import {TranslatePipe} from '@ngx-translate/core';

@Component({
  selector: 'app-control-errors',
  imports: [
    ErrorComponent,
    TranslatePipe
  ],
  templateUrl: './control-errors.component.html',
  styleUrl: './control-errors.component.scss'
})
export class ControlErrorsComponent {
  control = input.required<FormControl>();
  errors = viewChildren<ErrorComponent>(ErrorComponent);

  get hasErrors() {
    return this.errors().length > 0;
  }
}
