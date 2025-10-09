import {Component, input, output} from '@angular/core';
import {Tab} from '../../../profile/components/profile-settings-dialog/profile-settings-dialog.component';
import {NgClass} from '@angular/common';
import {TranslatePipe} from '@ngx-translate/core';

@Component({
  selector: 'app-button-toggle',
  imports: [
    NgClass,
    TranslatePipe
  ],
  templateUrl: './button-toggle.component.html',
  styleUrl: './button-toggle.component.scss'
})
export class ButtonToggleComponent {
  tab = input.required<Tab>();
  isFirst = input(false);
  isLast = input(false);

  selected = input(false);

  onClick = output();
}
