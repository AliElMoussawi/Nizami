import {Component} from '@angular/core';
import {SidebarItemComponent} from '../sidebar-item/sidebar-item.component';
import {RouterLink} from '@angular/router';
import {DocumentsIconComponent} from '../../icons/documents-icon/documents-icon.component';
import {UsersIconComponent} from '../../icons/users-icon/users-icon.component';

@Component({
  selector: 'app-sidebar',
  imports: [
    SidebarItemComponent,
    RouterLink,
    DocumentsIconComponent,
    UsersIconComponent
  ],
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.scss'
})
export class SidebarComponent {

}
