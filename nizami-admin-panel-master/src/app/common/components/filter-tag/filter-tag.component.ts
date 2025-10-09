import {Component, input, output} from '@angular/core';
import {NgClass} from '@angular/common';

@Component({
  selector: 'app-filter-tag',
  imports: [
    NgClass
  ],
  templateUrl: './filter-tag.component.html',
  styleUrl: './filter-tag.component.scss'
})
export class FilterTagComponent {
  isActive = input<boolean>();
  onClick = output();
}
