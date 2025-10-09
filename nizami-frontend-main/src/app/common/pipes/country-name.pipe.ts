import {Pipe, PipeTransform} from '@angular/core';
import {marker} from '@colsen1991/ngx-translate-extract-marker';
import {TranslateService} from '@ngx-translate/core';

@Pipe({
  name: 'countryName'
})
export class CountryNamePipe implements PipeTransform {
  constructor(private translate: TranslateService) {
  }

  codeToCountry: Record<string, string> = {
    'ae': 'United Arab Emirates',
    'sa': marker('Saudi Arabia'),
    'lb': 'Lebanon',
    'bh': 'Bahrain',
    'dj': 'Djibouti',
    'dz': 'Algeria',
    'eg': 'Egypt',
    'iq': 'Iraq',
    'jo': 'Jordan',
    'km': 'Comoros',
    'kw': 'Kuwait',
    'ly': 'Libya',
    'ma': 'Morocco',
    'mr': 'Mauritania',
    'om': 'Oman',
    'ps': 'Palestine',
    'qa': 'Qatar',
    'sd': 'Sudan',
    'so': 'Somalia',
    'sy': 'Syria',
    'tn': 'Tunisia',
    'ye': 'Yemen'
  };

  transform(value: string | undefined | null): string | undefined | null {
    if(!value) {
      return value;
    }

    return this.translate.instant(this.codeToCountry[value.toLowerCase()] ?? value);
  }
}
