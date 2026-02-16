import {Component, effect, ElementRef, input, output, signal, viewChild, viewChildren} from '@angular/core';
import {MessageComponent} from '../message/message.component';
import {MessageModel} from '../../models/message.model';
import {GeneratingResponseMessageComponent} from '../generating-response-message/generating-response-message.component';
import {ErrorMessageComponent} from '../error-message/error-message.component';
import {InitialMessagesComponent} from '../initial-messages/initial-messages.component';
import {ChatInputService} from '../../services/chat-input.service';
import {LoadingErrorComponent} from '../loading-error/loading-error.component';
import {animate, state, style, transition, trigger} from '@angular/animations';
import {ChatSideBarService} from '../../services/chat-side-bar.service';
import {NgClass} from '@angular/common';
import {ChatModel} from '../../models/chat.model';
import {MessagesService} from '../../services/messages.service';
import {TranslateService} from '@ngx-translate/core';
import {marker} from '@colsen1991/ngx-translate-extract-marker';

@Component({
  selector: 'app-chat-messages',
  imports: [
    MessageComponent,
    GeneratingResponseMessageComponent,
    ErrorMessageComponent,
    InitialMessagesComponent,
    LoadingErrorComponent,
    NgClass
  ],
  templateUrl: './chat-messages.component.html',
  styleUrl: './chat-messages.component.scss',
  animations: [
    trigger('slideInOut', [
      state('in', style({
        transform: 'translateY(0)',   // Final position (no movement)
        opacity: 1                    // Fully visible
      })),
      state('out', style({
        transform: 'translateY(100px)', // Initial position (below the screen)
        opacity: 0                    // Fully transparent
      })),
      transition('in <=> out', [
        animate('300ms ease-in-out')  // 300ms sliding effect
      ]),
    ]),

    trigger('fadeInOut', [
      state('in', style({
        opacity: 1,  // Fully visible
        display: 'block'
      })),
      state('out', style({
        opacity: 0,  // Fully transparent
        display: 'none'  // Ensures it’s removed from layout
      })),
      transition('in <=> out', [
        animate('200ms ease-in-out')  // 200ms fade effect
      ]),
    ])
  ],
})
export class ChatMessagesComponent {
  messages = input.required<MessageModel[]>();
  chat = input.required<ChatModel>();
  disabled = input(false);
  isNewChat = input(false);
  onNewMessage = output<MessageModel>();

  isLoadingMessages = input(false);
  loadingError = input<string | null>(null);

  isGeneratingResponse = input<boolean>(false);
  submittingMessageLanguage = input<'ar' | 'en'>('ar');
  error = input<string | null>(null);

  generatingResponseMessageComponent = viewChild(GeneratingResponseMessageComponent);
  errorMessageComponent = viewChild(ErrorMessageComponent);
  messageComponents = viewChildren(MessageComponent);
  chatContainer = viewChild<ElementRef<HTMLDivElement>>('chatContainer');
  onRetry = output();
  onRetryLoading = output();
  onReachedTop = output();

  showScrollToBottomButton = signal<boolean>(false);

  constructor(
    private translate: TranslateService,
    private chatInput: ChatInputService,
    public sidebar: ChatSideBarService,
    private messagesService: MessagesService,
  ) {
    effect(() => {
      if (!this.messages() || this.messages().length == 0) {
        this.showScrollToBottomButton.set(false);
      }
    });
  }


  scrollToLastMessage(): void {
    const messageComponents = this.messageComponents();
    if (messageComponents.length - 2 > 0) {
      const component = messageComponents[messageComponents.length - 2];

      component.elementRef.nativeElement.scrollIntoView({behavior: 'smooth'});
    }
  }

  smoothScrollToBottom() {
    this.chatContainer()?.nativeElement?.scrollTo({
      behavior: 'smooth',
      top: this.chatContainer()?.nativeElement?.scrollHeight
    });
    this.showScrollToBottomButton.set(false);
  }

  instantScrollToBottom() {
    this.chatContainer()?.nativeElement?.scrollTo({
      behavior: 'instant',
      top: this.chatContainer()?.nativeElement?.scrollHeight
    });
    this.showScrollToBottomButton.set(false);
  }

  scrollToGeneratingMessage(): void {
    this.generatingResponseMessageComponent()?.elementRef.nativeElement.scrollIntoView();
  }

  scrollToErrorMessage(): void {
    this.errorMessageComponent()?.elementRef.nativeElement.scrollIntoView();
  }

  uploadForReview() {
    this.chatInput.textareaControl?.patchValue("Review ");
    this.chatInput.addAttachment();
  }

  getLegalAdvice() {
    this.chatInput.textareaControl?.patchValue(this.translate.instant(marker('legal_advice_prompt')));
    this.chatInput.focusTextArea();
  }

  adjustDocument() {
    this.chatInput.textareaControl?.patchValue("Adjust ");

    this.chatInput.addAttachment();
  }

  scroll() {
    const scrollTop = this.chatContainer()?.nativeElement.scrollTop;

    if (scrollTop === 0 && !this.isLoadingMessages() && this.messages().length > 0) {
      this.onReachedTop.emit();
    }

    const element = this.chatContainer()!.nativeElement;
    const atBottom = (element.scrollTop + element.clientHeight + 25) >= element.scrollHeight;
    this.showScrollToBottomButton.set(!atBottom);
  }
}
