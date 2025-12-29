import {Component, effect, OnInit, output} from '@angular/core';
import {AuthService} from '../../../auth/services/auth.service';
import {ReactiveFormsModule} from "@angular/forms";
import {OutlineButtonComponent} from '../../../common/components/outline-button/outline-button.component';
import {UntilDestroy} from '@ngneat/until-destroy';
import {ToastrService} from 'ngx-toastr';
import {TranslatePipe, TranslateService} from '@ngx-translate/core';

@UntilDestroy()
@Component({
  selector: 'app-account-details-tab',
  imports: [
    ReactiveFormsModule,
    OutlineButtonComponent,
    TranslatePipe
  ],
  templateUrl: './account-details-tab.component.html',
  styleUrl: './account-details-tab.component.scss'
})
export class AccountDetailsTabComponent implements OnInit {
  onCancel = output();

  constructor(
    public auth: AuthService,
    public toastr: ToastrService,
    private translate: TranslateService,
  ) {
    effect(() => {
      this.ngOnInit();
    });
  }

  get user() {
    return this.auth.user;
  }

}
