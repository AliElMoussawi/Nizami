import {Component, forwardRef, input} from '@angular/core';
import {ControlValueAccessor, FormsModule, NG_VALUE_ACCESSOR, ReactiveFormsModule} from '@angular/forms';

@Component({
  selector: 'app-checkbox',
  imports: [
    ReactiveFormsModule,
    FormsModule
  ],
  templateUrl: './checkbox.component.html',
  styleUrl: './checkbox.component.scss',
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => CheckboxComponent),
      multi: true,
    },
  ]
})
export class CheckboxComponent implements ControlValueAccessor {
  value: boolean = false;
  isDisabled: boolean = false;
  label = input<string>('');

  writeValue(value: any): void {
    this.value = value || false;
  }

  registerOnChange(fn: (value: string) => void): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: () => void): void {
    this.onTouched = fn;
  }

  setDisabledState?(isDisabled: boolean): void {
    this.isDisabled = isDisabled;
  }

  onTouched: () => void = () => {
  };

// Triggered when the value changes
  onInputChange($event: any): void {
    if (!this.isDisabled) {
      const value = $event;
      this.value = value;
      this.onChange(value);
    }
  }

  // Callback functions provided by the Angular Forms API
  private onChange: (value: string) => void = () => {
  };
}
