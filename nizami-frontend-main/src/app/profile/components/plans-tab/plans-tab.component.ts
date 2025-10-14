import { Component, OnInit, Optional } from '@angular/core';
import { CommonModule, LowerCasePipe } from '@angular/common';
import { Router } from '@angular/router';
import { TranslatePipe } from '@ngx-translate/core';
import { DialogRef } from '@angular/cdk/dialog';
import { PaymentService } from '../../../payment/services/payment.service';
import { Plan } from '../../../payment/models/plan.model';
import { SpinnerComponent } from '../../../common/components/spinner/spinner.component';
import { ButtonComponent } from '../../../common/components/button/button.component';
import { ErrorComponent } from '../../../common/components/error/error.component';

@Component({
  selector: 'app-plans-tab',
  standalone: true,
  imports: [
    CommonModule, 
    TranslatePipe, 
    LowerCasePipe,
    SpinnerComponent,
    ButtonComponent,
    ErrorComponent
  ],
  templateUrl: './plans-tab.component.html',
  styleUrls: ['./plans-tab.component.scss']
})
export class PlansTabComponent implements OnInit {
  plans: Plan[] = [];
  loading = true;
  error: string | null = null;

  constructor(
    private paymentService: PaymentService,
    private router: Router,
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
    const plural = intervalCount > 1 ? `${intervalUnit.toLowerCase()}s` : intervalUnit.toLowerCase();
    return `/ ${intervalCount > 1 ? intervalCount + ' ' : ''}${plural}`;
  }
}
