import {Injectable, signal} from '@angular/core';
import {ChatModel} from '../models/chat.model';
import {catchError, EMPTY, finalize} from 'rxjs';
import {MessagesService} from './messages.service';
import {ToastrService} from 'ngx-toastr';
import {marker} from '@colsen1991/ngx-translate-extract-marker';
import {TranslateService} from '@ngx-translate/core';

const DAYS_AGO_MSG = marker('DAYS_AGO');
const MONTHS_AGO_MSG = marker('MONTHS_AGO');
const YEARS_AGO_MSG = marker('YEARS_AGO');

@Injectable({
  providedIn: 'root',
})
export class HistoryChatsService {
  selectedChat = signal<ChatModel | null>(null);
  chats = signal<ChatModel[]>([]);
  page = signal<number>(1);
  isLoading = signal<boolean>(false);
  searchValue = signal<string | null>(null);
  error = signal<any>(null);
  hasMorePages = signal<boolean>(true);

  constructor(
    private messages: MessagesService,
    private toastr: ToastrService,
    private translate: TranslateService,
  ) {
  }

  addChat(chat: ChatModel) {
    this.chats.update((chats) => [
      {
        ...chat,
        relative_date: this.getRelativeTime(new Date(Date.parse(chat.created_at))),
      },
      ...chats,
    ]);
  }

  deleteChat(chat: ChatModel) {
    this.chats.update((chats) => chats.filter((item) => item.id != chat.id));
  }

  search(value: string) {
    this.searchValue.set(value);
    this.page.set(1);
    this.chats.set([]);

    this.loadChats(this.page(), value);
  }


  load() {
    this.loadChats(this.page());
  }

  loadChats(page: any, search: string | null = null) {
    this.isLoading.set(true);
    this.error.set(null);

    this.messages
      .getChats(search, page)
      .pipe(
        catchError((e) => {
          this.error.set(e);
          this.toastr.error(this.translate.instant(marker('errors.failed_to_load_chats')));

          return EMPTY;
        }),
        finalize(() => {
          this.isLoading.set(false);
        }),
      )
      .subscribe((r) => {
        this.page.set(r.current_page);
        this.hasMorePages.set(r.current_page < r.last_page);

        const new_data = r.data.map((item) => {
          return {
            ...item,
            relative_date: this.getRelativeTime(new Date(Date.parse(item.created_at))),
          };
        });

        this.chats.update((chats) => [
          ...chats,
          ...new_data,
        ]);
      });
  }

  getRelativeTime(date: Date): string {
    const now = new Date();
    const timeDiff = now.getTime() - date.getTime();
    const diffInDays = Math.floor(timeDiff / (1000 * 3600 * 24));

    if (diffInDays < 1) {
      return this.translate.instant(marker('TODAY'));
    } else if (diffInDays === 1) {
      return this.translate.instant(marker('YESTERDAY'));
    } else if (diffInDays < 30) {
      return this.translate.instant(DAYS_AGO_MSG, {
        days: diffInDays,
      });
    } else if (diffInDays < 365) {
      return this.translate.instant(MONTHS_AGO_MSG, {
        months: Math.floor(diffInDays / 30),
      });
    } else {
      return this.translate.instant(YEARS_AGO_MSG, {
        years: Math.floor(diffInDays / 365),
      });
    }
  }

  loadMore() {
    this.loadChats(this.page() + 1);
  }
}
