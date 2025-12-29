import {Component, input} from '@angular/core';
import {TitleCasePipe} from '@angular/common';
import {environment} from '../../../../environments/environment';
import {AuthService} from '../../../auth/services/auth.service';
import {Dialog} from '@angular/cdk/dialog';
import {
  ProfileSettingsDialogComponent
} from '../../../profile/components/profile-settings-dialog/profile-settings-dialog.component';
import {UntilDestroy, untilDestroyed} from '@ngneat/until-destroy';
import {take} from 'rxjs';
import {ProfileMenuComponent} from '../../../chat/components/profile-menu/profile-menu.component';
import {CdkMenuTrigger} from '@angular/cdk/menu';

@UntilDestroy()
@Component({
  selector: 'app-user-profile-image',
  imports: [
    TitleCasePipe,
    ProfileMenuComponent,
    CdkMenuTrigger
  ],
  templateUrl: './user-profile-image.component.html',
  styleUrl: './user-profile-image.component.scss'
})
export class UserProfileImageComponent {
  disabled = input(false);
  showEmail = input<boolean>(true);
  shouldOpenProfileSettingsDialog = input<boolean>(false);

  constructor(
    private auth: AuthService,
    private dialog: Dialog,
  ) {
  }

  get profileImageUrl() {
    return environment.baseUrl + this.auth.user()?.profile_image;
  }

  user() {
    return this.auth.user();
  }

  clicked() {
    if (this.disabled()) {
      return;
    }

    this.openDialog();
  }

  openDialog() {
    this.dialog.open(ProfileSettingsDialogComponent, {})
      .closed
      .pipe(
        take(1),
        untilDestroyed(this)
      )
      .subscribe(() => {
      })
  }
}
