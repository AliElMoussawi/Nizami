import {Component, output, signal} from '@angular/core';

@Component({
  selector: 'app-dialog',
  imports: [],
  templateUrl: './dialog.component.html',
  styleUrl: './dialog.component.scss'
})
export class DialogComponent {
  isVisible = signal(false);

  confirmed = output();

  open() {
    this.isVisible.set(true);
  }

  close() {
    this.isVisible.set(false);
  }

  confirm() {
    this.confirmed.emit();
    this.close();
  }
}
