import {Component, Inject} from '@angular/core';
import {DIALOG_DATA, DialogRef} from '@angular/cdk/dialog';
import {UserModel} from '../../../common/models/user.model';
import {ToastrService} from 'ngx-toastr';
import {UsersService} from '../../services/users.service';
import {
  AbstractControl,
  FormControl,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
  ValidationErrors,
  Validators
} from '@angular/forms';
import {InputComponent} from '../../../common/components/input/input.component';
import {PasswordValidationErrorsComponent} from '../password-validation-errors/password-validation-errors.component';
import {UntilDestroy, untilDestroyed} from '@ngneat/until-destroy';
import {catchError, EMPTY, take} from 'rxjs';
import {ControlErrorsComponent} from '../../../common/components/errors/control-errors.component';
import {ErrorComponent} from '../../../common/components/error/error.component';
import {ButtonComponent} from '../../../common/components/button/button.component';
import {OutlineButtonComponent} from '../../../common/components/outline-button/outline-button.component';
import {specialCharPattern} from '../../../constants';
import {extractErrorFromResponse} from '../../../common/utils';

@UntilDestroy()
@Component({
  selector: 'app-reset-password-dialog',
  imports: [
    ReactiveFormsModule,
    InputComponent,
    PasswordValidationErrorsComponent,
    ControlErrorsComponent,
    ErrorComponent,
    FormsModule,
    ButtonComponent,
    OutlineButtonComponent
  ],
  templateUrl: './reset-password-dialog.component.html',
  styleUrl: './reset-password-dialog.component.scss'
})
export class ResetPasswordDialogComponent {
  form = new FormGroup({
    new_password: new FormControl(null, [Validators.required, Validators.minLength(8), Validators.pattern(specialCharPattern)]),
    confirm_password: new FormControl(null, [Validators.required]),
  }, {
    validators: this.passwordMatchValidator,
  });

  constructor(
    @Inject(DialogRef) public dialogRef: DialogRef<any>,
    @Inject(DIALOG_DATA) public data: any,
    private toastr: ToastrService,
    private userService: UsersService,
  ) {
  }

  get user(): UserModel {
    return this.data.user;
  }

  close() {
    this.dialogRef.close(false);
  }

  confirm() {
    this.dialogRef.close(true);
  }

  submit() {
    if (this.form.invalid) {
      return;
    }

    this.form.disable();

    this.userService
      .resetPassword(this.user.id, this.form.value)
      .pipe(
        take(1),
        untilDestroyed(this),
        catchError((e) => {
          this.toastr.error(extractErrorFromResponse(e) ?? "Failed updating the password!");
          this.form.enable();
          return EMPTY;
        }),
      )
      .subscribe(() => {
        this.close();
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
