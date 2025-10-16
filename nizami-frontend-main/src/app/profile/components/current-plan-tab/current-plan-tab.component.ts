import { Component, OnInit, Optional, output } from '@angular/core';
import { CommonModule, DatePipe, LowerCasePipe } from '@angular/common';
import { TranslatePipe } from '@ngx-translate/core';
import { Router } from '@angular/router';
import { DialogRef } from '@angular/cdk/dialog';
import { SubscriptionService } from '../../services/subscription.service';
import { UserSubscription } from '../../models/subscription.model';
import { SpinnerComponent } from '../../../common/components/spinner/spinner.component';
import { ErrorComponent } from '../../../common/components/error/error.component';
import { ButtonComponent } from '../../../common/components/button/button.component';
import { OutlineButtonComponent } from '../../../common/components/outline-button/outline-button.component';

@Component({
  selector: 'app-current-plan-tab',
  standalone: true,
  imports: [
    CommonModule,
    TranslatePipe,
    LowerCasePipe,
    DatePipe,
    SpinnerComponent,
    ErrorComponent,
    ButtonComponent,
    OutlineButtonComponent
  ],
  templateUrl: './current-plan-tab.component.html',
  styleUrls: ['./current-plan-tab.component.scss']
})
export class CurrentPlanTabComponent implements OnInit {
  onCancel = output();
  subscription: UserSubscription | null = null;
  loading = true;
  error: string | null = null;
  cancelling = false;
  showCancelConfirmation = false;

  constructor(
    private subscriptionService: SubscriptionService,
    private router: Router,
    @Optional() private dialogRef: DialogRef<any>
  ) {}

  ngOnInit(): void {
    this.loadActiveSubscription();
  }

  loadActiveSubscription(): void {
    this.loading = true;
    this.error = null;

    // Get the latest subscription (active, cancelled, or expired)
    this.subscriptionService.getLatestSubscription().subscribe({
      next: (subscription: UserSubscription) => {
        this.subscription = subscription;
        this.loading = false;
      },
      error: (err: any) => {
        this.loading = false;
        
        // HTTP status 0 means backend is unreachable
        if (err.status === 0) {
          this.error = 'Unable to connect to the server. Please check your connection and try again.';
          this.subscription = null;
          return;
        }
        
        // 404 means no subscription at all (not an error)
        if (err.status === 404) {
          this.error = null;
          this.subscription = null;
          return;
        }
        
        // Other errors
        this.error = `Failed to load subscription: ${err?.error?.message || err?.message || 'Unknown error'}`;
        this.subscription = null;
      }
    });
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

  isExpired(expiryDate: string): boolean {
    return new Date(expiryDate) < new Date();
  }

  getDaysRemaining(expiryDate: string): number {
    const now = new Date();
    const expiry = new Date(expiryDate);
    const diff = expiry.getTime() - now.getTime();
    return Math.ceil(diff / (1000 * 60 * 60 * 24));
  }

  canCancelSubscription(): boolean {
    if (!this.subscription) return false;
    return this.subscription.is_active && !this.isExpired(this.subscription.expiry_date);
  }

  isExpiredOrInactive(): boolean {
    if (!this.subscription) return false;
    return !this.subscription.is_active || this.isExpired(this.subscription.expiry_date);
  }

  renewSubscription(): void {
    if (!this.subscription?.plan?.uuid) return;
    
    // Close dialog if exists
    if (this.dialogRef) {
      this.dialogRef.close();
    }
    
    // Navigate to payment page with the same plan
    this.router.navigate(['/payment', this.subscription.plan.uuid]);
  }

  openCancelConfirmation(): void {
    this.showCancelConfirmation = true;
  }

  closeCancelConfirmation(): void {
    this.showCancelConfirmation = false;
  }

  confirmCancelSubscription(): void {
    this.cancelling = true;
    this.error = null;

    this.subscriptionService.cancelSubscription().subscribe({
      next: (response) => {
        this.cancelling = false;
        this.showCancelConfirmation = false;
        // Reload subscription to get updated status
        this.loadActiveSubscription();
      },
      error: (err) => {
        this.cancelling = false;
        this.showCancelConfirmation = false;
        if (err.error?.error === 'subscription_already_expired') {
          this.error = 'This subscription has already expired';
        } else if (err.error?.error === 'no_active_user_subscription') {
          this.error = 'No active subscription found';
        } else {
          this.error = `Failed to cancel subscription: ${err?.error?.message || err?.message || 'Unknown error'}`;
        }
      }
    });
  }
}

