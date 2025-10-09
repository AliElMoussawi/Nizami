import {Component, input, output} from '@angular/core';
import {Tab} from '../../../profile/components/profile-settings-dialog/profile-settings-dialog.component';
import {NgClass} from '@angular/common';
import {TranslatePipe} from '@ngx-translate/core';

@Component({
  selector: 'app-tabs-button',
  imports: [
    NgClass,
    TranslatePipe
  ],
  templateUrl: './tabs-button.component.html',
  styleUrl: './tabs-button.component.scss'
})
export class TabsButtonComponent {
  tab = input.required<Tab>();

  selected = input(false);

  onClick = output();
}
