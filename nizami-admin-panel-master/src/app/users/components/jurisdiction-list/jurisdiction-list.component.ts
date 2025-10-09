import {Component, input} from '@angular/core';
import {FlagComponent} from '../../../common/components/flag/flag.component';
import {CdkMenu, CdkMenuTrigger} from '@angular/cdk/menu';

@Component({
  selector: 'app-jurisdiction-list',
  imports: [
    FlagComponent,
    CdkMenuTrigger,
    CdkMenu
  ],
  templateUrl: './jurisdiction-list.component.html',
  styleUrl: './jurisdiction-list.component.scss'
})
export class JurisdictionListComponent {
  list = input<string[] | null>(null);

  openedViaHovering = false;

  openMenu(trigger: CdkMenuTrigger) {
    this.openedViaHovering = true;

    trigger.open();
  }

  closeMenu(trigger: CdkMenuTrigger) {
    if (this.openedViaHovering) {
      trigger.close();
    }
  }

  onClosed() {
    this.openedViaHovering = false;
  }

  openMenuByClicking(trigger: CdkMenuTrigger) {
    this.openedViaHovering = false;
    trigger.open();
  }
}
