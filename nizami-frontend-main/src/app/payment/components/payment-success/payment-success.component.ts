import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { TranslatePipe } from '@ngx-translate/core';
import { ButtonComponent } from '../../../common/components/button/button.component';
import { PaymentService } from '../../services/payment.service';
import { SpinnerComponent } from '../../../common/components/spinner/spinner.component';
import { AuthService } from '../../../auth/services/auth.service';

@Component({
  selector: 'app-payment-success',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    TranslatePipe,
    ButtonComponent,
    SpinnerComponent
  ],
  templateUrl: './payment-success.component.html',
  styleUrls: ['./payment-success.component.scss']
})
export class PaymentSuccessComponent implements OnInit {
  paymentId: string | null = null;
  loading = true;
  error: string | null = null;
  paymentVerified = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private paymentService: PaymentService,
    private authService: AuthService
  ) {}

  ngOnInit() {
    this.paymentId = this.route.snapshot.queryParamMap.get('paymentId');
    
    if (!this.paymentId) {
      this.error = 'Payment ID is missing';
      this.loading = false;
      return;
    }

    // Check if user is authenticated
    if (!this.authService.isAuthenticated()) {
      console.error('[PaymentSuccess] User not authenticated');
      this.error = 'Authentication required. Please log in again.';
      this.loading = false;
      setTimeout(() => {
        this.router.navigate(['/login']);
      }, 2000);
      return;
    }

    // Sync payment status with backend
    this.syncPayment();
  }

  syncPayment() {
    if (!this.paymentId) return;

    console.log('[PaymentSuccess] Syncing payment with backend...');
    console.log('[PaymentSuccess] Auth token present:', !!this.authService.getToken());

    this.paymentService.syncPaymentStatus(this.paymentId).subscribe({
      next: (response) => {
        console.log('[PaymentSuccess] Payment synced successfully:', response);
        this.paymentVerified = true;
        this.loading = false;
      },
      error: (err) => {
        console.error('[PaymentSuccess] Failed to sync payment:', err);
        this.error = 'Failed to verify payment. Please contact support.';
        this.loading = false;
      }
    });
  }

  goToChat() {
    this.router.navigate(['/chat']);
  }
}

