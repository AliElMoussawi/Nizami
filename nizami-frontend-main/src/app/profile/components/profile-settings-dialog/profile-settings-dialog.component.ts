import {Component, Inject, signal} from '@angular/core';
import {TabsButtonComponent} from '../../../common/components/tabs-button/tabs-button.component';
import {AccountDetailsTabComponent} from '../account-details-tab/account-details-tab.component';
import {UpdatePasswordTabComponent} from '../update-password-tab/update-password-tab.component';
import {PersonalDetailsTabComponent} from '../personal-details-tab/personal-details-tab.component';
import {PlansTabComponent} from '../plans-tab/plans-tab.component';
import {CurrentPlanTabComponent} from '../current-plan-tab/current-plan-tab.component';
import {DialogRef} from '@angular/cdk/dialog';
import {TranslatePipe} from '@ngx-translate/core';
import {marker} from '@colsen1991/ngx-translate-extract-marker';

@Component({
  selector: 'app-profile-settings-dialog',
  imports: [
    TabsButtonComponent,
    AccountDetailsTabComponent,
    UpdatePasswordTabComponent,
    PersonalDetailsTabComponent,
    PlansTabComponent,
    CurrentPlanTabComponent,
    TranslatePipe,
  ],
  templateUrl: './profile-settings-dialog.component.html',
  styleUrl: './profile-settings-dialog.component.scss'
})
export class ProfileSettingsDialogComponent {
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
      id: Tabs.Password,
      title: marker('password'),
    },
  ];

  constructor(
    @Inject(DialogRef) public dialogRef: DialogRef<any>,
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
    this.dialogRef.close();
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
}
