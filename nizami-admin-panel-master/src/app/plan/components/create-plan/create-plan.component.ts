import {Component} from '@angular/core';
import {CommonModule} from '@angular/common';
import {TemplateComponent} from '../../../common/components/template/template.component';
import {FormControl, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';
import {PlansService} from '../../services/plans.service';
import {Router} from '@angular/router';
import {ToastrService} from 'ngx-toastr';
import {InputComponent} from '../../../common/components/input/input.component';
import {ControlErrorsComponent} from '../../../common/components/errors/control-errors.component';
import {ButtonComponent} from '../../../common/components/button/button.component';
import {FlatButtonComponent} from '../../../common/components/flat-button/flat-button.component';
import {CheckboxComponent} from '../../../common/components/checkbox/checkbox.component';
import {FormsModule} from '@angular/forms';
import {MatSelect} from '@angular/material/select';
import {MatOption} from '@angular/material/core';
// Removed MatFormField and MatLabel as we no longer use mat-form-field wrapper

@Component({
  selector: 'app-create-plan',
  standalone: true,
  imports: [TemplateComponent, CommonModule, ReactiveFormsModule, FormsModule, InputComponent, ControlErrorsComponent, ButtonComponent, FlatButtonComponent, CheckboxComponent, MatSelect, MatOption],
  templateUrl: './create-plan.component.html',
  styleUrl: './create-plan.component.scss'
})
export class CreatePlanComponent {
  tiers = [
    { value: 'BASIC', label: 'Basic' },
    { value: 'PLUS', label: 'Plus' },
    { value: 'PREMIUM_MONTHLY', label: 'Premium-Monthly' },
    { value: 'PREMIUM_YEARLY', label: 'Premium-Yearly' },
  ];

  creditTypes = [
    { value: 'MESSAGES', label: 'Messages' },
  ];

  intervalUnits = [
    { value: 'MONTH', label: 'Month' },
    { value: 'YEAR', label: 'Year' },
  ];

  currencyOptions = [
    { value: 'USD', label: 'US Dollar' },
    { value: 'SAR', label: 'Saudi Riyal' },
  ];

  form = new FormGroup({
    name: new FormControl<string | null>(null, [Validators.required]),
    tier: new FormControl<string | null>(null, [Validators.required]),
    description: new FormControl<string | null>(null),
    price_cents: new FormControl<number | null>(null, [Validators.required, Validators.min(0)]),
    currency: new FormControl<string>('USD', [Validators.required]),
    interval_unit: new FormControl<string | null>(null),
    interval_count: new FormControl<number | null>(null, [Validators.min(1)]),
    credit_amount: new FormControl<number | null>(null, [Validators.min(0)]),
    credit_type: new FormControl<string | null>(null, [Validators.required]),
    is_unlimited: new FormControl<boolean>(false),
    rollover_allowed: new FormControl<boolean>(false),
  });

  isSubmitting = false;

  constructor(private plans: PlansService, private router: Router, private toastr: ToastrService) {}

  ngOnInit() {
    // Toggle logic: unlimited disables and clears credit fields
    this.form.controls.is_unlimited.valueChanges.subscribe((unlimited) => {
      const creditAmount = this.form.controls.credit_amount;
      const creditType = this.form.controls.credit_type;
      if (unlimited) {
        creditAmount.setValue(null);
        creditType.setValue(null);
        creditAmount.disable({ emitEvent: false });
        creditType.disable({ emitEvent: false });
      } else {
        creditAmount.enable({ emitEvent: false });
        creditType.enable({ emitEvent: false });
      }
    });

    // Ensure initial state respected on load
    const isUnlimited = this.form.controls.is_unlimited.value as boolean;
    if (isUnlimited) {
      this.form.controls.credit_amount.disable({ emitEvent: false });
      this.form.controls.credit_type.disable({ emitEvent: false });
    }
  }

  private buildPayload() {
    const raw = this.form.value as any;
    const payload: any = { ...raw };
    Object.keys(payload).forEach((k) => {
      if (payload[k] === null) {
        delete payload[k];
      }
    });
    return payload;
  }

  submit() {
    if (this.form.invalid || this.isSubmitting) {
      return;
    }
    this.isSubmitting = true;
    const payload = this.buildPayload();
    this.plans.create(payload).subscribe({
      next: () => {
        this.toastr.success('Plan created');
        this.router.navigate(['/plans']);
      },
      error: () => {
        this.toastr.error('Failed to create plan');
        this.isSubmitting = false;
      }
    });
  }

  cancel() {
    this.router.navigate(['/plans']);
  }
}


