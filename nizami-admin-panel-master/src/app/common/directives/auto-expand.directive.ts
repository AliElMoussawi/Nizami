import { Directive, ElementRef, HostListener, AfterViewInit } from '@angular/core';

@Directive({
  selector: '[appAutoExpand]'
})
export class AutoExpandDirective implements AfterViewInit {

  constructor(private el: ElementRef) {}

  @HostListener('input') onInput() {
    this.adjustHeight();
  }

  ngAfterViewInit() {
    this.adjustHeight(); // Adjust height for prefilled text
  }

  private adjustHeight() {
    const textarea = this.el.nativeElement;
    textarea.style.height = 'auto'; // Reset height
    textarea.style.height = textarea.scrollHeight + 10 + 'px'; // Adjust height dynamically
  }
}
