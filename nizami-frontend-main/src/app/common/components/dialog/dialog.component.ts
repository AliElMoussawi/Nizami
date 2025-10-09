import {Component, output, signal} from '@angular/core';
import {ClickOutsideDirective} from '../../directives/click-outside.directive';

@Component({
  selector: 'app-dialog',
  imports: [
    ClickOutsideDirective
  ],
  templateUrl: './dialog.component.html',
  styleUrl: './dialog.component.scss'
})
export class DialogComponent {
  isVisible = signal(false);

  confirmed = output();

  open() {
    this.isVisible.set(true);
  }

  close() {
    this.isVisible.set(false);
  }

  confirm() {
    this.confirmed.emit();
    this.close();
  }
}
