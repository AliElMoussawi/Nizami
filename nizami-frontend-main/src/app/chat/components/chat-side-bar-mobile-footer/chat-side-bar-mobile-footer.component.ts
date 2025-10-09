import {Component, input} from '@angular/core';
import {AuthService} from '../../../auth/services/auth.service';
import {TitleCasePipe} from '@angular/common';
import {UserProfileImageComponent} from '../../../common/components/user-profile-image/user-profile-image.component';
import {CdkMenuTrigger} from '@angular/cdk/menu';
import {ProfileMenuComponent} from '../profile-menu/profile-menu.component';

@Component({
  selector: 'app-chat-side-bar-mobile-footer',
  imports: [
    TitleCasePipe,
    UserProfileImageComponent,
    CdkMenuTrigger,
    ProfileMenuComponent,
  ],
  templateUrl: './chat-side-bar-mobile-footer.component.html',
  styleUrl: './chat-side-bar-mobile-footer.component.scss'
})
export class ChatSideBarMobileFooterComponent {
  showEmail = input<boolean>(true);
  shouldOpenProfileSettingsDialog = input<boolean>(false);

  constructor(
    private auth: AuthService,
  ) {
  }

  user() {
    return this.auth.user();
  }
}
