import {Component, input, signal} from '@angular/core';
import {NgIcon} from '@ng-icons/core';
import {TooltipComponent} from '../tooltip/tooltip.component';

@Component({
  selector: 'app-copy-button',
  imports: [
    NgIcon,
    TooltipComponent
  ],
  templateUrl: './copy-button.component.html',
  styleUrl: './copy-button.component.scss'
})
export class CopyButtonComponent {
  text = input.required<string>();

  isCopied = signal(false);

  onClick() {
    this.isCopied.set(false);

    if (navigator.clipboard) {
      navigator.clipboard.writeText(this.text()).then(() => {
        this.isCopied.set(true);

        setTimeout(() => {
          this.isCopied.set(false);
        }, 2000);
      }).catch(err => {
        this.isCopied.set(false);
      });
    } else {
      this.isCopied.set(false);
      alert('Clipboard API not supported in this browser.');
    }
  }
}
