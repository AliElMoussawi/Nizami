import {Component, input} from '@angular/core';
import {FlagComponent} from '../flag/flag.component';
import {CountryNamePipe} from '../../pipes/country-name.pipe';
import {NgClass} from '@angular/common';

@Component({
  selector: 'app-country',
  imports: [
    FlagComponent,
    CountryNamePipe,
    NgClass
  ],
  templateUrl: './country.component.html',
  styleUrl: './country.component.scss'
})
export class CountryComponent {
  code = input.required<string>();
  selected = input<boolean>(false);
  hideName = input<boolean>(false);
}
