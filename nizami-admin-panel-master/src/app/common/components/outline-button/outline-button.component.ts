import {Component, input, output} from '@angular/core';
import {NgClass} from '@angular/common';

@Component({
  selector: 'app-outline-button',
  imports: [
    NgClass
  ],
  templateUrl: './outline-button.component.html',
  styleUrl: './outline-button.component.scss'
})
export class OutlineButtonComponent {
  disabled = input(false);
  onClick = output();
  klass = input<any>('');
  type = input<any>('submit');

  click() {
    this.onClick.emit();
  }
}
