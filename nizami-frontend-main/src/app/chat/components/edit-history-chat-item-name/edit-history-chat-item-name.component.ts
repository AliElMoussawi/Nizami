import {Component, input, OnInit, output, signal} from '@angular/core';
import {ChatModel} from '../../models/chat.model';
import {InputComponent} from '../../../common/components/input/input.component';
import {TooltipComponent} from '../tooltip/tooltip.component';
import {FormControl, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';
import {catchError, EMPTY, finalize} from 'rxjs';
import {ToastrService} from 'ngx-toastr';
import {MessagesService} from '../../services/messages.service';
import { extractErrorFromResponse } from '../../../common/utils';
import {marker} from '@colsen1991/ngx-translate-extract-marker';
import {TranslatePipe, TranslateService} from '@ngx-translate/core';

@Component({
  selector: 'app-edit-history-chat-item-name',
  imports: [
    InputComponent,
    TooltipComponent,
    ReactiveFormsModule,
    TranslatePipe
  ],
  templateUrl: './edit-history-chat-item-name.component.html',
  styleUrl: './edit-history-chat-item-name.component.scss'
})
export class EditHistoryChatItemNameComponent implements OnInit {
  chat = input.required<ChatModel>();
  onCancel = output();
  onSave = output();
  isSaving = signal(false);
  form = new FormGroup({
    title: new FormControl<string>('', [Validators.required]),
  });

  constructor(
    private toastr: ToastrService,
    private messages: MessagesService,
    private translate: TranslateService,
  ) {
  }

  ngOnInit(): void {
    this.form.patchValue(this.chat());
  }

  save() {
    if (this.form.invalid) {
      return;
    }

    this.isSaving.set(true);
    this.form.disable();

    this.messages
      .updateChat(this.chat(), this.form.value)
      .pipe(
        catchError((e) => {
          this.toastr.error(extractErrorFromResponse(e) ?? this.translate.instant(marker('errors.failed_to_update_chat')));

          return EMPTY;
        }),
        finalize(() => {
          this.isSaving.set(false);
          this.form.enable();
        }),
      )
      .subscribe(() => {
        this.toastr.success(this.translate.instant(marker('success.chat_updated')));

        this.chat().title = this.form.value.title!;

        this.onSave.emit();
      });

  }

  cancel() {
    this.onCancel.emit();
  }
}
