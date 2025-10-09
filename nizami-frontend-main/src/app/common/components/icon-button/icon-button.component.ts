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
      return this.primaryClass;
    }

    return 'bg-white text-black border-2 border-grey1 hover:bg-grey2';
  }

  get primaryClass() {
    return `
         bg-blue1 text-white hover:bg-blue-500 focus:outline-none
         disabled:bg-grey3 disabled:text-slate-500 disabled:border-grey3 disabled:shadow-none disabled:cursor-not-allowed
         disabled:placeholder hover:bg-purple5
`
  }
}

export enum IconButtonType {
  primary = 'primary',
  default = 'default',
}
