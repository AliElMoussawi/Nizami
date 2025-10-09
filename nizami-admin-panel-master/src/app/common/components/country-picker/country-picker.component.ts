import {Component, ContentChildren, forwardRef, input, QueryList, viewChild} from '@angular/core';
import {ControlValueAccessor, FormsModule, NG_VALUE_ACCESSOR} from '@angular/forms';
import {ControlErrorsComponent} from '../errors/control-errors.component';
import {CountryListComponent, IConfig, ICountry} from 'ngx-countries-dropdown';
import {NgClass} from '@angular/common';

@Component({
  selector: 'app-country-picker',
  imports: [
    FormsModule,
    CountryListComponent,
    NgClass
  ],
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => CountryPickerComponent),
      multi: true,
    },
  ],
  templateUrl: './country-picker.component.html',
  styleUrl: './country-picker.component.scss'
})
export class CountryPickerComponent implements ControlValueAccessor {
  label = input<string | null>('');
  placeholder = input<string | null>('');
  type = input<string | null>('text');
  @ContentChildren(ControlErrorsComponent) errors!: QueryList<ControlErrorsComponent>;
  countryComponent = viewChild<CountryListComponent>(CountryListComponent);
  value: string = '';
  isDisabled: boolean = false;
  allowedCountries = input<string[]>([]);

  get hasError() {
    return this.errors && this.errors.length > 0 && this.errors.get(0)?.hasErrors;
  }

  get countryListConfig(): IConfig {
    return {
      hideDialCode: true,
      hideCode: true,
    };
  }

  get selectedCountryConfig(): IConfig {
    return {
      hideDialCode: true,
      hideCode: true,
    };
  }

  // Triggered when the value changes
  onInputChange($event: ICountry): void {
    if (!this.isDisabled) {
      this.value = $event.code;
      this.onChange(this.value);
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

    if(!value) {
      this.countryComponent()!.selectedCountry.set(null);
    }
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
