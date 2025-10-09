import {Component, ElementRef, input, output} from '@angular/core';
import {NgIcon} from '@ng-icons/core';
import {OutlineButtonComponent} from '../../../common/components/outline-button/outline-button.component';
import {Router} from '@angular/router';
import {TranslatePipe} from '@ngx-translate/core';

@Component({
  selector: 'app-chat-locked-error',
  imports: [
    NgIcon,
    OutlineButtonComponent,
    TranslatePipe
  ],
  templateUrl: './chat-locked-error.component.html',
  styleUrl: './chat-locked-error.component.scss'
})
export class ChatLockedErrorComponent {

  constructor(private router: Router) {
  }

  async redirectToNewChat() {
    await this.router.navigateByUrl('/chat');
    window.location.reload();
  }
}
