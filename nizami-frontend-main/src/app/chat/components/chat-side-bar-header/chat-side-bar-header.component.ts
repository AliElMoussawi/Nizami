import {Component} from '@angular/core';
import {ChatSideBarService} from '../../services/chat-side-bar.service';
import {IconButtonComponent} from '../../../common/components/icon-button/icon-button.component';

@Component({
  selector: 'app-chat-side-bar-header',
  imports: [
    IconButtonComponent
  ],
  templateUrl: './chat-side-bar-header.component.html',
  styleUrl: './chat-side-bar-header.component.scss'
})
export class ChatSideBarHeaderComponent {
  constructor(
    public sidebar: ChatSideBarService,
  ) {
  }

  toggleSidebar() {
    this.sidebar.toggle();
  }
}
