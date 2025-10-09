import {Component, output} from '@angular/core';
import {ChatSideBarService} from '../../services/chat-side-bar.service';
import {IconButtonComponent} from '../../../common/components/icon-button/icon-button.component';

@Component({
  selector: 'app-chat-side-bar-mobile-header',
  imports: [
    IconButtonComponent
  ],
  templateUrl: './chat-side-bar-mobile-header.component.html',
  styleUrl: './chat-side-bar-mobile-header.component.scss'
})
export class ChatSideBarMobileHeaderComponent {
  onNewChat = output();

  constructor(
    public sidebar: ChatSideBarService,
  ) {
  }

  toggleSidebar() {
    this.sidebar.toggle();
  }

  newChatClicked() {
    this.sidebar.close();
    this.onNewChat.emit();
  }
}
