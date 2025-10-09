import {Injectable, signal} from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class IsTypingService {
  value = signal(false);

  startTyping() {
    this.value.set(true);
  }

  stopTyping() {
    this.value.set(false);
  }
}
