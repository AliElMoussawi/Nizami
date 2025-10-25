import {Component, OnInit, output, signal} from '@angular/core';
import {DatePipe, NgClass} from '@angular/common';
import {TranslatePipe, TranslateService} from '@ngx-translate/core';
import {OutlineButtonComponent} from '../../../common/components/outline-button/outline-button.component';
import {PaymentService} from '../../../payment/services/payment.service';
import {PaginatedResponse} from '../../../payment/models/paginated-response.model';
import {Payment} from '../../../payment/models/payment.model';

@Component({
  selector: 'app-payments-tab',
  imports: [
    TranslatePipe,
    OutlineButtonComponent,
    DatePipe,
    NgClass,
  ],
  templateUrl: './payments-tab.component.html',
  styleUrl: './payments-tab.component.scss'
})
export class PaymentsTabComponent implements OnInit {
  onCancel = output();

  payments = signal<Payment[]>([]);
  currentPage = signal<number>(1);
  lastPage = signal<number>(1);
  perPage = signal<number>(5);
  localPage = signal<number>(1);
  localLastPage = signal<number>(1);
  loading = signal<boolean>(false);
  error = signal<string>('');

  constructor(
    private paymentService: PaymentService,
    private translate: TranslateService
  ) {}

  ngOnInit(): void {
    this.loadPage(1);
  }

  loadPage(page: number, targetLocalPage: number = 1) {
    if (page < 1 || (this.lastPage() && page > this.lastPage())) return;
    this.loading.set(true);
    this.error.set('');
    this.paymentService.listPayments(page, this.perPage())
      .subscribe({
        next: (res: PaginatedResponse<Payment>) => {
          this.payments.set(res.data);
          this.currentPage.set(res.current_page);
          this.lastPage.set(res.last_page);
          // Keep UI page size to 5 regardless of backend page size
          this.perPage.set(5);
          this.localLastPage.set(Math.max(1, Math.ceil(this.payments().length / this.perPage())));
          if (targetLocalPage === -1) {
            this.localPage.set(this.localLastPage());
          } else {
            this.localPage.set(targetLocalPage);
          }
          this.loading.set(false);
        },
        error: () => {
          this.error.set('failed_to_load_payments');
          this.loading.set(false);
        }
      });
  }

  displayedPayments(): Payment[] {
    const start = (this.localPage() - 1) * this.perPage();
    const end = start + this.perPage();
    return this.payments().slice(start, end);
  }

  nextClicked() {
    if (this.localPage() < this.localLastPage()) {
      this.localPage.set(this.localPage() + 1);
      return;
    }
    if (this.currentPage() < this.lastPage()) {
      this.loadPage(this.currentPage() + 1, 1);
    }
  }

  prevClicked() {
    if (this.localPage() > 1) {
      this.localPage.set(this.localPage() - 1);
      return;
    }
    if (this.currentPage() > 1) {
      this.loadPage(this.currentPage() - 1, -1); // go to last local page of previous backend page
    }
  }

  /**
   * Get translated payment status
   */
  getPaymentStatus(status: string): string {
    const translationKey = `payment_status.${status.toLowerCase()}`;
    const translation = this.translate.instant(translationKey);
    
    // If translation doesn't exist, return the original status
    if (translation === translationKey) {
      return status;
    }
    
    return translation;
  }

  /**
   * Get translated payment method/company
   */
  getPaymentMethod(method: string): string {
    if (!method) return '-';
    
    const translationKey = `payment_method.${method.toLowerCase()}`;
    const translation = this.translate.instant(translationKey);
    
    // If translation doesn't exist, return the original method
    if (translation === translationKey) {
      return method;
    }
    
    return translation;
  }
}


