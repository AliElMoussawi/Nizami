import {Injectable, signal, NgZone, OnDestroy} from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class IsTypingService implements OnDestroy {
  value = signal(false);
  private visibilityHandler: () => void;

  constructor(private ngZone: NgZone) {
    // Listen for visibility changes to handle tab switching
    this.visibilityHandler = () => {
      if (document.hidden && this.value()) {
        // Tab became hidden while typing - complete animation immediately
        this.ngZone.run(() => {
          this.stopTyping();
        });
      }
    };

    document.addEventListener('visibilitychange', this.visibilityHandler);
  }

  ngOnDestroy() {
    document.removeEventListener('visibilitychange', this.visibilityHandler);
  }

  startTyping() {
    // Only start typing if the tab is visible
    if (!document.hidden) {
      this.value.set(true);
    }
  }

  stopTyping() {
    this.value.set(false);
  }
}
