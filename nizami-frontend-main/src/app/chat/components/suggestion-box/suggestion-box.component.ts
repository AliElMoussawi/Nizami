import {Component, output} from '@angular/core';

@Component({
  selector: 'app-suggestion-box',
  imports: [],
  templateUrl: './suggestion-box.component.html',
  styleUrl: './suggestion-box.component.scss'
})
export class SuggestionBoxComponent {
  onClick = output();
}
