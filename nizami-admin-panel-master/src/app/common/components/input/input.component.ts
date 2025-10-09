import {
  AfterContentInit,
  Component,
  ContentChildren,
  ElementRef,
  forwardRef,
  input,
  output,
  QueryList
} from '@angular/core';
import {ControlValueAccessor, FormsModule, NG_VALUE_ACCESSOR} from '@angular/forms';
import {NgClass} from '@angular/common';
import {ControlErrorsComponent} from '../errors/control-errors.component';

@Component({
  selector: 'app-input',
  imports: [
    FormsModule,
    NgClass
  ],
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => InputComponent),
      multi: true,
    },
  ],
  templateUrl: './input.component.html',
  styleUrl: './input.component.scss'
})
export class InputComponent implements ControlValueAccessor, AfterContentInit {
  label = input<string | null>('');
  placeholder = input<string | null>('');
  type = input<string | null>('text');

  @ContentChildren('.icon-after') iconsAfter!: QueryList<any>;
  iconsAfterCount = 0;

  ngAfterContentInit() {
    this.iconsAfterCount = this.iconsAfter.length;
  }

  onEnter = output();

  value: any = '';
  isDisabled: boolean = false;

  // Triggered when the value changes
  onInputChange($event: any): void {
    if (!this.isDisabled) {
      let value = $event;
      this.value = value;
      this.onChange(value);
    }
  }

  // Register the function to call when the control value changes
  registerOnChange(fn: (value: string) => void): void {
    this.onChange = fn;
  }

  // Register the function to call when the control is touched
  registerOnTouched(fn: () => void): void {
    this.onTouched = fn;
  }

  // Writes a new value to the element
  writeValue(value: string): void {
    this.value = value || '';
  }

  // Set whether the control is disabled (not used here, but required for the interface)
  setDisabledState?(isDisabled: boolean): void {
    this.isDisabled = isDisabled;
  }

  onTouched: () => void = () => {
  };

  // Callback functions provided by the Angular Forms API
  private onChange: (value: string) => void = () => {
  };

  @ContentChildren(ControlErrorsComponent) errors!: QueryList<ControlErrorsComponent>;
  get hasError() {
    return this.errors && this.errors.length > 0 && this.errors.get(0)?.hasErrors;
  }
}
