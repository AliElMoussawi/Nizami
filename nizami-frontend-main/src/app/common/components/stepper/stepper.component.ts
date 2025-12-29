import {AfterContentInit, Component, ContentChildren, input, output, QueryList, TemplateRef} from '@angular/core';
import {NgClass, NgIf, NgTemplateOutlet} from '@angular/common';
import {StepDirective} from '../../directives/step.directive';

@Component({
  selector: 'app-stepper',
  imports: [
    NgClass,
    NgIf,
    NgTemplateOutlet
  ],
  templateUrl: './stepper.component.html',
  styleUrl: './stepper.component.scss'
})
export class StepperComponent implements AfterContentInit {
  step = input.required<number>();
  stepsCount = input.required<number>();
  disabled = input<boolean>(false);

  onStepClicked = output<number>();
  @ContentChildren(StepDirective) stepTemplates!: QueryList<StepDirective>;

  stepMap = new Map<string | number, TemplateRef<any>>();

  get steps() {
    return Array.from({length: this.stepsCount()!}, (_, i) => i + 1);
  }

  get currentStepTemplate() {
    return this.stepMap.get(this.step());
  }

  stepClicked($event: number) {
    this.onStepClicked.emit($event);
  }

  ngAfterContentInit() {
    this.stepTemplates.forEach((template) => {
      const appStep = template.appStep();

      if (appStep) {
        this.stepMap.set(appStep, template.template);
      }
    });
  }
}
