import {Component, input} from '@angular/core';
import {TitleCasePipe} from '@angular/common';
import {UntilDestroy} from '@ngneat/until-destroy';

@UntilDestroy()
@Component({
  selector: 'app-profile-image',
  imports: [
    TitleCasePipe
  ],
  templateUrl: './profile-image.component.html',
  styleUrl: './profile-image.component.scss'
})
export class ProfileImageComponent {
  imageUrl = input<string>();
  firstName = input<string>('');
  lastName = input<string>('');

  constructor() {
  }
}
