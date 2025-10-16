import {Component, signal} from '@angular/core';
import {AccountDetailsTabComponent} from '../account-details-tab/account-details-tab.component';
import {UpdatePasswordTabComponent} from '../update-password-tab/update-password-tab.component';
import {PersonalDetailsTabComponent} from '../personal-details-tab/personal-details-tab.component';
import {PlansTabComponent} from '../plans-tab/plans-tab.component';
import {CurrentPlanTabComponent} from '../current-plan-tab/current-plan-tab.component';
import {PaymentsTabComponent} from '../payments-tab/payments-tab.component';
import {NgIcon} from '@ng-icons/core';
import {Location} from '@angular/common';
import {ButtonToggleComponent} from '../../../common/components/button-toggle/button-toggle.component';
import {ButtonToggleGroupComponent} from '../../../common/components/button-toggle-group/button-toggle-group.component';
import {TranslatePipe} from '@ngx-translate/core';
import {marker} from '@colsen1991/ngx-translate-extract-marker';

@Component({
  selector: 'app-profile-settings-mobile',
  imports: [
    AccountDetailsTabComponent,
    UpdatePasswordTabComponent,
    PersonalDetailsTabComponent,
    PlansTabComponent,
    CurrentPlanTabComponent,
    PaymentsTabComponent,
    NgIcon,
    ButtonToggleComponent,
    ButtonToggleGroupComponent,
    TranslatePipe
  ],
  templateUrl: './profile-settings-mobile.component.html',
  styleUrl: './profile-settings-mobile.component.scss'
})
export class ProfileSettingsMobileComponent {
  selectedTabId = signal<string | null>(null);

  tabs: Tab[] = [
    {
      id: Tabs.AccountDetails,
      title: marker('account_details'),
    },
    {
      id: Tabs.Personal,
      title: marker('profile'),
    },
    {
      id: Tabs.CurrentPlan,
      title: marker('current_plan'),
    },
    {
      id: Tabs.Plans,
      title: marker('plans'),
    },
    {
      id: Tabs.Payments,
      title: marker('payments'),
    },
    {
      id: Tabs.Password,
      title: marker('password'),
    }
  ];

  constructor(
    private location: Location,
  ) {
    this.selectedTabId.set(Tabs.AccountDetails);
  }

  get allTabs(): typeof Tabs {
    return Tabs;
  }

  selectTab(tab: Tab) {
    this.selectedTabId.set(tab.id);
  }

  close() {
    this.location.back();
  }

  back() {
    this.location.back();
  }
}

export interface Tab {
  id: Tabs;
  title: string;
}

export enum Tabs {
  AccountDetails = 'account-details',
  Personal = 'personal',
  CurrentPlan = 'current-plan',
  Password = 'password',
  Plans = 'plans',
  Payments = 'payments',
}
