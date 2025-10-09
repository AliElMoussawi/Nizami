import {Component, signal} from '@angular/core';
import {TemplateComponent} from '../../../common/components/template/template.component';
import {DashboardCardComponent} from '../dashboard-card/dashboard-card.component';
import {NgIcon} from '@ng-icons/core';
import {DashboardService} from '../../services/dashboard.service';
import {finalize} from 'rxjs';
import {UntilDestroy, untilDestroyed} from '@ngneat/until-destroy';
import {DashboardCardModel} from '../../models/dashboard-card.model';

@UntilDestroy()
@Component({
  selector: 'app-dashboard',
  imports: [
    TemplateComponent,
    DashboardCardComponent,
    NgIcon
  ],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent {
  isLoading = signal<boolean>(true);
  cards = signal<DashboardCardModel[]>([]);

  constructor(
    private dashboard: DashboardService,
  ) {
    this.dashboard
      .loadCards()
      .pipe(
        untilDestroyed(this),
        finalize(() => {
          this.isLoading.set(false);
        }),
      )
      .subscribe((cards) => {
        this.cards.set(cards);
      });
  }
}
