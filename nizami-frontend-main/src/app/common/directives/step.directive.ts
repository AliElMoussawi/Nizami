import {Directive, input, TemplateRef} from '@angular/core';

@Directive({
  selector: '[appStep]'
})
export class StepDirective {
  appStep = input.required<string|number>();

  constructor(public template: TemplateRef<any>) {
  }
}
