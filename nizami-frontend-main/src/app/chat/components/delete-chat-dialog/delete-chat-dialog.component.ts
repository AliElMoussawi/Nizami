import {Component, Inject, signal} from '@angular/core';
import {
  DeleteConfirmationDialogComponent
} from '../../../common/components/delete-confirmation-dialog/delete-confirmation-dialog.component';
import {DIALOG_DATA, DialogRef} from '@angular/cdk/dialog';
import {catchError, EMPTY} from 'rxjs';
import {MessagesService} from '../../services/messages.service';
import {ToastrService} from 'ngx-toastr';
import {extractErrorFromResponse} from '../../../common/utils';
import {marker} from '@colsen1991/ngx-translate-extract-marker';
import {TranslatePipe, TranslateService} from '@ngx-translate/core';

@Component({
  selector: 'app-delete-chat-dialog',
  imports: [
    DeleteConfirmationDialogComponent,
    TranslatePipe
  ],
  templateUrl: './delete-chat-dialog.component.html',
  styleUrl: './delete-chat-dialog.component.scss'
})
export class DeleteChatDialogComponent {
  isDeleting = signal(false);

  constructor(
    @Inject(DIALOG_DATA) public data: any,
    @Inject(DialogRef) public dialogRef: DialogRef<any>,
    private messages: MessagesService,
    private toastr: ToastrService,
    private translate: TranslateService,
  ) {
  }

  get chat() {
    return this.data.chat;
  }

  deleteChat() {
    this.isDeleting.set(true);

    this.messages
      .deleteChat(this.chat)
      .pipe(
        catchError((e) => {
          this.toastr.error(extractErrorFromResponse(e) ?? this.translate.instant(marker("errors.failed_to_delete_chat")));

          this.isDeleting.set(false);

          return EMPTY;
        }),
      )
      .subscribe(() => {
        this.toastr.success(this.translate.instant(marker('success.chat_deleted')));

        this.dialogRef.close(true);
      });
  }

  close() {
    this.dialogRef.close(false)
  }
}
