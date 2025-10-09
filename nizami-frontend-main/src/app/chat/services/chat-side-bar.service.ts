import {Injectable, signal} from '@angular/core';
import {ScreenObserverService} from '../../common/services/screen-observer.service';

@Injectable({
  providedIn: 'root'
})
export class ChatSideBarService {
  isOpen = signal(true);

  constructor(
    private screenObserver: ScreenObserverService,
  ) {
    this.isOpen.set(!this.screenObserver.isMobile());
  }

  open() {
    this.isOpen.set(true);
  }

  close() {
    this.isOpen.set(false);
  }

  toggle() {
    if (this.isOpen()) {
      this.close();
    } else {
      this.open();
    }
  }
}
