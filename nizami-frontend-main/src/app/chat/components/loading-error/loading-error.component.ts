import {Component, ElementRef, input, output} from '@angular/core';
import {NgIcon} from '@ng-icons/core';
import {TranslatePipe} from '@ngx-translate/core';

@Component({
  selector: 'app-loading-error',
  imports: [
    NgIcon,
    TranslatePipe
  ],
  templateUrl: './loading-error.component.html',
  styleUrl: './loading-error.component.scss'
})
export class LoadingErrorComponent {
  error = input<string|null>(null);
  onRetry = output();

  constructor(public elementRef: ElementRef) {
  }
}
