import {Component, ElementRef, input, signal} from '@angular/core';
import {CopyButtonComponent} from "../copy-button/copy-button.component";
import {FileModel, MessageModel} from '../../models/message.model';
import {ChatSystemProfileComponent} from '../chat-system-profile/chat-system-profile.component';
import {NgxTypedWriterComponent} from 'ngx-typed-writer';
import {marked} from 'marked';
import {IsTypingService} from '../../services/is-typing.service';
import {UserMessageFileComponent} from "../user-message-file/user-message-file.component";
import {MessagesService} from '../../services/messages.service';
import {UntilDestroy, untilDestroyed} from '@ngneat/until-destroy';
import {take} from 'rxjs';
import {SafeHtmlPipe} from '../../../common/pipes/safe-html.pipe';

@UntilDestroy()
@Component({
  selector: 'app-system-message',
  imports: [
    CopyButtonComponent,
    ChatSystemProfileComponent,
    NgxTypedWriterComponent,
    UserMessageFileComponent,
    SafeHtmlPipe
  ],
  templateUrl: './system-message.component.html',
  styleUrl: './system-message.component.scss'
})
export class SystemMessageComponent {
  message = input.required<MessageModel>();
  showCursor = signal(false);
  isLast = input<boolean>(false);

  constructor(
    public elementRef: ElementRef,
    private isTypingService: IsTypingService,
    private messagesService: MessagesService,
  ) {
  }

  get isTyping() {
    return this.isTypingService.value;
  }

  get text() {
    return marked(this.message().text.trim(), {async: false});
  }

  writingDone() {
    this.isTypingService.stopTyping();
  }

  clicked(file: FileModel) {
    this
      .messagesService
      .downloadFile(file)
      .pipe(
        untilDestroyed(this),
        take(1),
      )
      .subscribe()
  }
}
