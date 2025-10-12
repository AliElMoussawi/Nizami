import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { Plan, PlansResponse } from '../models/plan.model';
import { AuthService } from '../../auth/services/auth.service';
import { catchError, EMPTY, map } from 'rxjs';
import { ToastrService } from 'ngx-toastr';
import { TranslateService } from '@ngx-translate/core';
import { marker } from '@colsen1991/ngx-translate-extract-marker';

@Injectable({
  providedIn: 'root'
})
export class PlansService {
  availablePlans = signal<Plan[]>([]);
  isLoading = signal(false);
  error = signal<string | null>(null);

  constructor(
    private http: HttpClient,
    private auth: AuthService,
    private toastr: ToastrService,
    private translate: TranslateService
  ) {}

  getAvailableUpgradePlans() {
    this.isLoading.set(true);
    this.error.set(null);

    return this.http.get<PlansResponse>(
      environment.apiUrl + '/v1/plans/available-for-upgrade',
      {
        headers: {
          'Authorization': 'Bearer ' + this.auth.getToken()!,
        },
      }
    ).pipe(
      map((response: PlansResponse) => {
        this.availablePlans.set(response.data);
        this.isLoading.set(false);
        return response.data;
      }),
      catchError((error: any) => {
        this.error.set(error.message || 'Failed to load upgrade plans');
        this.isLoading.set(false);
        this.toastr.error(this.translate.instant(marker('errors.failed_to_load_upgrade_plans')));
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

  onUpgradeClick(plan: Plan) {
    // TODO: Implement upgrade functionality
    console.log('Upgrade to plan:', plan);
  }
}
