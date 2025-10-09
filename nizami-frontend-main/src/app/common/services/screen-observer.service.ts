import {Injectable, signal} from '@angular/core';
import {BreakpointObserver, Breakpoints} from '@angular/cdk/layout';

@Injectable({
  providedIn: 'root',
})
export class ScreenObserverService {
  isMobile = signal<boolean>(false);

  constructor(
    private breakpointObserver: BreakpointObserver,
  ) {
    this.updateScreen();

    window.addEventListener('resize', () => this.updateScreen());
  }

  private updateScreen() {
    this.isMobile.set(this.breakpointObserver.isMatched([
        Breakpoints.XSmall,
        Breakpoints.Small,
        Breakpoints.Medium,
      ])
    ); // Tailwind xl = 1280px
  }
}
