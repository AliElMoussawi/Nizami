import { Component, Inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslatePipe } from '@ngx-translate/core';
import { marker } from '@colsen1991/ngx-translate-extract-marker';
import { DialogRef } from '@angular/cdk/dialog';
import { PlansService } from '../../services/plans.service';
import { Plan } from '../../models/plan.model';

@Component({
  selector: 'app-upgrade-plans-dialog',
  standalone: true,
  imports: [CommonModule, TranslatePipe],
  templateUrl: './upgrade-plans-dialog.component.html',
  styleUrl: './upgrade-plans-dialog.component.scss'
})
export class UpgradePlansDialogComponent implements OnInit {
  availablePlans = signal<Plan[]>([]);
  isLoading = signal(false);
  error = signal<string | null>(null);

  constructor(
    @Inject(DialogRef) public dialogRef: DialogRef<any>,
    private plansService: PlansService
  ) {}

  ngOnInit() {
    this.loadAvailablePlans();
  }

  loadAvailablePlans() {
    this.isLoading.set(true);
    this.error.set(null);

    this.plansService.getAvailableUpgradePlans().subscribe({
      next: (plans: Plan[]) => {
        this.availablePlans.set(plans);
        this.isLoading.set(false);
      },
      error: (error: any) => {
        this.error.set(error.message || 'Failed to load upgrade plans');
        this.isLoading.set(false);
      }
    });
  }

  formatPrice(priceCents: number, currency: string): string {
    return this.plansService.formatPrice(priceCents, currency);
  }

  formatInterval(intervalCount: number, intervalUnit: string): string {
    return this.plansService.formatInterval(intervalCount, intervalUnit);
  }

  onUpgradeClick(plan: Plan) {
    this.plansService.onUpgradeClick(plan);
  }

  close() {
    this.dialogRef.close();
  }

  get marker() {
    return marker;
  }
}
