import {Component, computed, input, OnInit, output} from '@angular/core';
import {SuggestionBoxComponent} from '../suggestion-box/suggestion-box.component';
import {AuthService} from '../../../auth/services/auth.service';
import {NgIf, TitleCasePipe} from '@angular/common';
import {ChatInputComponent} from '../chat-input/chat-input.component';
import {MessageModel} from '../../models/message.model';
import {TranslatePipe} from '@ngx-translate/core';
import {ScreenObserverService} from '../../../common/services/screen-observer.service';

@Component({
  selector: 'app-initial-messages',
  imports: [
    SuggestionBoxComponent,
    TitleCasePipe,
    ChatInputComponent,
    TranslatePipe,
    NgIf
  ],
  templateUrl: './initial-messages.component.html',
  styleUrl: './initial-messages.component.scss'
})
export class InitialMessagesComponent implements OnInit {
  onUploadForReview = output();
  onGetLegalAdvice = output();
  onAdjustDocument = output();
  disabled = input(false);
  onNewMessage = output<MessageModel>();
  showChatInput = computed(() => !this.screenObserver.isMobile());

  constructor(
    private authService: AuthService,
    private screenObserver: ScreenObserverService,
  ) {
  }


  user() {
    return this.authService.user();
  }
}
