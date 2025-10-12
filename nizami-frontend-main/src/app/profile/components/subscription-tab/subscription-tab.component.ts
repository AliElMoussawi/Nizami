import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslatePipe } from '@ngx-translate/core';
import { marker } from '@colsen1991/ngx-translate-extract-marker';
import { Dialog } from '@angular/cdk/dialog';
import { SubscriptionService } from '../../services/subscription.service';
import { UserSubscription } from '../../models/subscription.model';
import { UpgradePlansDialogComponent } from '../upgrade-plans-dialog/upgrade-plans-dialog.component';

@Component({
  selector: 'app-subscription-tab',
  standalone: true,
  imports: [CommonModule, TranslatePipe],
  templateUrl: './subscription-tab.component.html',
  styleUrl: './subscription-tab.component.scss'
})
export class SubscriptionTabComponent implements OnInit {
  activeSubscription = signal<UserSubscription | null>(null);
  isLoading = signal(false);
  error = signal<string | null>(null);

  constructor(
    private subscriptionService: SubscriptionService,
    private dialog: Dialog
  ) {}

  ngOnInit() {
    this.loadActiveSubscription();
  }

  loadActiveSubscription() {
    this.isLoading.set(true);
    this.error.set(null);

    this.subscriptionService.getActiveSubscription().subscribe({
      next: (subscription: UserSubscription) => {
        this.activeSubscription.set(subscription);
        this.isLoading.set(false);
      },
      error: (error: any) => {
        this.error.set(error.message || 'Failed to load subscription');
        this.isLoading.set(false);
      }
    });
  }

  formatPrice(priceCents: number, currency: string): string {
    return this.subscriptionService.formatPrice(priceCents, currency);
  }

  formatInterval(intervalCount: number, intervalUnit: string): string {
    return this.subscriptionService.formatInterval(intervalCount, intervalUnit);
  }

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }

  openUpgradePlansDialog() {
    this.dialog.open(UpgradePlansDialogComponent, {
      width: '100vw',
      height: '100vh',
      maxWidth: '100vw',
      maxHeight: '100vh',
      panelClass: 'full-screen-dialog'
    });
  }

  get marker() {
    return marker;
  }
}
