import {Component, Input, Output, EventEmitter, OnInit, signal} from '@angular/core';
import {CommonModule} from '@angular/common';
import {PaymentsService} from '../../services/payments.service';
import {Payment} from '../../types/payment.types';
import {UntilDestroy, untilDestroyed} from '@ngneat/until-destroy';
import {catchError, EMPTY} from 'rxjs';

@UntilDestroy()
@Component({
  selector: 'app-payment-details-modal',
  imports: [CommonModule],
  templateUrl: './payment-details-modal.component.html',
  styleUrl: './payment-details-modal.component.scss'
})
export class PaymentDetailsModalComponent implements OnInit {
  @Input() paymentId: string | null = null;
  @Output() close = new EventEmitter<void>();

  payment = signal<Payment | null>(null);
  loading = signal<boolean>(false);
  error = signal<string | null>(null);
  userInfo = signal<{name: string, email: string} | null>(null);

  constructor(
    private paymentsService: PaymentsService,
  ) {}

  ngOnInit(): void {
    if (this.paymentId) {
      this.loadPaymentDetails();
    }
  }

  loadPaymentDetails() {
    if (!this.paymentId) return;
    
    this.loading.set(true);
    this.error.set(null);
    
    this.paymentsService.getPaymentDetails(this.paymentId)
      .pipe(
        untilDestroyed(this),
        catchError((_error) => {
          this.error.set('Failed to load payment details. Please try again.');
          this.loading.set(false);
          return EMPTY;
        })
      )
      .subscribe((payment) => {
        this.payment.set(payment);
        this.loadUserInfo(payment);
        this.loading.set(false);
      });
  }

  private loadUserInfo(payment: Payment) {
    const userId = payment.metadata?.user_id;
    const userEmail = payment.metadata?.user_email;
    const userName = payment.metadata?.user_name;
    
    if (userId) {
      this.userInfo.set({
        name: `User ID = ${userId}`,
        email: userEmail || ''
      });
    } else if (userEmail) {
      this.userInfo.set({
        name: userName || 'Unknown User',
        email: userEmail
      });
    }
  }

  closeModal() {
    this.close.emit();
  }

  navigateToUser() {
    const payment = this.payment();
    if (payment?.metadata?.user_id) {
      // Navigate directly to user edit page
      window.open(`/users/${payment.metadata.user_id}/edit`, '_blank');
    }
  }

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleString();
  }

  getStatusColor(status: string): string {
    const colors: { [key: string]: string } = {
      'paid': 'text-green-600 bg-green-100',
      'failed': 'text-red-600 bg-red-100',
      'authorized': 'text-yellow-600 bg-yellow-100',
      'initiated': 'text-blue-600 bg-blue-100',
      'voided': 'text-gray-600 bg-gray-100'
    };
    return colors[status] || 'text-gray-600 bg-gray-100';
  }
}
