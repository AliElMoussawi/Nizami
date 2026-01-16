import {Component, input, output} from '@angular/core';
import {TranslatePipe} from '@ngx-translate/core';

@Component({
  selector: 'app-legal-assistance-consent-dialog',
  imports: [
    TranslatePipe
  ],
  templateUrl: './legal-assistance-consent-dialog.component.html',
  styleUrl: './legal-assistance-consent-dialog.component.scss'
})
export class LegalAssistanceConsentDialogComponent {
  chatTitle = input<string>('');
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
