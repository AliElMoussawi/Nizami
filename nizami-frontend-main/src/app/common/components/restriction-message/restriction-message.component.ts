import {Component, effect, ElementRef, HostListener, Renderer2, signal, ViewChild} from '@angular/core';
import {NgxTooltipComponent} from '@controllable-ui/ngx-tooltip';
import {ChatSideBarService} from '../../../chat/services/chat-side-bar.service';
import {TranslatePipe} from '@ngx-translate/core';

@Component({
  selector: 'app-restriction-message',
  imports: [
    NgxTooltipComponent,
    TranslatePipe
  ],
  templateUrl: './restriction-message.component.html',
  styleUrl: './restriction-message.component.scss'
})
export class RestrictionMessageComponent {
  isOpened = signal(false);

  @ViewChild('tooltipTrigger', {static: true}) trigger!: ElementRef;

  constructor(
    private eRef: ElementRef,
    private renderer: Renderer2,
    private sidebar: ChatSideBarService,
  ) {
    effect(() => {
      if (!sidebar.isOpen()) {
        this.isOpened.set(false);
      }
    });
  }

  @HostListener('document:click', ['$event'])
  handleClickOutside(event: MouseEvent) {
    if (
      this.isOpened &&
      !this.eRef.nativeElement.contains(event.target) &&
      !this.trigger.nativeElement.contains(event.target)
    ) {
      this.isOpened.set(false);
    }
  }

  handleOpen$ = () => {
    this.isOpened.set(true);
  };

  handleClose$ = () => {
    this.isOpened.set(false);
  };
}
