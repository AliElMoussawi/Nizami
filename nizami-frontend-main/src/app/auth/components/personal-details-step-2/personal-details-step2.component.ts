import {Component, input, Input, OnInit, output} from '@angular/core';
import {ButtonComponent} from "../../../common/components/button/button.component";
import {FormControl, FormGroup, FormsModule, ReactiveFormsModule, Validators} from "@angular/forms";
import {RouterLink} from "@angular/router";
import {ControlErrorsComponent} from '../../../common/components/errors/control-errors.component';
import {InputComponent} from '../../../common/components/input/input.component';
import {UntilDestroy, untilDestroyed} from '@ngneat/until-destroy';
import {TranslatePipe} from '@ngx-translate/core';

@UntilDestroy()
@Component({
  selector: 'app-personal-details-step-2',
  imports: [
    ButtonComponent,
    FormsModule,
    ReactiveFormsModule,
    RouterLink,
    ControlErrorsComponent,
    InputComponent,
    TranslatePipe,
  ],
  templateUrl: './personal-details-step2.component.html',
  styleUrl: './personal-details-step2.component.scss'
})
export class PersonalDetailsStep2Component implements OnInit {
  form = new FormGroup({
    job_title: new FormControl<any>(null, [Validators.required]),
    company_name: new FormControl(null, [Validators.required]),
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
}
