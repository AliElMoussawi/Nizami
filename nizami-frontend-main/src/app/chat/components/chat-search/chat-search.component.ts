import {Component, output, signal} from '@angular/core';
import {InputComponent} from '../../../common/components/input/input.component';
import {FormsModule} from '@angular/forms';
import {debounceTime, distinct, distinctUntilChanged, Subject} from 'rxjs';
import {UntilDestroy, untilDestroyed} from '@ngneat/until-destroy';
import {TranslatePipe} from '@ngx-translate/core';

@UntilDestroy()
@Component({
  selector: 'app-chat-search',
  imports: [
    InputComponent,
    FormsModule,
    TranslatePipe
  ],
  templateUrl: './chat-search.component.html',
  styleUrl: './chat-search.component.scss'
})
export class ChatSearchComponent {
  value = signal<string>('');
  onSearch = output<string>();
  inputChange = new Subject<string>();


  constructor() {
    this.inputChange
      .pipe(
        untilDestroyed(this),
        debounceTime(500),
        distinctUntilChanged(),
      )
      .subscribe((x) => {
        this.onSearch.emit(x);
      });
  }

  search() {
    this.onSearch.emit(this.value()!);
  }

  onChange($event: any) {
    this.inputChange.next($event);
  }
}
