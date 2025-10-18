import {Component, OnInit} from '@angular/core';
import {FormBuilder, FormGroup, FormControl, Validators, ReactiveFormsModule, FormsModule} from '@angular/forms';
import {Router} from '@angular/router';
import {ToastrService} from 'ngx-toastr';
import {UntilDestroy, untilDestroyed} from '@ngneat/until-destroy';
import {catchError, EMPTY, take} from 'rxjs';

import {TemplateComponent} from '../../../common/components/template/template.component';
import {InputComponent} from '../../../common/components/input/input.component';
import {ButtonComponent} from '../../../common/components/button/button.component';
import {FlatButtonComponent} from '../../../common/components/flat-button/flat-button.component';
import {CommonModule} from '@angular/common';

import {SubscriptionsService} from '../../services/subscriptions.service';
import {PlansService} from '../../../plans/services/plans.service';
import {SubscriptionUtilsService} from '../../services/subscription-utils.service';
import {extractErrorFromResponse} from '../../../common/utils';

import {Plan, CreateSubscriptionRequest} from '../../types/subscription.types';
import {CREDIT_TYPES} from '../../constants/subscription.constants';

@UntilDestroy()
@Component({
  selector: 'app-create-subscription',
  imports: [
    TemplateComponent,
    ReactiveFormsModule,
    FormsModule,
    CommonModule,
    InputComponent,
    ButtonComponent,
    FlatButtonComponent,
  ],
  templateUrl: './create-subscription.component.html',
  styleUrl: './create-subscription.component.scss'
})
export class CreateSubscriptionComponent implements OnInit {
  subscriptionForm: FormGroup<{
    user_email: FormControl<string>;
    plan: FormControl<string>;
    credit_amount: FormControl<number | null>;
    credit_type: FormControl<string>;
    is_unlimited: FormControl<boolean>;
    expiry_date: FormControl<string>;
  }>;
  isLoading = false;
  plans: Plan[] = [];
  selectedPlan: Plan | null = null;
  
  // Constants for template
  readonly CREDIT_TYPES = CREDIT_TYPES;

  constructor(
    private fb: FormBuilder,
    private subscriptionsService: SubscriptionsService,
    private plansService: PlansService,
    private subscriptionUtils: SubscriptionUtilsService,
    private router: Router,
    private toastr: ToastrService,
  ) {
    this.subscriptionForm = this.fb.group({
      user_email: ['', [Validators.required, Validators.email]],
      plan: ['', [Validators.required]],
      credit_amount: [null],
      credit_type: [CREDIT_TYPES.MESSAGES, [Validators.required]],
      is_unlimited: [false],
      expiry_date: ['', [Validators.required]],
    });
  }

  ngOnInit(): void {
    this.loadPlans();
    
    // Watch for plan selection changes
    this.subscriptionForm.get('plan')?.valueChanges
      .pipe(untilDestroyed(this))
      .subscribe(planUuid => {
        this.onPlanSelectionChange(planUuid);
      });
    
    // Watch for is_unlimited changes
    this.subscriptionForm.get('is_unlimited')?.valueChanges
      .pipe(untilDestroyed(this))
      .subscribe(value => {
        if (value) {
          this.subscriptionForm.get('credit_amount')?.setValue(null);
          this.subscriptionForm.get('credit_amount')?.clearValidators();
        } else {
          this.subscriptionForm.get('credit_amount')?.setValidators([Validators.required, Validators.min(1)]);
        }
        this.subscriptionForm.get('credit_amount')?.updateValueAndValidity();
      });

  }

  onPlanSelectionChange(planUuid: string) {
    if (!planUuid) {
      this.selectedPlan = null;
      this.resetFormToDefaults();
      this.updateFormValidation();
      return;
    }

    this.selectedPlan = this.plans.find(plan => plan.uuid === planUuid) || null;

    if (this.selectedPlan) {
      // Auto-populate form with plan properties
      this.populateFormFromPlan(this.selectedPlan);
    }
    
    this.updateFormValidation();
  }

  updateFormValidation() {
    const creditTypeControl = this.subscriptionForm.get('credit_type');
    const creditAmountControl = this.subscriptionForm.get('credit_amount');
    const isUnlimitedControl = this.subscriptionForm.get('is_unlimited');

    if (!this.selectedPlan) {
      // For no plan selected, require all fields
      creditTypeControl?.setValidators([Validators.required]);
      if (!isUnlimitedControl?.value) {
        creditAmountControl?.setValidators([Validators.required, Validators.min(1)]);
      } else {
        creditAmountControl?.clearValidators();
      }
    } else {
      // For predefined plans, clear validators as they're auto-populated
      creditTypeControl?.clearValidators();
      creditAmountControl?.clearValidators();
    }

    creditTypeControl?.updateValueAndValidity();
    creditAmountControl?.updateValueAndValidity();
  }

  populateFormFromPlan(plan: Plan) {
    this.subscriptionForm.patchValue({
      credit_amount: plan.credit_amount,
      credit_type: plan.credit_type || CREDIT_TYPES.MESSAGES,
      is_unlimited: plan.is_unlimited,
    });

    // Set expiry date to 1 year from now
    const expiryDate = new Date();
    expiryDate.setFullYear(expiryDate.getFullYear() + 1);
    this.subscriptionForm.patchValue({
      expiry_date: expiryDate.toISOString().slice(0, 16)
    });
  }

  resetFormToDefaults() {
    this.subscriptionForm.patchValue({
      credit_amount: null,
      credit_type: CREDIT_TYPES.MESSAGES,
      is_unlimited: false,
      expiry_date: ''
    });
  }

  loadPlans() {
    this.plansService.getPlans()
      .pipe(
        take(1),
        untilDestroyed(this),
        catchError((e) => {
          console.error('Error loading plans:', e);
          this.toastr.error('Failed to load plans');
          return EMPTY;
        })
      )
      .subscribe(response => {
        this.plans = response.data || [];
      });
  }


  onSubmit() {
    if (this.subscriptionForm.valid && !this.isLoading) {
      this.isLoading = true;
      
      const formData = this.subscriptionForm.value as CreateSubscriptionRequest;
      
      // Convert datetime-local input to ISO string
      if (formData.expiry_date) {
        formData.expiry_date = new Date(formData.expiry_date).toISOString();
      }

      this.subscriptionsService
        .createSubscription(formData)
        .pipe(
          take(1),
          untilDestroyed(this),
          catchError((e) => {
            const errorMessage = extractErrorFromResponse(e);
            this.toastr.error(errorMessage ?? "Failed to create subscription");
            this.isLoading = false;
            return EMPTY;
          }),
        )
        .subscribe(() => {
          this.toastr.success("Subscription created successfully");
          this.router.navigate(['/subscriptions']);
        });
    } else {
      this.markFormGroupTouched();
    }
  }

  onCancel() {
    this.router.navigate(['/subscriptions']);
  }

  // Utility methods for template
  formatPlanDisplayName(plan: Plan): string {
    return this.subscriptionUtils.formatPlanDisplayName(plan);
  }

  formatPlanProperties(plan: Plan): string {
    return this.subscriptionUtils.formatPlanProperties(plan);
  }

  getPlanPriceInDollars(plan: Plan): number {
    return this.subscriptionUtils.getPlanPriceInDollars(plan);
  }

  getIntervalUnitLabel(plan: Plan): string {
    return this.subscriptionUtils.getIntervalUnitLabel(plan);
  }

  private markFormGroupTouched() {
    Object.keys(this.subscriptionForm.controls).forEach(key => {
      const control = this.subscriptionForm.get(key);
      control?.markAsTouched();
    });
  }

  getFieldError(fieldName: string): string {
    const field = this.subscriptionForm.get(fieldName);
    if (field?.errors && field.touched) {
      if (field.errors['required']) {
        return `${fieldName} is required`;
      }
      if (field.errors['min']) {
        return `${fieldName} must be at least ${field.errors['min'].min}`;
      }
    }
    return '';
  }

}
