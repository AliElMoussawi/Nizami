import {ApplicationConfig, inject, provideAppInitializer, provideZoneChangeDetection} from '@angular/core';
import {provideRouter} from '@angular/router';

import {routes} from './app.routes';
import {provideAnimations} from '@angular/platform-browser/animations';
import {HTTP_INTERCEPTORS, provideHttpClient} from '@angular/common/http';
import {provideIcons} from '@ng-icons/core';
import {
  heroArrowLeft,
  heroArrowRightStartOnRectangle,
  heroBars3BottomLeft,
  heroChatBubbleOvalLeftEllipsis,
  heroChatBubbleLeft,
  heroChatBubbleBottomCenterText,
  heroCheck,
  heroDocument,
  heroDocumentArrowUp,
  heroDocumentDuplicate,
  heroDocumentText,
  heroCalendar,
  heroExclamationCircle,
  heroEye,
  heroArrowDownTray,
  heroEyeSlash,
  heroGlobeAlt,
  heroMagnifyingGlass,
  heroPaperAirplane,
  heroPaperClip,
  heroPencilSquare,
  heroPlusCircle,
  heroTrash,
  heroCheckCircle,
  heroArrowPath,
  heroUsers,
  heroHome,
  heroEllipsisVertical,
  heroCursorArrowRays,
  heroChatBubbleOvalLeft,
} from '@ng-icons/heroicons/outline';
import {heroStopSolid} from '@ng-icons/heroicons/solid';
import {provideMarkdown} from 'ngx-markdown';
import {provideToastr} from 'ngx-toastr';
import {AuthService} from './auth/services/auth.service';
import {AuthInterceptor} from './common/interceptors/auth-interceptor';
import {provideFlatpickrDefaults} from 'angularx-flatpickr';

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({eventCoalescing: true}),
    provideAnimations(),
    provideRouter(routes),
    provideHttpClient(),
    provideIcons({
      heroArrowDownTray,
      heroCursorArrowRays,
      heroEllipsisVertical,
      heroHome,
      heroDocument,
      heroExclamationCircle,
      heroCheck,
      heroDocumentDuplicate,
      heroChatBubbleLeft,
      heroBars3BottomLeft,
      heroArrowRightStartOnRectangle,
      heroEye,
      heroEyeSlash,
      heroTrash,
      heroPencilSquare,
      heroMagnifyingGlass,
      heroPlusCircle,
      heroGlobeAlt,
      heroPaperClip,
      heroPaperAirplane,
      heroChatBubbleBottomCenterText,
      heroStopSolid,
      heroArrowLeft,
      heroDocumentArrowUp,
      heroChatBubbleOvalLeft,
      heroChatBubbleOvalLeftEllipsis,
      heroDocumentText,
      heroCheckCircle,
      heroArrowPath,
      heroUsers,
      heroCalendar,
    }),
    provideMarkdown(),
    provideToastr(),
    provideFlatpickrDefaults(),
    provideAppInitializer(() => {
      let authService = inject(AuthService);
      authService.loadToken();

      if (authService.isAuthenticated()) {
        authService.loadProfile().subscribe();
      }
    }),
    {
      provide: HTTP_INTERCEPTORS,
      useClass: AuthInterceptor,
      multi: true,
    }
  ],
};
