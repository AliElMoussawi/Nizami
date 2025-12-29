import {Component, output, viewChild} from '@angular/core';
import {ChatModel} from '../../models/chat.model';
import {ChatSideBarService} from '../../services/chat-side-bar.service';
import {HistoryChatsComponent} from '../history-chats/history-chats.component';
import {ChatSearchComponent} from '../chat-search/chat-search.component';
import {animate, state, style, transition, trigger} from '@angular/animations';
import {ChatSideBarMobileHeaderComponent} from '../chat-side-bar-mobile-header/chat-side-bar-mobile-header.component';
import {ChatSideBarMobileFooterComponent} from '../chat-side-bar-mobile-footer/chat-side-bar-mobile-footer.component';
import {TranslatePipe} from '@ngx-translate/core';

@Component({
  selector: 'app-mobile-chat-side-bar',
  imports: [
    ChatSearchComponent,
    HistoryChatsComponent,
    ChatSideBarMobileHeaderComponent,
    ChatSideBarMobileFooterComponent,
    TranslatePipe
  ],
  animations: [
    trigger('slideInOut', [
      state('closed', style({transform: 'translateX(100%)', visibility: 'hidden'})),
      state('open', style({transform: 'translateX(0)', visibility: 'visible'})),
      transition('closed <=> open', animate('300ms ease-in-out'))
    ]),
  ],
  templateUrl: './mobile-chat-side-bar.component.html',
  styleUrl: './mobile-chat-side-bar.component.scss'
})
export class MobileChatSideBarComponent {
  onViewChat = output<ChatModel>();
  onDeleteChat = output<ChatModel>();
  historyChats = viewChild(HistoryChatsComponent);
  onNewChat = output();

  constructor(
    public sidebar: ChatSideBarService,
  ) {
  }

  onAnimationDone(_$event: any) {
    // this.sidebar.showCollapsedContent.set(!this.sidebar.isOpen());
  }

  viewChat($event: ChatModel) {
    this.sidebar.close();
    this.onViewChat.emit($event);
  }

  deleteChat($event: ChatModel) {
    this.sidebar.close();
    this.onDeleteChat.emit($event);
  }

  search(value: string) {
    if (!this.historyChats()) {
      return;
    }

    this.historyChats()?.search(value);
  }
}
