import {Component, input, output} from '@angular/core';
import {ButtonComponent} from '../../../common/components/button/button.component';
import {NgIcon} from '@ng-icons/core';
import {IconButtonComponent} from '../../../common/components/icon-button/icon-button.component';
import {ChatSideBarService} from '../../services/chat-side-bar.service';
import {JurisdictionSelectComponent} from '../jurisdiction-select/jurisdiction-select.component';
import {TranslatePipe} from '@ngx-translate/core';

@Component({
  selector: 'app-chat-header',
  imports: [
    ButtonComponent,
    NgIcon,
    IconButtonComponent,
    JurisdictionSelectComponent,
    TranslatePipe
  ],
  templateUrl: './chat-header.component.html',
  styleUrl: './chat-header.component.scss'
})
export class ChatHeaderComponent {
  onNewChatClicked = output();
  onLegalAssistanceClicked = output();
  
  messagesCount = input<number>(0);
  showLegalAssistanceButton = input<boolean>(false);

  constructor(public sidebar: ChatSideBarService) {
  }

  newChatClicked() {
    this.onNewChatClicked.emit();
  }

  legalAssistanceClicked() {
    this.onLegalAssistanceClicked.emit();
  }
}
