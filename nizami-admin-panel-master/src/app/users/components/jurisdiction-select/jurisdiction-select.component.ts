import {Component, forwardRef, signal} from '@angular/core';
import {ControlValueAccessor, NG_VALUE_ACCESSOR} from '@angular/forms';
import {CountryListComponent, IConfig, ICountry} from 'ngx-countries-dropdown';
import {NgClass} from '@angular/common';
import {FlagComponent} from '../../../common/components/flag/flag.component';
import {JurisdictionService} from '../../../reference-documents/services/jurisdiction.service';
import {take} from 'rxjs';
import {UntilDestroy, untilDestroyed} from '@ngneat/until-destroy';

@UntilDestroy()
@Component({
  selector: 'app-jurisdiction-select',
  imports: [
    CountryListComponent,
    NgClass,
    FlagComponent
  ],
  templateUrl: './jurisdiction-select.component.html',
  styleUrl: './jurisdiction-select.component.scss',
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => JurisdictionSelectComponent),
      multi: true,
    },
  ],
})
export class JurisdictionSelectComponent implements ControlValueAccessor {
  value = signal<string[]>([]);
  isDisabled: boolean = false;

  constructor(private jurisdictionService: JurisdictionService) {
    jurisdictionService
      .load()
      .pipe(
        take(1),
        untilDestroyed(this),
      )
      .subscribe();
  }

  get allowedCountries() {
    let j = this.jurisdictionService.jurisdictions().filter((x) => !this.value().includes(x.toLowerCase()));

    if (j.length > 0) {
      return j;
    }

    // fake value so that no results are returned
    return ['123xy'];
  }

  get isLoaded() {
    return this.jurisdictionService.isLoaded;
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

  get hasError() {
    return false;
  }

  registerOnChange(fn: (value: string[]) => void): void {
    this.onChange = fn;
  }

  // Register the function to call when the control is touched
  registerOnTouched(fn: () => void): void {
    this.onTouched = fn;
  }

  // Writes a new value to the element
  writeValue(value: string[]): void {
    this.value.set((value ?? []).map((x) => x.toLowerCase()));
  }

  // Set whether the control is disabled (not used here, but required for the interface)
  setDisabledState?(isDisabled: boolean): void {
    this.isDisabled = isDisabled;
  }

  onTouched: () => void = () => {
  };

  onInputChange($event: ICountry, f: CountryListComponent) {
    f.selectedCountry.set(null);

    this.value.update((x) => [
      ...x,
      $event.code,
    ].map((x) => x.toLowerCase()).filter((v, i, a) => a.indexOf(v) === i));

    this.onChange(this.value());
  }

  remove(country: string) {
    this.value.update((x) => x.filter(x => x !== country));
    this.onChange(this.value());
  }

  // Callback functions provided by the Angular Forms API
  private onChange: (value: string[]) => void = () => {
  };
}
