import {Component} from '@angular/core';
import {AuthService} from '../../../auth/services/auth.service';
import {SidebarLogoComponent} from '../sidebar-logo/sidebar-logo.component';
import {MatMenu, MatMenuItem, MatMenuTrigger} from "@angular/material/menu";
import {UserProfileImageComponent} from '../user-profile-image/user-profile-image.component';

@Component({
  selector: 'app-header',
  imports: [
    SidebarLogoComponent,
    MatMenu,
    MatMenuTrigger,
    MatMenuItem,
    UserProfileImageComponent
  ],
  templateUrl: './header.component.html',
  styleUrl: './header.component.scss'
})
export class HeaderComponent {
  constructor(
    public auth: AuthService,
  ) {
  }

  logout() {
    this.auth.logout()
  }
}
