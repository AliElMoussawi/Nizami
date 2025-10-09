import {Component} from '@angular/core';
import {CountryComponent} from '../../../common/components/country/country.component';

@Component({
  selector: 'app-jurisdiction-select',
  imports: [
    CountryComponent
  ],
  templateUrl: './jurisdiction-select.component.html',
  styleUrl: './jurisdiction-select.component.scss'
})
export class JurisdictionSelectComponent {
  constructor() {
  }
}
