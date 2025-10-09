import {Component, input, output} from '@angular/core';
import {NgClass} from '@angular/common';

@Component({
  selector: 'app-icon-button',
  imports: [
    NgClass
  ],
  templateUrl: './icon-button.component.html',
  styleUrl: './icon-button.component.scss'
})
export class IconButtonComponent {
  type = input<string>(IconButtonType.default);
  onClick = output();

  disabled = input(false);

  get klass() {
    if (this.type() == IconButtonType.primary) {
      return 'bg-blue-600 text-white';
    }

    return 'bg-white text-black';
  }
}

export enum IconButtonType  {
  primary = 'primary',
  default = 'default',
}
