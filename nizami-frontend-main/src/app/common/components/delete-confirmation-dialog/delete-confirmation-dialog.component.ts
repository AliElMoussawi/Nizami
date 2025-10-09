import {Component, input, output} from '@angular/core';
import {TranslatePipe} from '@ngx-translate/core';

@Component({
  selector: 'app-delete-confirmation-dialog',
  imports: [
    TranslatePipe
  ],
  templateUrl: './delete-confirmation-dialog.component.html',
  styleUrl: './delete-confirmation-dialog.component.scss'
})
export class DeleteConfirmationDialogComponent {
  title = input<string>('Delete');
  disabled = input<boolean>(false);
  confirmed = output();
  onClose = output();

  constructor() {
  }

  close() {
    this.onClose.emit();
  }

  confirm() {
    this.confirmed.emit();
  }
}
