import {Component, input, output} from '@angular/core';
import {TranslatePipe} from '@ngx-translate/core';
import {Router} from '@angular/router';

@Component({
  selector: 'app-credit-error-popup',
  imports: [
    TranslatePipe
  ],
  templateUrl: './credit-error-popup.component.html',
  styleUrl: './credit-error-popup.component.scss'
})
export class CreditErrorPopupComponent {
  isVisible = input<boolean>(false);
  errorMessage = input<string>('');
  onClose = output();
  onGoToPlans = output();

  constructor(private router: Router) {}

  close() {
    this.onClose.emit();
  }

  goToPlans() {
    this.onGoToPlans.emit();
    this.router.navigate(['/profile-settings'], { queryParams: { tab: 'plans' } });
    this.close();
  }
}
