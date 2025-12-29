import {Component, effect, ElementRef, output, signal, viewChild} from '@angular/core';
import {ChatSideBarHeaderComponent} from '../chat-side-bar-header/chat-side-bar-header.component';
import {HistoryChatsComponent} from '../history-chats/history-chats.component';
import {ChatSideBarService} from '../../services/chat-side-bar.service';
import {ChatSearchComponent} from '../chat-search/chat-search.component';
import {animate, state, style, transition, trigger} from '@angular/animations';
import {ChatModel} from '../../models/chat.model';
import {UserProfileImageComponent} from '../../../common/components/user-profile-image/user-profile-image.component';
import {HistoryChatsService} from '../../services/history-chats.service';
import {ChatSideBarMobileFooterComponent} from '../chat-side-bar-mobile-footer/chat-side-bar-mobile-footer.component';
import {TranslatePipe} from '@ngx-translate/core';

@Component({
  selector: 'app-chat-side-bar',
  imports: [
    ChatSideBarHeaderComponent,
    HistoryChatsComponent,
    ChatSearchComponent,
    UserProfileImageComponent,
    ChatSideBarMobileFooterComponent,
    TranslatePipe
  ],
  animations: [
    /*
        trigger('slideInOut', [
          state('closed', style({width: '0', overflow: 'hidden'})),
          state('open', style({width: '20rem'})),
          transition('closed <=> open', animate('300ms ease-in-out'))
        ]),
    */
    trigger('slideInOut', [
      state('closed', style({transform: 'translateX(100%)', visibility: 'hidden'})),
      state('open', style({transform: 'translateX(0)', visibility: 'visible'})),
      transition('closed <=> open', animate('300ms ease-in-out'))
    ])
  ],
  templateUrl: './chat-side-bar.component.html',
  styleUrl: './chat-side-bar.component.scss'
})
export class ChatSideBarComponent {
  hc = viewChild<ElementRef>('hc');

  onViewChat = output<ChatModel>();
  onDeleteChat = output<ChatModel>();
  historyChats = viewChild(HistoryChatsComponent);
  hasScrollBar = signal(false);

  constructor(
    public sidebar: ChatSideBarService,
    private historyChatService: HistoryChatsService,
  ) {
    effect(() => {
      this.setHasScrollbar();
    });
  }

  onAnimationDone(_$event: any) {
    // this.sidebar.showCollapsedContent.set(!this.sidebar.isOpen());
  }

  viewChat($event: ChatModel) {
    this.onViewChat.emit($event);
  }

  deleteChat($event: ChatModel) {
    this.onDeleteChat.emit($event);
  }

  search(value: string) {
    if (!this.historyChats()) {
      return;
    }

    this.historyChats()?.search(value);
  }

  private setHasScrollbar() {
    if (this.hasScrollBar()) {
      return;
    }

    if (this.historyChatService.isLoading()) {
      return;
    }

    setTimeout(() => {
      this.hasScrollBar.set(this.detectScrollBar());
    });
  }

  private detectScrollBar() {
    const el = this.hc()!.nativeElement;
    return el.scrollHeight > el.clientHeight;
  }
}
