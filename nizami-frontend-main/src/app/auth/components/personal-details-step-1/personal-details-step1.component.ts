import {Component, input, Input, OnInit, output} from '@angular/core';
import {ButtonComponent} from "../../../common/components/button/button.component";
import {FormControl, FormGroup, FormsModule, ReactiveFormsModule, Validators} from "@angular/forms";
import {RouterLink} from "@angular/router";
import {ProfileImageInputComponent} from '../profile-image-input/profile-image-input.component';
import {DatePickerComponent} from '../../../common/components/date-picker/date-picker.component';
import {ControlErrorsComponent} from '../../../common/components/errors/control-errors.component';
import {UntilDestroy, untilDestroyed} from '@ngneat/until-destroy';
import {TranslatePipe} from '@ngx-translate/core';

@UntilDestroy()
@Component({
  selector: 'app-personal-details-step-1',
  imports: [
    ButtonComponent,
    FormsModule,
    ReactiveFormsModule,
    RouterLink,
    ProfileImageInputComponent,
    DatePickerComponent,
    ControlErrorsComponent,
    TranslatePipe,
  ],
  templateUrl: './personal-details-step1.component.html',
  styleUrl: './personal-details-step1.component.scss'
})
export class PersonalDetailsStep1Component implements OnInit {
  form = new FormGroup({
    profile_image: new FormControl<any>(null, []),
    date_of_birth: new FormControl(null, [Validators.required]),
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

  ngOnInit() {
    this.form.patchValue(this.initial());

    this.form.valueChanges
      .pipe(untilDestroyed(this))
      .subscribe((v) => {
        this.onChange.emit(v);
      });
  }

  submit() {
    this.form.markAllAsTouched();

    if (this.form.invalid) {
      return;
    }

    this.onSubmit.emit(this.form.value);
  }

  selectFile($event: File | null) {
    this.form.controls.profile_image.patchValue($event);
  }

}
