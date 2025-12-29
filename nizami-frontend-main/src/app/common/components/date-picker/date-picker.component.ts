import {Component, ContentChildren, forwardRef, input, QueryList} from '@angular/core';
import {ControlValueAccessor, FormsModule, NG_VALUE_ACCESSOR} from '@angular/forms';
import {NgClass} from '@angular/common';
import {ControlErrorsComponent} from '../errors/control-errors.component';
import {FlatpickrDirective} from 'angularx-flatpickr';

@Component({
  selector: 'app-date-picker',
  imports: [
    FormsModule,
    NgClass,
    FlatpickrDirective
  ],
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => DatePickerComponent),
      multi: true,
    },
  ],
  templateUrl: './date-picker.component.html',
  styleUrl: './date-picker.component.scss'
})
export class DatePickerComponent implements ControlValueAccessor {
  label = input<string | null>('');
  placeholder = input<string | null>('');
  @ContentChildren(ControlErrorsComponent) errors!: QueryList<ControlErrorsComponent>;
  maxDate = input<string | Date>('');

  value: any = '';
  isDisabled: boolean = false;

  get hasError() {
    return this.errors && this.errors.length > 0 && this.errors.get(0)?.hasErrors;
  }

  // Triggered when the value changes
  onInputChange($event: any): void {
    if (!this.isDisabled) {
      const value = $event;
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
}
