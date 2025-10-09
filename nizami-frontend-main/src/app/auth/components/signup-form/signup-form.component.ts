import {Component, signal} from '@angular/core';
import {ReactiveFormsModule} from '@angular/forms';
import {AuthService} from '../../services/auth.service';
import {UntilDestroy, untilDestroyed} from '@ngneat/until-destroy';
import {catchError, EMPTY} from 'rxjs';
import {ToastrService} from 'ngx-toastr';
import {Router} from '@angular/router';
import {StepperComponent} from '../../../common/components/stepper/stepper.component';
import {StepDirective} from '../../../common/directives/step.directive';
import {CreateAccountStepComponent} from '../create-account-step/create-account-step.component';
import {PersonalDetailsStep1Component} from '../personal-details-step-1/personal-details-step1.component';
import {PersonalDetailsStep2Component} from '../personal-details-step-2/personal-details-step2.component';
import {convertToFormData, extractErrorFromResponse} from '../../../common/utils';
import {marker} from '@colsen1991/ngx-translate-extract-marker';
import {TranslateService} from '@ngx-translate/core';

@UntilDestroy()
@Component({
  selector: 'app-signup-form',
  imports: [
    ReactiveFormsModule,
    StepperComponent,
    StepDirective,
    CreateAccountStepComponent,
    PersonalDetailsStep1Component,
    PersonalDetailsStep2Component
  ],
  templateUrl: './signup-form.component.html',
  styleUrl: './signup-form.component.scss'
})
export class SignupFormComponent {
  data: any = {};

  step = signal(1);
  isCreating = signal<boolean>(false);

  constructor(
    private auth: AuthService,
    private toastr: ToastrService,
    private router: Router,
    private translate: TranslateService,
  ) {
  }

  createAccount() {
    this.isCreating.set(true);

    let value = {
      ...this.data,
    };

    if (typeof value.profile_image == 'string' || !value.profile_image) {
      delete value['profile_image'];
    }

    this
      .auth
      .signup(convertToFormData(value))
      .pipe(
        untilDestroyed(this),
        catchError((e) => {
            this.toastr.error(extractErrorFromResponse(e) ?? this.translate.instant(marker('errors.failed_to_register')));

            this.isCreating.set(false);

            return EMPTY;
          }
        ),
      )
      .subscribe((x) => {
        this.router.navigate(['/chat/']);
      });
  }

  createAccountSubmit($event: any) {
    this.data = {
      ...this.data,
      ...$event,
    };

    this.step.set(2);
  }

  personalStep1Submit($event: any) {
    this.data = {
      ...this.data,
      ...$event,
    };

    this.step.set(3);
  }

  personalStep2Submit($event: any) {
    this.data = {
      ...this.data,
      ...$event,
    };

    this.createAccount();
  }

  onStepClicked(step: number) {
    this.step.set(step);
  }

  onChange($event: any) {
    this.data = {
      ...this.data,
      ...$event,
    };
  }
}
