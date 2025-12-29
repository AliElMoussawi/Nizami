import {Component, input, OnInit, output, signal} from '@angular/core';
import {ChatModel} from '../../models/chat.model';
import {ReactiveFormsModule} from '@angular/forms';
import {NgClass} from '@angular/common';
import {TooltipComponent} from '../tooltip/tooltip.component';
import {EditHistoryChatItemNameComponent} from '../edit-history-chat-item-name/edit-history-chat-item-name.component';
import {Dialog} from '@angular/cdk/dialog';
import {DeleteChatDialogComponent} from '../delete-chat-dialog/delete-chat-dialog.component';
import {UntilDestroy, untilDestroyed} from '@ngneat/until-destroy';
import {take} from 'rxjs';
import {HighlightPipe} from '../../../common/pipes/highlight.pipe';
import {FlagComponent} from '../../../common/components/flag/flag.component';
import {MessagesService} from '../../services/messages.service';
import {DeviceDetectorService} from 'ngx-device-detector';
import {
  AccessRestrictedChatMobileDialogComponent
} from '../access-restricted-chat-mobile-dialog/access-restricted-chat-mobile-dialog.component';

@UntilDestroy()
@Component({
  selector: 'app-history-chat-item',
  imports: [
    ReactiveFormsModule,
    NgClass,
    TooltipComponent,
    EditHistoryChatItemNameComponent,
    HighlightPipe,
    FlagComponent,

  ],
  templateUrl: './history-chat-item.component.html',
  styleUrl: './history-chat-item.component.scss'
})
export class HistoryChatItemComponent implements OnInit {
  chat = input.required<ChatModel>();
  selected = input<boolean>(false);
  alwaysShowActions = input(false);
  highlightedText = input<string | null>(null);


  onClick = output<ChatModel>();
  onDelete = output<ChatModel>();

  showButtons = signal(false);
  editModeEnabled = signal<boolean>(false);

  constructor(
    private dialog: Dialog,
    private deviceService: DeviceDetectorService,
    private messageServices: MessagesService,
  ) {
  }



  viewChat() {
    this.onClick.emit(this.chat());
  }

  deleteChat() {
    this.onDelete.emit(this.chat());
  }

  onDeleteClicked($event: MouseEvent) {
    $event.preventDefault();
    $event.stopPropagation();
    this.deleteDialog();
  }

  onEditClicked($event: MouseEvent) {
    $event.stopPropagation();

    this.editModeEnabled.set(true);
  }

  mouseOver() {
    this.showButtons.set(true);
  }

  mouseOut() {
    this.showButtons.set(false);
  }

  private deleteDialog() {
    this.dialog
      .open(DeleteChatDialogComponent, {
        data: {
          chat: this.chat(),
        },
      })
      .closed
      .pipe(
        take(1),
        untilDestroyed(this),
      )
      .subscribe((x) => {
        if (x == true) {
          this.deleteChat();
        }
      });
  }

  private accessRestrictionMobileDialog() {
    this
      .dialog
      .open(
        AccessRestrictedChatMobileDialogComponent, {
          data: {
            chat: this.chat(),
          },
        },
      )
      .closed
      .pipe(
        untilDestroyed(this),
        take(1),
      )
      .subscribe((r) => {
        if (r) {
          this.deleteDialog();
        }
      });
  }
}
