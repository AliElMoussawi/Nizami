import {Component, EventEmitter, Input, Output} from '@angular/core';
import {UntilDestroy} from "@ngneat/until-destroy";
import {MatMenu, MatMenuItem, MatMenuTrigger} from '@angular/material/menu';
import {RouterLink} from '@angular/router';
import {NgIcon} from '@ng-icons/core';

@UntilDestroy()
@Component({
  selector: 'app-actions',
  templateUrl: './actions.component.html',
  imports: [
    MatMenuTrigger,
    MatMenu,
    RouterLink,
    MatMenuItem,
    NgIcon
  ],
  styleUrls: ['./actions.component.scss']
})
export class ActionsComponent {
  @Output()
  onDelete = new EventEmitter<any>();

  @Input()
  showDelete = false;

  @Output()
  onSelect = new EventEmitter<any>();

  @Input()
  showSelect = false;

  @Input()
  viewRouterLink: any = null;

  @Input()
  editRouterLink: any = null;

  delete() {
    this.onDelete.emit();
  }

  select() {
    this.onSelect.emit();
  }
}
