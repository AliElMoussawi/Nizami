import {Component, effect, input, output} from '@angular/core';
import {FormControl, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';
import {InputComponent} from '../../../common/components/input/input.component';
import {FlatButtonComponent} from '../../../common/components/flat-button/flat-button.component';
import {ButtonComponent} from '../../../common/components/button/button.component';
import {UserModel} from '../../../common/models/user.model';
import {DatePickerComponent} from '../../../common/components/date-picker/date-picker.component';
import {ControlErrorsComponent} from '../../../common/components/errors/control-errors.component';
import {CountryPickerComponent} from '../../../common/components/country-picker/country-picker.component';
import {ProfileImageDragComponent} from '../../../common/components/profile-image-drag/profile-image-drag.component';
import {Router} from '@angular/router';
import {JurisdictionSelectComponent} from '../jurisdiction-select/jurisdiction-select.component';
import {take} from 'rxjs';
import {UntilDestroy, untilDestroyed} from '@ngneat/until-destroy';
import {JurisdictionService} from '../../../reference-documents/services/jurisdiction.service';
import {NgIcon} from '@ng-icons/core';

@UntilDestroy()
@Component({
  selector: 'app-user-form',
  imports: [
    InputComponent,
    ReactiveFormsModule,
    FlatButtonComponent,
    ButtonComponent,
    DatePickerComponent,
    ControlErrorsComponent,
    ProfileImageDragComponent,
    NgIcon,

  ],
  templateUrl: './user-form.component.html',
  styleUrl: './user-form.component.scss'
})
export class UserFormComponent {
  disabled = input(false);
  value = input<UserModel | null>(null);
  showPasswordNote = input(true);

  onSubmit = output<any>();
  onSubmitAndReset = output<any>();

  form = new FormGroup({
    first_name: new FormControl('', [Validators.required]),
    last_name: new FormControl('', [Validators.required]),
    email: new FormControl('', [Validators.required, Validators.email]),
    date_of_birth: new FormControl('', [Validators.required]),
    company_name: new FormControl('', [Validators.required]),
    job_title: new FormControl('', []),
    profile_image: new FormControl<any>(null, []),
    country: new FormControl('sa', []),
    jurisdiction: new FormControl(['sa'], [Validators.required]),
  });

  showCreateAnother = input<boolean>(true);
  submitText = input<string>('Create');

  constructor(
    private router: Router,
    private jurisdictionService: JurisdictionService,
  ) {
    jurisdictionService
      .load()
      .pipe(
        take(1),
        untilDestroyed(this),
      )
      .subscribe();


    effect(() => {
      if (this.value()) {
        this.form.patchValue(this.value()!);
      }
    });

    effect(() => {
      let isDisabled = this.disabled();

      if (isDisabled) {
        this.form.disable();
      } else {
        this.form.enable();
      }
    });
  }

  get allowedCountries() {
    return this.jurisdictionService.jurisdictions;
  }

  submit() {
    if (this.form.invalid) {
      return;
    }

    let value = this.form.value;

    if (value.profile_image == null) {
      delete value['profile_image'];
    }

    this.onSubmit.emit(this.form.value);
  }

  createAndCreateAnother() {
    if (this.form.invalid) {
      return;
    }

    this.onSubmitAndReset.emit(this.form.value);
  }

  cancelClicked() {
    this.router.navigateByUrl('/users');
  }
}
