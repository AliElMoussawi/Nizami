import {Component, OnDestroy, signal} from '@angular/core';
import {InputComponent} from '../../../common/components/input/input.component';
import {ButtonComponent} from '../../../common/components/button/button.component';
import {FormControl, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';
import {AuthService} from '../../services/auth.service';
import {catchError, EMPTY, finalize} from 'rxjs';
import {UntilDestroy, untilDestroyed} from '@ngneat/until-destroy';
import {AuthCardComponent} from '../auth-card/auth-card.component';
import {ControlErrorsComponent} from '../../../common/components/errors/control-errors.component';

@UntilDestroy()
@Component({
  selector: 'app-forgot-password-form',
  imports: [
    InputComponent,
    ButtonComponent,
    ReactiveFormsModule,
    AuthCardComponent,
    ControlErrorsComponent,
  ],
  templateUrl: './forgot-password-form.component.html',
  styleUrl: './forgot-password-form.component.scss'
})
export class ForgotPasswordFormComponent implements OnDestroy {
  isSubmitted = signal(false);

  form = new FormGroup({
    email: new FormControl(null, [Validators.required, Validators.email]),
  });
  isResendDisabled = signal(true);
  countDownMax = 30;
  countDown = signal(this.countDownMax);
  timer: any;

  constructor(private auth: AuthService) {
  }

  get emailControl() {
    return this.form.controls.email;
  }

  ngOnDestroy() {
    if (this.timer) {
      clearInterval(this.timer);
    }
  }

  submit() {
    if (this.form.invalid) {
      return;
    }

    this.form.disable();
    this.auth
      .forgotPassword(this.form.value)
      .pipe(
        untilDestroyed(this),
        catchError(() => {
          return EMPTY;
        }),
        finalize(() => {
          this.form.enable();
          this.isSubmitted.set(true)

          this.startTimer();
        }),
      )
      .subscribe();
  }

  resend() {
    if (this.isResendDisabled()) {
      return;
    }

    this.submit();
  }

  startTimer() {
    this.isResendDisabled.set(true);
    this.countDown.set(this.countDownMax);

    this.timer = setInterval(() => {
      this.countDown.update((v) => v - 1);

      if (this.countDown() <= 0) {
        this.isResendDisabled.set(false);
        clearInterval(this.timer);
      }
    }, 1000);
  }
}
