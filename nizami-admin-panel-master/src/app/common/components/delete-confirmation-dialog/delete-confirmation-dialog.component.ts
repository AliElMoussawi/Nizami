import {Component, Inject} from '@angular/core';
import {DIALOG_DATA, DialogRef} from '@angular/cdk/dialog';

@Component({
  selector: 'app-delete-confirmation-dialog',
  imports: [],
  templateUrl: './delete-confirmation-dialog.component.html',
  styleUrl: './delete-confirmation-dialog.component.scss'
})
export class DeleteConfirmationDialogComponent {
  constructor(
    @Inject(DialogRef) public dialogRef: DialogRef<any>,
    @Inject(DIALOG_DATA) public data: any,
  ) {
  }

  get body() {
    return this.data.body;
  }

  get what() {
    return this.data.what;
  }

  close() {
    this.dialogRef.close(false);
  }

  confirm() {
    this.dialogRef.close(true);
  }
}
