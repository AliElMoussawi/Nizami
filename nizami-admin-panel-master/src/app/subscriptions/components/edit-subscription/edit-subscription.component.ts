import {Component, OnInit} from '@angular/core';
import {TemplateComponent} from '../../../common/components/template/template.component';
import {FormBuilder, FormGroup, FormControl, Validators, ReactiveFormsModule} from '@angular/forms';
import {SubscriptionsService, UserSubscriptionModel} from '../../services/subscriptions.service';
import {Router, ActivatedRoute} from '@angular/router';
import {ToastrService} from 'ngx-toastr';
import {UntilDestroy, untilDestroyed} from '@ngneat/until-destroy';
import {catchError, EMPTY, take} from 'rxjs';
import {extractErrorFromResponse} from '../../../common/utils';
import {CommonModule} from '@angular/common';
import {InputComponent} from '../../../common/components/input/input.component';
import {ButtonComponent} from '../../../common/components/button/button.component';
import {FlatButtonComponent} from '../../../common/components/flat-button/flat-button.component';

@UntilDestroy()
@Component({
  selector: 'app-edit-subscription',
  imports: [
    TemplateComponent,
    ReactiveFormsModule,
    CommonModule,
    InputComponent,
    ButtonComponent,
    FlatButtonComponent,
  ],
  templateUrl: './edit-subscription.component.html',
  styleUrl: './edit-subscription.component.scss'
})
export class EditSubscriptionComponent implements OnInit {
  subscriptionForm: FormGroup<{
    is_active: FormControl<boolean>;
    credit_amount: FormControl<number | null>;
    credit_type: FormControl<string>;
    is_unlimited: FormControl<boolean>;
    expiry_date: FormControl<string>;
  }>;
  isLoading = false;
  subscription: UserSubscriptionModel | null = null;
  subscriptionUuid: string = '';

  constructor(
    private fb: FormBuilder,
    private subscriptionsService: SubscriptionsService,
    private router: Router,
    private route: ActivatedRoute,
    private toastr: ToastrService,
  ) {
    this.subscriptionForm = this.fb.group({
      is_active: [false, [Validators.required]],
      credit_amount: [null],
      credit_type: ['MESSAGES', [Validators.required]],
      is_unlimited: [false],
      expiry_date: ['', [Validators.required]],
    });
  }

  ngOnInit(): void {
    this.subscriptionUuid = this.route.snapshot.paramMap.get('uuid') || '';
    
    if (this.subscriptionUuid) {
      this.loadSubscription();
    }

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

  loadSubscription() {
    this.isLoading = true;
    
    this.subscriptionsService
      .loadSubscription(this.subscriptionUuid)
      .pipe(
        take(1),
        untilDestroyed(this),
        catchError((e) => {
          this.toastr.error(extractErrorFromResponse(e) ?? "Failed to load subscription");
          this.router.navigate(['/subscriptions']);
          return EMPTY;
        }),
      )
      .subscribe((subscription) => {
        this.subscription = subscription;
        this.populateForm(subscription);
        this.isLoading = false;
      });
  }

  populateForm(subscription: UserSubscriptionModel) {
    this.subscriptionForm.patchValue({
      is_active: subscription.is_active,
      credit_amount: subscription.credit_amount,
      credit_type: subscription.credit_type,
      is_unlimited: subscription.is_unlimited,
      expiry_date: subscription.expiry_date ? new Date(subscription.expiry_date).toISOString().slice(0, 16) : '',
    });
  }

  onSubmit() {
    if (this.subscriptionForm.valid && !this.isLoading) {
      this.isLoading = true;
      
      const formData = this.subscriptionForm.value;
      
      // Convert datetime-local input to ISO string
      if (formData.expiry_date) {
        formData.expiry_date = new Date(formData.expiry_date).toISOString();
      }

      this.subscriptionsService
        .updateSubscription(this.subscriptionUuid, formData)
        .pipe(
          take(1),
          untilDestroyed(this),
          catchError((e) => {
            this.toastr.error(extractErrorFromResponse(e) ?? "Failed to update subscription");
            this.isLoading = false;
            return EMPTY;
          }),
        )
        .subscribe(() => {
          this.toastr.success("Subscription updated successfully");
          this.router.navigate(['/subscriptions']);
        });
    } else {
      this.markFormGroupTouched();
    }
  }

  onCancel() {
    this.router.navigate(['/subscriptions']);
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
