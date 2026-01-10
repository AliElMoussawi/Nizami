import { Component, OnInit, Optional, output } from '@angular/core';
import { CommonModule, LowerCasePipe } from '@angular/common';
import { Router } from '@angular/router';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';
import { DialogRef } from '@angular/cdk/dialog';
import { PaymentService } from '../../../payment/services/payment.service';
import { Plan } from '../../../payment/models/plan.model';
import { SpinnerComponent } from '../../../common/components/spinner/spinner.component';
import { ButtonComponent } from '../../../common/components/button/button.component';
import { ErrorComponent } from '../../../common/components/error/error.component';
import { OutlineButtonComponent } from '../../../common/components/outline-button/outline-button.component';

@Component({
  selector: 'app-plans-tab',
  standalone: true,
  imports: [
    CommonModule, 
    TranslatePipe, 
    LowerCasePipe,
    SpinnerComponent,
    ButtonComponent,
    ErrorComponent,
    OutlineButtonComponent
  ],
  templateUrl: './plans-tab.component.html',
  styleUrls: ['./plans-tab.component.scss']
})
export class PlansTabComponent implements OnInit {
  onCancel = output();
  plans: Plan[] = [];
  loading = true;
  error: string | null = null;

  constructor(
    private paymentService: PaymentService,
    private router: Router,
    private translateService: TranslateService,
    @Optional() private dialogRef: DialogRef<any>
  ) {}

  ngOnInit(): void {
    this.loadPlans();
  }

  loadPlans(): void {
    this.loading = true;
    this.error = null;

    this.paymentService.listAvailableUpgradePlans().subscribe({
      next: (plans: Plan[]) => {
        this.plans = Array.isArray(plans) ? plans : [];
        this.loading = false;
      },
      error: (err: any) => {
        this.error = `Failed to load plans: ${err?.message || err?.status || 'Unknown error'}`;
        this.plans = [];
        this.loading = false;
      }
    });
  }
  selectPlan(plan: Plan): void {
    // Close the dialog if it exists (when opened from profile settings)
    if (this.dialogRef) {
      this.dialogRef.close();
    }
    
    // Navigate to payment page
    this.router.navigate(['/payment', plan.uuid]);
  }

  formatPrice(priceCents: number, currency: string): string {
    if (isNaN(priceCents)) return `0.00 ${currency}`;
    return `${(priceCents / 100).toFixed(2)} ${currency}`;
  }

  getIntervalText(intervalUnit: string | null, intervalCount: number | null): string {
    if (!intervalUnit || !intervalCount) return '';
    
    const unitKey = intervalCount > 1 
      ? `billing_interval.${intervalUnit.toLowerCase()}s`
      : `billing_interval.${intervalUnit.toLowerCase()}`;
    
    const translatedUnit = this.translateService.instant(unitKey);
    const prefix = this.translateService.instant('interval_prefix') || '/';
    
    return intervalCount > 1 
      ? `${prefix} ${intervalCount} ${translatedUnit}`
      : `${prefix} ${translatedUnit}`;
  }

  getCreditTypeText(creditType: string | null): string {
    if (!creditType) return '';
    // Always use plural form for credit type
    const key = `credit_type.messages`;
    return this.translateService.instant(key);
  }
}
