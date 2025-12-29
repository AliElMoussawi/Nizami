import {
  ApplicationConfig,
  importProvidersFrom,
  inject,
  provideAppInitializer,
  provideZoneChangeDetection
} from '@angular/core';
import {provideRouter} from '@angular/router';

import {routes} from './app.routes';
import {provideAnimations} from '@angular/platform-browser/animations';
import {HTTP_INTERCEPTORS, HttpClient, provideHttpClient, withInterceptorsFromDi} from '@angular/common/http';
import {provideIcons} from '@ng-icons/core';
import {
  heroArrowLeft,
  heroArrowPath,
  heroArrowRightStartOnRectangle,
  heroBars3BottomLeft,
  heroChatBubbleOvalLeftEllipsis,
  heroCheck,
  heroCheckCircle,
  heroDocument,
  heroDocumentArrowUp,
  heroDocumentDuplicate,
  heroDocumentText,
  heroExclamationCircle,
  heroExclamationTriangle,
  heroEye,
  heroEyeSlash,
  heroGlobeAlt,
  heroLockClosed,
  heroMagnifyingGlass,
  heroPaperAirplane,
  heroPaperClip,
  heroPencilSquare,
  heroPlusCircle,
  heroTrash,
} from '@ng-icons/heroicons/outline';
import { Arabic } from "flatpickr/dist/l10n/ar"

import {heroLockClosedSolid, heroStopSolid,} from '@ng-icons/heroicons/solid';
import {provideMarkdown} from 'ngx-markdown';
import {provideToastr} from 'ngx-toastr';
import {AuthService} from './auth/services/auth.service';
import {AuthInterceptor} from './common/interceptors/auth.interceptor';
import {provideFlatpickrDefaults} from 'angularx-flatpickr';
import {ErrorInterceptor} from './common/interceptors/error.interceptor';
import {TranslateLoader, TranslateModule} from '@ngx-translate/core';
import {TranslateHttpLoader} from '@ngx-translate/http-loader';
import {TranslationLoaderService} from './common/services/translation-loader.service';


const httpLoaderFactory: (http: HttpClient) => TranslateHttpLoader = (http: HttpClient) =>
  new TranslateHttpLoader(http, './assets/i18n/', '.json');


export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({eventCoalescing: true}),
    provideAnimations(),
    provideRouter(routes),
    provideHttpClient(withInterceptorsFromDi()),
    {
      provide: HTTP_INTERCEPTORS,
      useClass: AuthInterceptor,
      multi: true,
    },
    {
      provide: HTTP_INTERCEPTORS,
      useClass: ErrorInterceptor,
      multi: true,
    },
    provideIcons({
      heroDocument,
      heroExclamationCircle,
      heroCheck,
      heroDocumentDuplicate,
      heroBars3BottomLeft,
      heroArrowRightStartOnRectangle,
      heroEye,
      heroEyeSlash,
      heroExclamationTriangle,
      heroTrash,
      heroPencilSquare,
      heroMagnifyingGlass,
      heroPlusCircle,
      heroGlobeAlt,
      heroPaperClip,
      heroPaperAirplane,
      heroStopSolid,
      heroArrowLeft,
      heroDocumentArrowUp,
      heroChatBubbleOvalLeftEllipsis,
      heroDocumentText,
      heroCheckCircle,
      heroArrowPath,
      heroLockClosed,
      heroLockClosedSolid,
    }),
    provideMarkdown(),
    provideToastr({
      positionClass: 'toast-top-left'
    }),
    provideFlatpickrDefaults({
      locale: Arabic,
    }),
    provideAppInitializer(async () => {
      const translationLoader = inject(TranslationLoaderService);
      return await translationLoader.load();
    }),
    provideAppInitializer(async () => {
        const authService = inject(AuthService);
        authService.loadToken();

        if (authService.isAuthenticated()) {
          authService.loadProfile().subscribe(() => {});
        }
      },
    ),
    importProvidersFrom([TranslateModule.forRoot({
      defaultLanguage: 'ar',
      loader: {
        provide: TranslateLoader,
        useFactory: httpLoaderFactory,
        deps: [HttpClient],
      },
    })]),
  ]
};
