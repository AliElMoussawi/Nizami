import {Component, input, OnInit, output, signal} from '@angular/core';
import {FormControl, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';
import {UntilDestroy, untilDestroyed} from '@ngneat/until-destroy';
import {catchError, EMPTY, finalize} from 'rxjs';
import {ToastrService} from 'ngx-toastr';
import {ButtonComponent} from '../../../common/components/button/button.component';
import {FlatButtonComponent} from '../../../common/components/flat-button/flat-button.component';
import {PromptModel} from '../../models/prompt.model';
import {PromptsService} from '../../services/prompts.service';
import {AutoExpandDirective} from '../../../common/directives/auto-expand.directive';
import {extractErrorFromResponse} from '../../../common/utils';

@UntilDestroy()
@Component({
  selector: 'app-edit-prompt',
  imports: [
    ReactiveFormsModule,
    ButtonComponent,
    FlatButtonComponent,
    AutoExpandDirective
  ],
  templateUrl: './edit-prompt.component.html',
  styleUrl: './edit-prompt.component.scss'
})
export class EditPromptComponent implements OnInit {
  isUpdating = signal<boolean>(false);
  prompt = input.required<PromptModel>();

  form = new FormGroup({
    value: new FormControl('', [Validators.required]),
  });
  onUpdated = output<PromptModel>();

  constructor(
    private promptsService: PromptsService,
    private toastr: ToastrService,
  ) {
  }

  ngOnInit() {
    this.form.patchValue(this.prompt());
  }

  submit() {
    this.isUpdating.set(true);

    this.promptsService
      .updatePrompt(this.prompt()!.id, this.form.value)
      .pipe(
        untilDestroyed(this),
        catchError((e) => {
          this.toastr.error(extractErrorFromResponse(e) ?? "Failed updating prompt");

          return EMPTY;
        }),
        finalize(() => {
          this.isUpdating.set(false);
        })
      )
      .subscribe((x) => {
        this.toastr.success('Prompt successfully updated');
        this.onUpdated.emit(x);
      });
  }

  reset() {
    this.form.patchValue(this.prompt());
  }
}
