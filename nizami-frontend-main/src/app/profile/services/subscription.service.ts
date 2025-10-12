import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { UserSubscription } from '../models/subscription.model';
import { AuthService } from '../../auth/services/auth.service';
import { catchError, EMPTY, map } from 'rxjs';
import { ToastrService } from 'ngx-toastr';
import { TranslateService } from '@ngx-translate/core';
import { marker } from '@colsen1991/ngx-translate-extract-marker';

@Injectable({
  providedIn: 'root'
})
export class SubscriptionService {
  activeSubscription = signal<UserSubscription | null>(null);
  isLoading = signal(false);
  error = signal<string | null>(null);

  constructor(
    private http: HttpClient,
    private auth: AuthService,
    private toastr: ToastrService,
    private translate: TranslateService
  ) {}

  getActiveSubscription() {
    this.isLoading.set(true);
    this.error.set(null);

    return this.http.get<UserSubscription>(
      environment.apiUrl + '/v1/subscriptions/active',
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      }
    ).pipe(
      map((response: any) => {
        this.activeSubscription.set(response);
        this.isLoading.set(false);
        return response;
      }),
      catchError((error: { message: any; }) => {
        this.error.set(error.message || 'Failed to load subscription');
        this.isLoading.set(false);
        this.toastr.error(this.translate.instant(marker('errors.failed_to_load_subscription')));
        return EMPTY;
      })
    );
  }

  formatPrice(priceCents: number, currency: string): string {
    const price = priceCents / 100;
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency.toUpperCase()
    }).format(price);
  }

  formatInterval(intervalCount: number, intervalUnit: string): string {
    if (intervalCount === 1) {
      return intervalUnit;
    }
    return `${intervalCount} ${intervalUnit}s`;
  }
}
