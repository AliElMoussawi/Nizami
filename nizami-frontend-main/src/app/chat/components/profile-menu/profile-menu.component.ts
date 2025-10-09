import {Component, input} from '@angular/core';
import {CdkMenu, CdkMenuItem} from '@angular/cdk/menu';
import {AuthService} from '../../../auth/services/auth.service';
import {Dialog} from '@angular/cdk/dialog';
import {Router} from '@angular/router';
import {
  ProfileSettingsDialogComponent
} from '../../../profile/components/profile-settings-dialog/profile-settings-dialog.component';
import {take} from 'rxjs';
import {UntilDestroy, untilDestroyed} from '@ngneat/until-destroy';
import {TranslatePipe} from '@ngx-translate/core';

@UntilDestroy()
@Component({
  selector: 'app-profile-menu',
  imports: [
    CdkMenu,
    CdkMenuItem,
    TranslatePipe
  ],
  templateUrl: './profile-menu.component.html',
  styleUrl: './profile-menu.component.scss'
})
export class ProfileMenuComponent {
  showEmail = input<boolean>(true);
  shouldOpenProfileSettingsDialog = input<boolean>(false);

  constructor(
    private auth: AuthService,
    private dialog: Dialog,
    private router: Router,
  ) {
  }

  user() {
    return this.auth.user();
  }

  logout() {
    this.auth.logout();
  }

  openProfileSettingsDialog() {
    this.dialog.open(ProfileSettingsDialogComponent, {})
      .closed
      .pipe(
        take(1),
        untilDestroyed(this)
      )
      .subscribe((x) => {
      })
  }

  openProfileClicked() {
    if (this.shouldOpenProfileSettingsDialog()) {
      this.openProfileSettingsDialog();
      return;
    }

    this.navigate();
  }

  private navigate() {
    this.router.navigateByUrl('/profile-settings')
  }
}
