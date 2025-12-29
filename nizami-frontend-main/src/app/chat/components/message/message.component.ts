import {Component, ElementRef, input} from '@angular/core';
import {MessageModel} from '../../models/message.model';
import {UserMessageComponent} from '../user-message/user-message.component';
import {SystemMessageComponent} from '../system-message/system-message.component';
import {TranslationDisclaimerComponent} from '../translation-disclaimer/translation-disclaimer.component';

@Component({
  selector: 'app-message',
  imports: [
    UserMessageComponent,
    SystemMessageComponent,
    TranslationDisclaimerComponent,
  ],
  templateUrl: './message.component.html',
  styleUrl: './message.component.scss',
  standalone: true
})
export class MessageComponent {
  message = input.required<MessageModel>();
  isLast = input<boolean>(false);

  constructor(public elementRef: ElementRef) {
  }
}

