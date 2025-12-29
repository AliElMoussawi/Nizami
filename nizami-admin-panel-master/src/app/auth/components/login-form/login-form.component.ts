import {Component, signal} from '@angular/core';
import {InputComponent} from '../../../common/components/input/input.component';
import {ButtonComponent} from '../../../common/components/button/button.component';
import {FormControl, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';
import {AuthService} from '../../services/auth.service';
import {UntilDestroy, untilDestroyed} from '@ngneat/until-destroy';
import {catchError, EMPTY} from 'rxjs';
import {ToastrService} from 'ngx-toastr';
import {Router, RouterLink} from '@angular/router';
import {AuthCardComponent} from '../auth-card/auth-card.component';
import {extractErrorFromResponse} from '../../../common/utils';
import {CheckboxComponent} from '../../../common/components/checkbox/checkbox.component';

@UntilDestroy()
@Component({
  selector: 'app-login-form',
  imports: [
    InputComponent,
    ButtonComponent,
    ReactiveFormsModule,
    RouterLink,
    AuthCardComponent,
    CheckboxComponent
  ],
  templateUrl: './login-form.component.html',
  styleUrl: './login-form.component.scss'
})
export class LoginFormComponent {
  isPasswordVisible = signal(false);
  form = new FormGroup({
    email: new FormControl(null, [Validators.required, Validators.email]),
    password: new FormControl(null, [Validators.required]),
    remember_me: new FormControl(null, []),
  });

  constructor(
    private auth: AuthService,
    private toastr: ToastrService,
    private router: Router,
  ) {
  }

  showPassword() {
    this.isPasswordVisible.set(!this.isPasswordVisible());
  }

  submit() {
    if (this.form.invalid) {
      return;
    }

    this.form.disable();

    this
      .auth
      .login(this.form.value)
      .pipe(
        untilDestroyed(this),
        catchError((e) => {
            this.toastr.error(extractErrorFromResponse(e) ?? "Failed to login");

            this.form.enable();

            return EMPTY;
          }
        ),
      )
      .subscribe((_x) => {
        this.router.navigate(['/users']);
      });
  }
}
