import {Component, input, Input, output} from '@angular/core';
import {NgClass} from '@angular/common';

@Component({
  selector: 'app-flat-button',
  imports: [
    NgClass
  ],
  templateUrl: './flat-button.component.html',
  styleUrl: './flat-button.component.scss'
})
export class FlatButtonComponent {
  disabled = input(false);
  onClick = output();
  klass = input<any>('');
  type = input<any>('button');

  click() {
    this.onClick.emit();
  }
}
