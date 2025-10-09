import {Component, signal} from '@angular/core';
import {InputComponent} from '../../../common/components/input/input.component';
import {ButtonComponent} from '../../../common/components/button/button.component';
import {FormControl, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';
import {AuthService} from '../../services/auth.service';
import {catchError, EMPTY, finalize} from 'rxjs';
import {ActivatedRoute, Router} from '@angular/router';
import {ToastrService} from 'ngx-toastr';
import {UntilDestroy, untilDestroyed} from '@ngneat/until-destroy';
import {AuthCardComponent} from '../auth-card/auth-card.component';
import {specialCharPattern} from '../../../constants';
import {
  PasswordValidationErrorsComponent
} from '../../../users/components/password-validation-errors/password-validation-errors.component';
import {extractErrorFromResponse} from '../../../common/utils';

@UntilDestroy()
@Component({
  selector: 'app-reset-password-form',
  imports: [
    InputComponent,
    ButtonComponent,
    ReactiveFormsModule,
    AuthCardComponent,
    PasswordValidationErrorsComponent
  ],
  templateUrl: './reset-password-form.component.html',
  styleUrl: './reset-password-form.component.scss'
})
export class ResetPasswordFormComponent {
  isSubmitted = signal(false);

  form = new FormGroup({
    email: new FormControl('', [Validators.required, Validators.email]),
    password: new FormControl('', [Validators.required, Validators.minLength(8), Validators.pattern(specialCharPattern)]),
  });
  isPasswordVisible = signal(false);
  token = null;

  constructor(
    private auth: AuthService,
    private router: Router,
    private route: ActivatedRoute,
    private toastr: ToastrService,
  ) {
    this.token = this.route.snapshot.queryParams['token'] ?? null;

    if (!this.token) {
      this.toastr.error("Please request reset password first");
      this.router.navigateByUrl('/forgot-password');
    }
  }

  submit() {
    if (this.form.invalid) {
      return;
    }

    this.form.disable();
    this.auth
      .resetPassword({
        ...this.form.value,
        token: this.token,
      })
      .pipe(
        untilDestroyed(this),
        catchError((e) => {
          this.toastr.error(extractErrorFromResponse(e) ?? "The password is not updated, please try again!");

          return EMPTY;
        }),
        finalize(() => {
          this.form.enable();
        }),
      )
      .subscribe(() => {
        this.isSubmitted.set(true)
      });
  }

  continue() {
    this.router.navigateByUrl('/users');
  }

  showPassword() {
    this.isPasswordVisible.set(!this.isPasswordVisible());
  }
}
