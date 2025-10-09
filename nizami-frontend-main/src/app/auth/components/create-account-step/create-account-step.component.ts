import {Component, input, Input, OnInit, output, signal} from '@angular/core';
import {FormControl, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';
import {RouterLink} from '@angular/router';
import {InputComponent} from '../../../common/components/input/input.component';
import {ControlErrorsComponent} from '../../../common/components/errors/control-errors.component';
import {PasswordValidationErrorsComponent} from '../password-validation-errors/password-validation-errors.component';
import {ButtonComponent} from '../../../common/components/button/button.component';
import {UntilDestroy, untilDestroyed} from '@ngneat/until-destroy';
import {specialCharPattern} from '../../../constants';
import {TranslatePipe} from '@ngx-translate/core';

@UntilDestroy()
@Component({
  selector: 'app-create-account-step',
  imports: [
    RouterLink,
    InputComponent,
    ControlErrorsComponent,
    ReactiveFormsModule,
    PasswordValidationErrorsComponent,
    ButtonComponent,
    TranslatePipe
  ],
  templateUrl: './create-account-step.component.html',
  styleUrl: './create-account-step.component.scss'
})
export class CreateAccountStepComponent implements OnInit {
  isPasswordVisible = signal(false);
  form = new FormGroup({
    first_name: new FormControl(null, [Validators.required]),
    last_name: new FormControl(null, [Validators.required]),
    email: new FormControl(null, [Validators.required, Validators.email]),
    password: new FormControl(null, [Validators.required, Validators.minLength(8), Validators.pattern(specialCharPattern)]),
  });

  initial = input<any>();
  onSubmit = output<any>();
  onChange = output<any>();

  @Input()
  set disabled(value: boolean) {
    if (value) {
      this.form.disable();
    } else {
      this.form.enable();
    }
  }

  get passwordControl() {
    return this.form.controls.password;
  }

  ngOnInit() {
    this.form.patchValue(this.initial());

    this.form.valueChanges
      .pipe(untilDestroyed(this))
      .subscribe((v) => {
        this.onChange.emit(v);
      });
  }

  showPassword() {
    this.isPasswordVisible.set(!this.isPasswordVisible());
  }

  submit() {
    this.form.markAllAsTouched();

    if (this.form.invalid) {
      return;
    }

    this.onSubmit.emit(this.form.value);
  }
}
