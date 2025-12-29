import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { CommonModule, LowerCasePipe } from '@angular/common';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';
import { PaymentService } from '../../services/payment.service';
import { AuthService } from '../../../auth/services/auth.service';
import { Plan } from '../../models/plan.model';
import { environment } from '../../../../environments/environment';
import { SpinnerComponent } from '../../../common/components/spinner/spinner.component';
import { ErrorComponent } from '../../../common/components/error/error.component';

declare let Moyasar: any;

@Component({
  selector: 'app-payment',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    TranslatePipe,
    LowerCasePipe,
    SpinnerComponent,
    ErrorComponent
  ],
  templateUrl: './payment.component.html',
  styleUrls: ['./payment.component.scss']
})
export class PaymentComponent implements OnInit, OnDestroy {
  plan: Plan | null = null;
  loading = true;
  error: string | null = null;
  moyasarInstance: any = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private paymentService: PaymentService,
    private authService: AuthService,
    private translate: TranslateService
  ) {}

  ngOnInit() {
    const planId = this.route.snapshot.paramMap.get('planId');
    
    if (!planId) {
      this.error = 'Plan ID is required';
      this.loading = false;
      return;
    }

    this.loadPlanAndInitMoyasar(planId);
  }

  ngOnDestroy() {
    if (this.moyasarInstance) {
      this.moyasarInstance = null;
    }
  }

  private loadPlanAndInitMoyasar(planId: string) {
    this.paymentService.getPlan(planId).subscribe({
      next: (plan: Plan) => {
        this.plan = plan;
        this.loading = false;
        this.initMoyasar();
      },
      error: (err: any) => {
        this.error = 'Failed to load plan details';
        this.loading = false;
        console.error('Error loading plan:', err);
      }
    });
  }

  private initMoyasar() {
    if (!this.plan) return;

    // Wait for user data to load if it's still loading
    if (this.authService.isLoadingUser()) {
      // Wait a bit and try again
      setTimeout(() => {
        this.initMoyasar();
      }, 100);
      return;
    }

    const user = this.authService.user();
    const userId = user?.id;

    // Ensure user is authenticated before initializing payment
    if (!userId) {
      console.error('User ID is required for payment');
      this.error = 'User authentication required. Please log in again.';
      // Redirect to login and let the user authenticate
      this.router.navigate(['/login']);
      return;
    }

    const baseUrl = environment.production ? 'https://app.nizami.ai' : 'http://localhost:4201';

    setTimeout(() => {
      try {
        this.moyasarInstance = Moyasar.init({
          element: '.mysr-form',
          amount: this.plan!.price_cents,
          currency: this.plan!.currency,
          description: this.plan!.description || `${this.plan!.name} Subscription`,
          publishable_api_key: environment.moyasarPublishableKey,
          callback_url: `${baseUrl}/payment/callback`,
          supported_networks: ['visa', 'mastercard', 'mada'],
          methods: ['creditcard'],
          credit_card:{
            save_card: true
          },
          metadata: {
            user_id: userId.toString(),
            plan_id: this.plan!.uuid
          }
        });
        
        console.log('Moyasar initialized successfully');
      } catch (err) {
        console.error('Error initializing Moyasar:', err);
        this.error = 'Failed to load payment form. Please refresh and try again.';
      }
    }, 100);
  }

  /**
   * Get translated billing interval
   */
  getBillingInterval(interval: string | null): string {
    if (!interval) return '';
    
    const translationKey = `billing_interval.${interval.toLowerCase()}`;
    const translation = this.translate.instant(translationKey);
    
    // If translation doesn't exist, return the original interval
    if (translation === translationKey) {
      return interval;
    }
    
    return translation;
  }
}

