import {Component, effect, ElementRef, input, OnInit, output, signal, viewChild, WritableSignal} from '@angular/core';
import {FormControl, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';
import {IsTypingService} from '../../services/is-typing.service';
import {ChatInputService} from '../../services/chat-input.service';
import {NgClass} from '@angular/common';
import {FileModel, MessageModel} from '../../models/message.model';
import {MessagesService} from '../../services/messages.service';
import {catchError, map} from 'rxjs';
import {UntilDestroy, untilDestroyed} from '@ngneat/until-destroy';
import {HttpEventType} from '@angular/common/http';
import {FileUploadingProgressComponent} from '../file-uploading-progress/file-uploading-progress.component';
import {IconButtonComponent} from '../../../common/components/icon-button/icon-button.component';
import {ChatSideBarService} from '../../services/chat-side-bar.service';
import {TranslatePipe} from '@ngx-translate/core';

@UntilDestroy()
@Component({
  imports: [
    ReactiveFormsModule,
    NgClass,
    FileUploadingProgressComponent,
    IconButtonComponent,
    TranslatePipe
  ],
  selector: 'app-chat-input',
  standalone: true,
  styleUrl: './chat-input.component.scss',
  templateUrl: './chat-input.component.html'
})
export class ChatInputComponent implements OnInit {
  textarea = viewChild<ElementRef<HTMLTextAreaElement>>('input');
  filesInput = viewChild<ElementRef<HTMLInputElement>>('filesInput')

  disabled = input(false);

  uploadingFilesCount = 0;

  files: WritableSignal<{
    file: FileModel;
    progress: number;
    error?: any;
  }>[] = [];

  onNewMessage = output<MessageModel>();
  form = new FormGroup({
    text: new FormControl<string>('', [Validators.required, Validators.minLength(1)]),
  });

  constructor(
    private isTypingService: IsTypingService,
    private chatInputService: ChatInputService,
    private messageService: MessagesService,
    public sidebar: ChatSideBarService,
  ) {
    this.chatInputService.textareaControl = this.form.controls.text;

    effect(() => {
      const isDisabled = this.disabled();

      if (isDisabled) {
        this.form.disable();
      } else {
        this.form.enable();
      }
    });
  }

  get isTyping() {
    return this.isTypingService.value;
  };

  ngOnInit() {
    this.chatInputService.textarea = this.textarea;
    if(this.filesInput()) {
      this.chatInputService.filesInput.set(this.filesInput()!.nativeElement);
    }
  }

  sendMessage() {
    if (this.form.invalid) {
      return;
    }
    const text = this.form.controls.text.value;
    if (text == null || text.trim().length < 1) {
      return;
    }

    if (this.uploadingFilesCount > 0) {
      return;
    }

    this.onNewMessage.emit({
      id: null,
      text: this.form.value.text!,
      messageFiles: this.files?.map((item) => item().file),
    });

    this.form.reset();
    this.files = [];
    if (this.filesInput()) {
      this.filesInput()!.nativeElement!.value = '';
    }

    this.editingText();
  }

  editingText() {
    const textarea = this.textarea()!.nativeElement;

    const rowHeight = parseInt(window.getComputedStyle(textarea).lineHeight, 10);
    if (!textarea.value) {
      textarea.style.height = `${rowHeight}px`;
      return;
    }

    const scrollHeight = textarea.scrollHeight;

    const maxRows = 5;
    const maxHeight = rowHeight * maxRows;

    textarea.style.height = `${Math.min(scrollHeight, maxHeight)}px`;
  }

  focus() {
    this.chatInputService.focusTextArea();
  }

  addAttachment(addAttachmentButton: HTMLButtonElement, filesInput: HTMLInputElement) {
    this.chatInputService.filesInput?.set(filesInput!);
    this.chatInputService.addAttachment();

    addAttachmentButton.blur();
  }

  stopTyping() {
    this.isTypingService.stopTyping();
  }

  onFilesSelected($event: Event) {
    const input = $event.target as HTMLInputElement;
    if (input.files) {
      Array.from(input.files).forEach((rawFile) => {
        const file: FileModel = {
          file: rawFile,
        };

        this.uploadingFilesCount += input.files!.length;

        this.uploadFile(file);
      });
    }
  }

  removeFile(index: number, file: FileModel) {
    this.files.splice(index, 1);
    this.uploadingFilesCount--;

    if (file.id) {
      this.messageService
        .removeMessageFile(file.id)
        .pipe(untilDestroyed(this))
        .subscribe();
    }
  }

  tryAgain(i: number, file: FileModel) {
    const file$ = this.files[i];

    file$.update((f) => {
      return {
        ...f,
        error: null,
        progress: 0,
      };
    });

    this.uploadRawFile(file, file$);
  }

  private uploadFile(file: FileModel) {
    const file$ = signal({
      file: file,
      progress: 0,
      error: null,
    });

    this.uploadRawFile(file, file$);

    this.files.push(file$);
  }

  private uploadRawFile(file: FileModel, file$: WritableSignal<{ file: FileModel; progress: number; error?: any }>) {
    this.messageService
      .uploadMessageFile(file.file!)
      .pipe(
        untilDestroyed(this),
        map((event) => {
          switch (event.type) {
            case HttpEventType.UploadProgress:
              if (event.total) {
                file$.update((f) => {
                  const uploading_progress_ratio = 80;

                  return {
                    ...f,
                    progress: Math.round((event.loaded / event.total!) * uploading_progress_ratio)
                  };
                });
              }
              break;
            case HttpEventType.Response:
              file$.update((f) => {
                return {
                  ...f,
                  progress: 100
                };
              });
              break;
          }

          return event;
        }),
        catchError((e) => {
          file$.update((f) => {
            return {
              ...f,
              progress: 0,
              error: e,
            };
          });
          return [];
        }),
      )
      .subscribe((x) => {
        if (x.type == HttpEventType.Response) {
          file$.set({
            file: x.body!,
            progress: 100,
            error: null,
          });
          this.uploadingFilesCount--;
        }
      });
  }

  prevent($event: any) {
    $event.preventDefault();
    $event.stopPropagation();
  }
}
