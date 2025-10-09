import {ElementRef, Injectable, signal, Signal} from '@angular/core';
import {FormControl} from '@angular/forms';

@Injectable({
  providedIn: 'root'
})
export class ChatInputService {
  textareaControl!: FormControl<string | null>;
  textarea!: Signal<ElementRef<HTMLTextAreaElement> | undefined>;
  filesInput = signal<HTMLInputElement | null>(null);

  constructor() {
  }

  focusTextArea() {
    this.textarea()?.nativeElement?.focus();
  }

  addAttachment() {
    this.filesInput()?.click();
  }
}
