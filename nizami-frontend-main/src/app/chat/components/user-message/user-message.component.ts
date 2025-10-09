import {Component, ElementRef, input} from '@angular/core';
import {MessageModel} from '../../models/message.model';
import {UserMessageFileComponent} from '../user-message-file/user-message-file.component';
import {NgClass} from '@angular/common';

@Component({
  selector: 'app-user-message',
  imports: [
    UserMessageFileComponent,
    NgClass
  ],
  templateUrl: './user-message.component.html',
  styleUrl: './user-message.component.scss'
})
export class UserMessageComponent {
  message = input.required<MessageModel>();

  constructor(public elementRef: ElementRef) {
  }
}
