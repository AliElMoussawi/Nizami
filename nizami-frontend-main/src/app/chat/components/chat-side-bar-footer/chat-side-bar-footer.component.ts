import {Component} from '@angular/core';
import {AuthService} from '../../../auth/services/auth.service';
import {TitleCasePipe} from '@angular/common';
import {UserProfileImageComponent} from '../../../common/components/user-profile-image/user-profile-image.component';

@Component({
  selector: 'app-chat-side-bar-footer',
  imports: [
    TitleCasePipe,
    UserProfileImageComponent
  ],
  templateUrl: './chat-side-bar-footer.component.html',
  styleUrl: './chat-side-bar-footer.component.scss'
})
export class ChatSideBarFooterComponent {
  constructor(
    private auth: AuthService,
  ) {
  }


  user() {
    return this.auth.user();
  }

  logout() {
    this.auth.logout();
  }
}
