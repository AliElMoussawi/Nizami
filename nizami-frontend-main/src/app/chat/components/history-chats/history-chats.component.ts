import {Component, input, output} from '@angular/core';
import {HistoryChatItemComponent} from '../history-chat-item/history-chat-item.component';
import {ChatModel} from '../../models/chat.model';
import {ActivatedRoute} from '@angular/router';
import {UntilDestroy, untilDestroyed} from '@ngneat/until-destroy';
import {SpinnerComponent} from '../../../common/components/spinner/spinner.component';
import {ButtonComponent} from '../../../common/components/button/button.component';
import {HistoryChatsService} from '../../services/history-chats.service';
import {heroUser} from '@ng-icons/heroicons/outline';
import {NgClass} from '@angular/common';
import {TranslatePipe} from '@ngx-translate/core';

@UntilDestroy()
@Component({
  selector: 'app-history-chats',
  imports: [
    HistoryChatItemComponent,
    SpinnerComponent,
    ButtonComponent,
    NgClass,
    TranslatePipe,
  ],
  templateUrl: './history-chats.component.html',
  styleUrl: './history-chats.component.scss'
})
export class HistoryChatsComponent {
  onViewChat = output<ChatModel>();
  onDeleteChat = output<ChatModel>();
  alwaysShowActions = input(false);
  hasScrollBar = input(false);
  selected_id = null;
  protected readonly heroUser = heroUser;

  constructor(
    private route: ActivatedRoute,
    public historyChats: HistoryChatsService,
  ) {
    this.route.params
      .pipe(
        untilDestroyed(this),
      )
      .subscribe((x) => {
        this.selected_id = x['id'] ?? null;
      });
  }

  onLoadMore() {
    this.historyChats.loadMore();
  }

  viewChat(chat: ChatModel) {
    this.onViewChat.emit(chat);
  }

  deleteChat(chat: ChatModel) {
    this.historyChats.deleteChat(chat);

    this.onDeleteChat.emit(chat);
  }

  search(value: string) {
    this.historyChats.search(value);
  }
}
