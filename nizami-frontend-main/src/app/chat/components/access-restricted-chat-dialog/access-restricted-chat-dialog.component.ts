import {Component, Inject} from '@angular/core';
import {DIALOG_DATA, DialogRef} from '@angular/cdk/dialog';
import {OutlineButtonComponent} from '../../../common/components/outline-button/outline-button.component';
import {CountryNamePipe} from '../../../common/pipes/country-name.pipe';
import {TranslatePipe} from '@ngx-translate/core';

@Component({
  selector: 'app-access-restricted-chat-dialog',
  imports: [
    OutlineButtonComponent,
    CountryNamePipe,
    TranslatePipe
  ],
  templateUrl: './access-restricted-chat-dialog.component.html',
  styleUrl: './access-restricted-chat-dialog.component.scss'
})
export class AccessRestrictedChatDialogComponent {
  jurisdiction!: string;

  constructor(
    @Inject(DIALOG_DATA) public data: any,
    @Inject(DialogRef) public dialogRef: DialogRef<any>,
  ) {
    this.jurisdiction = data.jurisdiction;
  }

  confirm() {
    this.dialogRef.close(true);
  }
}
