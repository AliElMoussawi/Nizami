import {Component, input, OnInit} from '@angular/core';
import {NgClass} from '@angular/common';

@Component({
  selector: 'app-translation-disclaimer',
  imports: [
    NgClass
  ],
  templateUrl: './translation-disclaimer.component.html',
  styleUrl: './translation-disclaimer.component.scss'
})
export class TranslationDisclaimerComponent implements OnInit {
  language = input<string>();
  translation_disclaimer_language = input<string>();

  dir: string = 'rtl';
  className: string = '';

  ngOnInit() {
    this.className = this.translation_disclaimer_language() == 'en' ? 'align-left' : 'align-right';
    this.dir = this.translation_disclaimer_language() == 'en' ? 'ltr' : 'rtl';
  }
}
