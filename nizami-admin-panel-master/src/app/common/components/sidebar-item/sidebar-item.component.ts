import {Component, input} from '@angular/core';
import {IsActiveMatchOptions, RouterLink, RouterLinkActive, UrlTree} from '@angular/router';
import {NgClass} from '@angular/common';

@Component({
  selector: 'app-sidebar-item',
  imports: [
    RouterLink,
    RouterLinkActive,
    NgClass
  ],
  templateUrl: './sidebar-item.component.html',
  styleUrl: './sidebar-item.component.scss'
})
export class SidebarItemComponent {
  routerLink = input<any[] | string | UrlTree | null | undefined>();
  routerLinkActive = input<string[] | string>('');
  routerLinkActiveOptions = input<{ exact: boolean } | IsActiveMatchOptions>({exact: false});
}
