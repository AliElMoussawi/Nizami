import {Component} from '@angular/core';
import {TitleCasePipe} from '@angular/common';
import {environment} from '../../../../environments/environment';
import {AuthService} from '../../../auth/services/auth.service';
import {UntilDestroy} from '@ngneat/until-destroy';

@UntilDestroy()
@Component({
  selector: 'app-user-profile-image',
  imports: [
    TitleCasePipe
  ],
  templateUrl: './user-profile-image.component.html',
  styleUrl: './user-profile-image.component.scss'
})
export class UserProfileImageComponent {
  constructor(
    private auth: AuthService,
  ) {
  }

  get profileImageUrl() {
    return environment.baseUrl + this.auth.user()?.profile_image;
  }

  user() {
    return this.auth.user();
  }
}
