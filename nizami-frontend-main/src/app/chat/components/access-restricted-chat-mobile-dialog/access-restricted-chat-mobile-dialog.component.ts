import {Component, Inject} from '@angular/core';
import {DIALOG_DATA, DialogRef} from '@angular/cdk/dialog';
import {CountryNamePipe} from '../../../common/pipes/country-name.pipe';
import {TranslatePipe} from '@ngx-translate/core';

@Component({
  selector: 'app-access-restricted-chat-mobile-dialog',
  imports: [
    CountryNamePipe,
    TranslatePipe
  ],
  templateUrl: './access-restricted-chat-mobile-dialog.component.html',
  styleUrl: './access-restricted-chat-mobile-dialog.component.scss'
})
export class AccessRestrictedChatMobileDialogComponent {
  constructor(
    @Inject(DIALOG_DATA) public data: any,
    @Inject(DialogRef) public dialogRef: DialogRef<any>,
  ) {
  }

  get chat() {
    return this.data.chat;
  }

  confirm() {
    this.dialogRef.close(true);
  }

  close() {
    this.dialogRef.close(false)
  }
}
