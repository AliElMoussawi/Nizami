import {TranslateService} from '@ngx-translate/core';
import {firstValueFrom} from 'rxjs';
import {Injectable} from '@angular/core';

@Injectable({providedIn: 'root'})
export class TranslationLoaderService {
  constructor(private translate: TranslateService) {
  }

  async load(): Promise<void> {
    const lang = 'ar';
    this.translate.setDefaultLang(lang);
    await firstValueFrom(this.translate.use(lang));
  }
}
