import {Component, input} from '@angular/core';

@Component({
  selector: 'app-flag',
  imports: [],
  templateUrl: './flag.component.html',
  styleUrl: './flag.component.scss'
})
export class FlagComponent {
  code = input.required<string | undefined | null>();

  get url() {
    return `/assets/icons/flags/${this.code()?.toLowerCase()}.png`;
  };
}
