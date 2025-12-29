import {Component, signal} from '@angular/core';
import {InputComponent} from '../../../common/components/input/input.component';
import {ButtonComponent} from '../../../common/components/button/button.component';
import {FormControl, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';
import {AuthService} from '../../services/auth.service';
import {catchError, EMPTY, finalize} from 'rxjs';
import {NgIcon} from '@ng-icons/core';
import {ActivatedRoute, Router} from '@angular/router';
import {ToastrService} from 'ngx-toastr';
import {UntilDestroy, untilDestroyed} from '@ngneat/until-destroy';
import {PasswordValidationErrorsComponent} from '../password-validation-errors/password-validation-errors.component';
import {ControlErrorsComponent} from '../../../common/components/errors/control-errors.component';
import {specialCharPattern} from '../../../constants';
import {extractErrorFromResponse} from '../../../common/utils';
import {TranslatePipe, TranslateService} from '@ngx-translate/core';
import {marker} from '@colsen1991/ngx-translate-extract-marker';

@UntilDestroy()
@Component({
  selector: 'app-reset-password-form',
  imports: [
    InputComponent,
    ButtonComponent,
    ReactiveFormsModule,
    NgIcon,
    PasswordValidationErrorsComponent,
    ControlErrorsComponent,
    TranslatePipe
  ],
  templateUrl: './reset-password-form.component.html',
  styleUrl: './reset-password-form.component.scss'
})
export class ResetPasswordFormComponent {
  isSubmitted = signal(false);
  isPasswordVisible = signal(false);
  token = null;

  form = new FormGroup({
    email: new FormControl('', [Validators.required, Validators.email]),
    password: new FormControl('', [Validators.required, Validators.minLength(8), Validators.pattern(specialCharPattern)]),
  });

  constructor(
    private auth: AuthService,
    private router: Router,
    private route: ActivatedRoute,
    private toastr: ToastrService,
    private translate: TranslateService,
  ) {
    this.token = this.route.snapshot.queryParams['token'] ?? null;

    if (!this.token) {
      this.toastr.error(this.translate.instant(marker('errors.request_reset_password')));
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
          this.toastr.error(extractErrorFromResponse(e) ?? this.translate.instant(marker('errors.the_password_is_not_updated')));

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
    this.router.navigateByUrl('/chat/');
  }

  showPassword() {
    this.isPasswordVisible.set(!this.isPasswordVisible());
  }
}
