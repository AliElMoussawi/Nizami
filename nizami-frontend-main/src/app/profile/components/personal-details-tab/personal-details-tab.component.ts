import {Component, effect, OnInit, output, signal} from '@angular/core';
import {ProfileImageInputComponent} from '../../../auth/components/profile-image-input/profile-image-input.component';
import {AuthService} from '../../../auth/services/auth.service';
import {ControlErrorsComponent} from '../../../common/components/errors/control-errors.component';
import {FormControl, FormGroup, FormsModule, ReactiveFormsModule, Validators} from '@angular/forms';
import {InputComponent} from '../../../common/components/input/input.component';
import {DatePickerComponent} from '../../../common/components/date-picker/date-picker.component';
import {UntilDestroy, untilDestroyed} from '@ngneat/until-destroy';
import {catchError, EMPTY, finalize} from 'rxjs';
import {ToastrService} from 'ngx-toastr';
import {convertToFormData, extractErrorFromResponse} from '../../../common/utils';
import {environment} from '../../../../environments/environment';
import {ButtonComponent} from '../../../common/components/button/button.component';
import {OutlineButtonComponent} from '../../../common/components/outline-button/outline-button.component';
import {TranslatePipe, TranslateService} from '@ngx-translate/core';
import {marker} from '@colsen1991/ngx-translate-extract-marker';

@UntilDestroy()
@Component({
  selector: 'app-personal-details-tab',
  imports: [
    ProfileImageInputComponent,
    ControlErrorsComponent,
    FormsModule,
    InputComponent,
    ReactiveFormsModule,
    DatePickerComponent,
    ButtonComponent,
    OutlineButtonComponent,
    TranslatePipe
  ],
  templateUrl: './personal-details-tab.component.html',
  styleUrl: './personal-details-tab.component.scss'
})
export class PersonalDetailsTabComponent implements OnInit {
  form = new FormGroup({
    profile_image: new FormControl<any>(null, []),
    first_name: new FormControl<any>(null, [Validators.required]),
    last_name: new FormControl<any>(null, [Validators.required]),
    date_of_birth: new FormControl<any>(null, [Validators.required]),
    job_title: new FormControl<any>(null, [Validators.required]),
    company_name: new FormControl<any>(null, [Validators.required]),
  });

  isSaving = signal(false);
  onCancel = output();

  constructor(
    private auth: AuthService,
    private toastr: ToastrService,
    private translate: TranslateService,
  ) {
    effect(() => {
      this.ngOnInit();
    });
  }

  get profileImage(): string | null {
    if (this.user()?.profile_image) {
      return environment.baseUrl + this.user()!.profile_image;
    }

    return null;
  }

  get user() {
    return this.auth.user;
  }

  ngOnInit() {
    if (this.user()) {
      this.form.patchValue(this.user()!);
    }
  }

  selectFile($event: File | null) {
    this.form.controls.profile_image.patchValue($event);
  }

  save() {
    if (this.form.invalid) {
      return;
    }

    this.form.disable();
    this.isSaving.set(true);

    const value = this.form.value;

    if (typeof value.profile_image == 'string' || !value.profile_image) {
      delete value['profile_image'];
    }

    this
      .auth
      .saveProfile(convertToFormData(value))
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
      .subscribe((x) => {
        this.auth.user.update((y) => {
          return {...y, ...x}
        });
        this.toastr.success(this.translate.instant(marker('success.profile_saved')));
      });
  }
}
