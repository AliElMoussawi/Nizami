import {Component, ElementRef} from '@angular/core';
import {ChatSystemProfileComponent} from '../chat-system-profile/chat-system-profile.component';

@Component({
  selector: 'app-generating-response-message',
  templateUrl: './generating-response-message.component.html',
  imports: [
    ChatSystemProfileComponent,
  ],
  styleUrl: './generating-response-message.component.scss'
})
export class GeneratingResponseMessageComponent {
  constructor(public elementRef: ElementRef) {
  }
}
