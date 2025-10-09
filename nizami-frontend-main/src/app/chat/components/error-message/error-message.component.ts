import {Component, ElementRef, input, output} from '@angular/core';
import {NgIcon} from '@ng-icons/core';
import {TooltipComponent} from '../tooltip/tooltip.component';
import {TranslatePipe} from '@ngx-translate/core';

@Component({
  selector: 'app-error-message',
  imports: [
    NgIcon,
    TooltipComponent,
    TranslatePipe
  ],
  templateUrl: './error-message.component.html',
  styleUrl: './error-message.component.scss'
})
export class ErrorMessageComponent {
  error = input<string|null>(null);
  onRetry = output();

  constructor(public elementRef: ElementRef) {
  }
}
