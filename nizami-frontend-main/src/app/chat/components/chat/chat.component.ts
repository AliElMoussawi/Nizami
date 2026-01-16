import {Component, signal, viewChild} from '@angular/core';
import {ChatInputComponent} from '../chat-input/chat-input.component';
import {ChatMessagesComponent} from '../chat-messages/chat-messages.component';
import {MessageModel} from '../../models/message.model';
import {MessagesService} from '../../services/messages.service';
import {UntilDestroy, untilDestroyed} from '@ngneat/until-destroy';
import {catchError, EMPTY, Subject, takeUntil} from 'rxjs';
import {v4 as uuid} from 'uuid';
import {ChatSideBarComponent} from '../chat-side-bar/chat-side-bar.component';
import {ChatModel} from '../../models/chat.model';
import {ChatHeaderComponent} from '../chat-header/chat-header.component';
import {ActivatedRoute, Router} from '@angular/router';
import {IsTypingService} from '../../services/is-typing.service';
import {MobileChatSideBarComponent} from '../mobile-chat-side-bar/mobile-chat-side-bar.component';
import {ChatSideBarService} from '../../services/chat-side-bar.service';
import {NgClass, NgStyle} from '@angular/common';
import {HistoryChatsService} from '../../services/history-chats.service';
import {marker} from '@colsen1991/ngx-translate-extract-marker';
import {TranslateService} from '@ngx-translate/core';
import {detectLanguage, extractErrorFromResponse} from '../../../common/utils';
import {CreditErrorPopupComponent} from '../../../common/components/credit-error-popup/credit-error-popup.component';
import {ToastrService} from 'ngx-toastr';
import {HttpErrorResponse} from '@angular/common/http';


@UntilDestroy()
@Component({
  selector: 'app-chat',
  imports: [
    ChatInputComponent,
    ChatMessagesComponent,
    ChatSideBarComponent,
    ChatHeaderComponent,
    MobileChatSideBarComponent,
    NgClass,
    NgStyle,
    CreditErrorPopupComponent,
  ],
  providers: [
    MessagesService,
    IsTypingService,
    HistoryChatsService,
    ChatSideBarService,
  ],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.scss',
  standalone: true
})
export class ChatComponent {
  lastId = signal<number | null>(null);
  canLoadMore = signal<boolean>(true);

  chatMessages = viewChild<ChatMessagesComponent>('chatMessages');
  chatInput = viewChild<ChatInputComponent>('chatInput');
  sidebar = viewChild<ChatSideBarComponent>('sideBar');

  messages = signal<MessageModel[]>([]);
  isDisabled = signal<boolean>(false);

  isLoadingMessages = signal<boolean>(false);
  loadingError = signal<string | null>(null);

  isGeneratingResponse = signal<boolean>(false);
  error = signal<string | null>(null);
  submittingMessage = signal<MessageModel | null>(null);
  showCreditErrorPopup = signal<boolean>(false);
  creditErrorMessage = signal<string>('');

  stop$ = new Subject<void>();

  constructor(
    private messagesService: MessagesService,
    private router: Router,
    private route: ActivatedRoute,
    private isTypingService: IsTypingService,
    public sidebarService: ChatSideBarService,
    public historyChats: HistoryChatsService,
    private translate: TranslateService,
    private toastr: ToastrService,
  ) {
    const id = this.route.snapshot.params['id'] ?? null;
    if (id) {
      this.loadChat(id);
    } else {
      this.refreshMessages();
      this.isLoadingMessages.set(false);
    }

    this.historyChats.load();
  }

  get isNewChat() {
    return ((!this.messages() || this.messages().length == 0) && !this.isLoadingMessages() && !this.error() && !this.loadingError() && !this.isGeneratingResponse());
  }

  get chat() {
    return this.historyChats.selectedChat;
  }

  onNewMessage(message: MessageModel) {
    this.submittingMessage.set(message);

    this.isDisabled.set(true);
    this.isGeneratingResponse.set(true);
    this.error.set(null);

    if (this.chat()) {
      this.sendMessage(message);
      return;
    }

    this.messagesService
      .createChat(message.text)
      .pipe(
        takeUntil(this.stop$),
        untilDestroyed(this),
        catchError((err) => {
          const extracted = extractErrorFromResponse(err);
          if (typeof extracted === 'string' && extracted.startsWith('errors.')) {
            this.error.set(this.translate.instant(marker(extracted)));
          } else if (typeof extracted === 'string' && extracted.trim().length > 0) {
            this.error.set(extracted);
          } else {
            this.error.set(this.translate.instant(marker('errors.failed_creating_chat')));
          }
          this.isDisabled.set(false);
          this.isGeneratingResponse.set(false);

          this.scrollToErrorMessage();

          return EMPTY;
        }),
      )
      .subscribe((chat) => {
        this.chat.set(chat);
        this.historyChats.addChat(this.chat()!);

        this.sendMessage(message);

        this.router.navigateByUrl(`chat/${chat.id}`);
      });
  }

  scrollToLastMessage() {
    this.chatMessages()?.scrollToLastMessage();
  }

  scrollToBottom() {
    this.chatMessages()?.smoothScrollToBottom();
  }

  scrollToGeneratingMessage() {
    setTimeout(() => {
      this.chatMessages()?.scrollToGeneratingMessage();
    }, 100);
  }

  scrollToErrorMessage() {
    setTimeout(() => {
      this.chatMessages()?.scrollToErrorMessage();
    }, 100);
  }

  focusInput() {
    this.chatInput()?.focus();
  }

  viewChat(chat: ChatModel) {
    this.stop$.next();
    this.stop$.complete();

    this.refreshStop();
    this.router.navigateByUrl(`chat/${chat.id}`);

    this.chat.set(chat);
    this.isDisabled.set(true);
    this.error.set(null);
    this.lastId.set(null);
    this.loadingError.set(null);
    this.isLoadingMessages.set(false);
    this.isGeneratingResponse.set(false);
    this.submittingMessage.set(null);
    this.messages.set([]);
    this.canLoadMore.set(true);

    this.loadMessages();

  }

  deleteChat(chat: ChatModel) {
    if (chat.id == this.chat()?.id) {
      this.newChatClicked();
    }
  }

  newChatClicked() {
    this.stop$.next();
    this.stop$.complete();

    this.router.navigateByUrl('/chat');
    this.isGeneratingResponse.set(false);
    this.chat.set(null);
    this.isTypingService.stopTyping();
    this.isDisabled.set(false);
    this.refreshMessages();
    this.error.set(null);

    this.refreshStop();
  }

  requestLegalAssistance() {
    const currentChat = this.chat();
    if (!currentChat || !currentChat.id) {
      return;
    }

    this.messagesService
      .createLegalAssistanceRequest(currentChat.id)
      .pipe(
        untilDestroyed(this),
        catchError((err: HttpErrorResponse) => {
          // Check if it's a validation error (400 status)
          if (err.status === 400) {
            // Extract validation error message
            let errorMessage = '';
            
            if (err.error && typeof err.error === 'object') {
              // Handle DRF validation errors - could be field-specific or general
              const errorObj = err.error;
              
              // Check for field-specific errors (e.g., { chat_id: ['error message'] })
              const fieldErrors = Object.values(errorObj).flat();
              if (fieldErrors.length > 0 && typeof fieldErrors[0] === 'string') {
                errorMessage = fieldErrors[0] as string;
              } else if (errorObj.detail) {
                errorMessage = errorObj.detail;
              } else if (errorObj.error) {
                errorMessage = errorObj.error;
              } else {
                // Fallback to first value if it's a string
                const firstValue = Object.values(errorObj)[0];
                if (typeof firstValue === 'string') {
                  errorMessage = firstValue;
                } else if (Array.isArray(firstValue) && firstValue.length > 0) {
                  errorMessage = firstValue[0];
                }
              }
            } else if (typeof err.error === 'string') {
              errorMessage = err.error;
            }
            
            // Show yellow/warning toast for validation errors
            this.toastr.warning(
              errorMessage || this.translate.instant(marker('errors.validation_error')),
              '',
              { timeOut: 5000 }
            );
          } else {
            // Show red/error toast for other errors
            const extracted = extractErrorFromResponse(err);
            const errorMsg = typeof extracted === 'string' && extracted.startsWith('errors.')
              ? this.translate.instant(marker(extracted))
              : (extracted || this.translate.instant(marker('errors.something_went_wrong')));
            
            this.toastr.error(errorMsg, '', { timeOut: 5000 });
          }
          
          return EMPTY;
        }),
      )
      .subscribe((response) => {
        // Show green/success toast
        this.toastr.success(
          this.translate.instant(marker('success.legal_assistance_requested')),
          '',
          { timeOut: 5000 }
        );
      });
  }

  loadMessages(scrollToBottom = true) {
    if (!this.chat()) {
      return;
    }

    if (this.isLoadingMessages() || !this.canLoadMore()) {
      return;
    }

    this.isLoadingMessages.set(true);
    this.loadingError.set(null);

    this.scrollToGeneratingMessage();

    const currentHeight = this.chatMessages()?.chatContainer()?.nativeElement.scrollHeight ?? 0;
    const currentTop = this.chatMessages()?.chatContainer()?.nativeElement.scrollTop ?? 0;

    this.messagesService
      .loadMessages(this.chat()?.id, this.lastId())
      .pipe(
        untilDestroyed(this),
        takeUntil(this.stop$),
        catchError(() => {
          this.loadingError.set("Failed loading the messages!");
          this.isDisabled.set(false);

          this.scrollToErrorMessage();

          return EMPTY;
        }),
      )
      .subscribe((response) => {
        this.canLoadMore.set(response.data && response.data.length > 0);

        this.messages.update((old) => [...response.data, ...old]);

        this.lastId.set(response.last_id);

        this.loadingError.set(null);
        this.isDisabled.set(false);
        this.isLoadingMessages.set(false);

        if (scrollToBottom) {
          this.finalizeAnswering();
        } else {
          setTimeout(() => {
            const newHeight = this.chatMessages()?.chatContainer()?.nativeElement.scrollHeight ?? 0;
            if (this.chatMessages()?.chatContainer()) {
              this.chatMessages()!.chatContainer()!.nativeElement.scrollTop = newHeight - currentHeight + currentTop;
            }
          }, 1);
        }
      });

  }

  onScroll() {
    this.loadMessages(false);
  }

  refreshStop() {
    this.stop$ = new Subject();
  }

  private sendMessage(message: MessageModel) {
    if (message.uuid == null) {
      message = {
        ...message,

        language: detectLanguage(message.text),
        message_file_ids: message.messageFiles?.map((file) => file.id),
        uuid: uuid(),
        chat_id: this.chat()?.id,
        role: 'user',
      };

      this.submittingMessage.set(message);

      this.messages.update((current) => [
        ...(current ?? []),
        message,
      ]);
    }

    this.scrollToGeneratingMessage();

    this.messagesService
      .sendMessage(message)
      .pipe(
        untilDestroyed(this),
        takeUntil(this.stop$),
        catchError((err) => {
          const extracted = extractErrorFromResponse(err);
          
          // Define all ledger enum error types that should show popup
          const popupErrorTypes = [
            'errors.user_inactive',
            'errors.subscription_not_found',
            'errors.subscription_multiple_active',
            'errors.subscription_expired',
            'errors.subscription_inactive',
            'errors.no_message_credits'
          ];
          
          // Check if it's a ledger error and show popup instead of inline error
          if (typeof extracted === 'string' && popupErrorTypes.includes(extracted)) {
            this.creditErrorMessage.set(this.translate.instant(marker(extracted)));
            this.showCreditErrorPopup.set(true);
            this.isDisabled.set(false);
            this.isGeneratingResponse.set(false);
            return EMPTY;
          }
          
          // Handle other errors normally
          if (typeof extracted === 'string' && extracted.startsWith('errors.')) {
            this.error.set(this.translate.instant(marker(extracted)));
          } else if (typeof extracted === 'string' && extracted.trim().length > 0) {
            this.error.set(extracted);
          } else {
            this.error.set(this.translate.instant(marker('errors.failed_generating_response')));
          }
          this.isDisabled.set(false);
          this.isGeneratingResponse.set(false);

          this.scrollToErrorMessage();

          return EMPTY;
        }),
      )
      .subscribe((response) => {

        this.messages.update((current) => [
          ...current,
          {
            ...response,
            role: "system",
          }
        ]);

        this.isTypingService.startTyping();
        this.error.set(null);
        this.isDisabled.set(false);
        this.isGeneratingResponse.set(false);
        this.submittingMessage.set(null);

        this.finalizeAnswering();
      });
  }

  private finalizeAnswering() {
    setTimeout(() => {
      this.scrollToBottom();
      this.focusInput();
    }, 100);
  }

  private loadChat(id: any) {
    this.messages.set([]);
    this.isDisabled.set(true);
    this.loadingError.set(null);

    this.messagesService
      .loadChat(id)
      .pipe(
        untilDestroyed(this),
        takeUntil(this.stop$),
        catchError((_e) => {
          this.loadingError.set(this.translate.instant(marker('errors.failed_loading_chat')));

          return EMPTY;
        }),
      )
      .subscribe((chat) => {
        this.chat.set(chat);

        this.loadingError.set(null);

        this.loadMessages();
      });
  }

  private refreshMessages() {
    this.messages.set([]);
  }

  // Credit error popup handlers
  closeCreditErrorPopup() {
    this.showCreditErrorPopup.set(false);
  }

  goToPlansFromPopup() {
    this.showCreditErrorPopup.set(false);
    // Navigation is handled in the popup component
  }
}
