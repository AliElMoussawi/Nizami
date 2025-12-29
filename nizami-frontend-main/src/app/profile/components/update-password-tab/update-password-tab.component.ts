import {Component, output, signal} from '@angular/core';
import {
  AbstractControl,
  FormControl,
  FormGroup,
  ReactiveFormsModule,
  ValidationErrors,
  Validators
} from "@angular/forms";
import {InputComponent} from '../../../common/components/input/input.component';
import {ControlErrorsComponent} from '../../../common/components/errors/control-errors.component';
import {
  PasswordValidationErrorsComponent
} from '../../../auth/components/password-validation-errors/password-validation-errors.component';
import {ButtonComponent} from '../../../common/components/button/button.component';
import {OutlineButtonComponent} from '../../../common/components/outline-button/outline-button.component';
import {ErrorComponent} from '../../../common/components/error/error.component';
import {UntilDestroy, untilDestroyed} from '@ngneat/until-destroy';
import {catchError, EMPTY, finalize} from 'rxjs';
import {AuthService} from '../../../auth/services/auth.service';
import {ToastrService} from 'ngx-toastr';
import {specialCharPattern} from '../../../constants';
import {extractErrorFromResponse} from '../../../common/utils';
import {TranslatePipe, TranslateService} from '@ngx-translate/core';
import {marker} from '@colsen1991/ngx-translate-extract-marker';

@UntilDestroy()
@Component({
  selector: 'app-update-password-tab',
  imports: [
    ReactiveFormsModule,
    InputComponent,
    ControlErrorsComponent,
    PasswordValidationErrorsComponent,
    ButtonComponent,
    OutlineButtonComponent,
    ErrorComponent,
    TranslatePipe,
  ],
  templateUrl: './update-password-tab.component.html',
  styleUrl: './update-password-tab.component.scss'
})
export class UpdatePasswordTabComponent {
  form = new FormGroup({
    old_password: new FormControl(null, [Validators.required]),
    new_password: new FormControl(null, [Validators.required, Validators.minLength(8), Validators.pattern(specialCharPattern)]),
    confirm_password: new FormControl(null, [Validators.required]),
  }, {
    validators: this.passwordMatchValidator,
  });

  onCancel = output();
  isSaving = signal(false);

  constructor(
    private auth: AuthService,
    private toastr: ToastrService,
    private translate: TranslateService,
  ) {
  }

  save() {
    if (this.form.invalid) {
      return;
    }

    this.form.disable();
    this.isSaving.set(true);

    this
      .auth
      .updatePassword(this.form.value)
      .pipe(
        untilDestroyed(this),
        catchError((e) => {
            this.toastr.error(extractErrorFromResponse(e) ?? this.translate.instant(marker('errors.something_went_wrong')));

            return EMPTY;
          }
        ),
        finalize(() => {
          this.isSaving.set(false);
          this.form.enable();
        }),
      )
      .subscribe(() => {
        this.toastr.success(this.translate.instant(marker('success.password_saved')));

        this.form.reset();
      });
  }

  // Custom Validator for matching passwords
  passwordMatchValidator(control: AbstractControl): ValidationErrors | null {
    const password = control.get('new_password')?.value;
    const confirmPassword = control.get('confirm_password')?.value;

    if (!password || !confirmPassword) {
      return null; // If fields are empty, don't show an error
    }

    return password === confirmPassword ? null : {mismatch: true};
  }

}
