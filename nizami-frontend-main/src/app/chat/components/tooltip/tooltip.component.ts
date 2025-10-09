import {Component, effect, ElementRef, input, signal} from '@angular/core';
import {NgxTooltipComponent, Placement} from "@controllable-ui/ngx-tooltip";
import {ChatSideBarService} from '../../services/chat-side-bar.service';

@Component({
  selector: 'app-tooltip',
  imports: [
    NgxTooltipComponent
  ],
  templateUrl: './tooltip.component.html',
  styleUrl: './tooltip.component.scss'
})
export class TooltipComponent {
  arrow = input<boolean>(false);
  triggerActions = input<('hover' | 'focus' | 'click')[]>(['hover', 'focus']);
  tooltipRootClass = input<string>();
  preferredPlacement = input<Placement>('bottom');
  placementStrategy = input<'default' | 'considerKeepingCurrentPlacement'>(
    'default'
  );
  dialogOffset = input<number>(5);

  dialogMinMaxSizes = input<{
    dialogMaxHeight?: number;
    dialogMinHeight?: number;
    dialogMaxWidth?: number;
    dialogMinWidth?: number;
  }>();

  scrollableContainer = input<ElementRef<any>>();
  enterDelay = input<number>(100);
  leaveDelay = input<number>(150);

  dialogIsOpen = signal<boolean>(false);

  constructor(private sidebar: ChatSideBarService) {
    effect(() => {
      if (!sidebar.isOpen()) {
        this.dialogIsOpen.set(false);
      }
    });
  }

  handleOpen$ = () => {
    this.dialogIsOpen.set(true);
  };

  handleClose$ = () => {
    this.dialogIsOpen.set(false);
  };
}
