import {Component, input, Input, output} from '@angular/core';
import {NgClass} from '@angular/common';

@Component({
  selector: 'app-button',
  imports: [
    NgClass
  ],
  templateUrl: './button.component.html',
  styleUrl: './button.component.scss'
})
export class ButtonComponent {
  disabled = input(false);
  onClick = output();
  klass = input<any>('');
  type = input<any>('submit');

  click() {
    this.onClick.emit();
  }
}
