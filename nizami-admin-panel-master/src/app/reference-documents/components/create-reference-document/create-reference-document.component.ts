import {Component, Inject, input, signal} from '@angular/core';
import {FormControl, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';
import {UntilDestroy, untilDestroyed} from '@ngneat/until-destroy';
import {catchError, EMPTY, finalize} from 'rxjs';
import {ToastrService} from 'ngx-toastr';
import {ReferenceDocumentsService} from '../../services/reference-documents.service';
import {UserModel} from '../../../common/models/user.model';
import {ButtonComponent} from '../../../common/components/button/button.component';
import {FlatButtonComponent} from '../../../common/components/flat-button/flat-button.component';
import {InputComponent} from '../../../common/components/input/input.component';
import {ControlErrorsComponent} from '../../../common/components/errors/control-errors.component';
import {FileDragZoneComponent} from '../file-drag-zone/file-drag-zone.component';
import {convertToFormData, extractErrorFromResponse} from '../../../common/utils';
import {DialogRef} from '@angular/cdk/dialog';
import {HttpErrorResponse} from '@angular/common/http';
import {LanguageSelectComponent} from '../../../common/components/language-select/language-select.component';

@UntilDestroy()
@Component({
  selector: 'app-create-reference-document',
  imports: [
    ReactiveFormsModule,
    ControlErrorsComponent,
    ButtonComponent,
    FlatButtonComponent,
    InputComponent,
    FileDragZoneComponent,
    LanguageSelectComponent,
  ],
  templateUrl: './create-reference-document.component.html',
  styleUrl: './create-reference-document.component.scss'
})
export class CreateReferenceDocumentComponent {
  isCreating = signal<boolean>(false);
  value = input<UserModel | null>(null);
  form = new FormGroup({
    name: new FormControl(null, Validators.required),
    description: new FormControl(null),
    language: new FormControl('ar', Validators.required),
    file: new FormControl<File | null | string>(null, Validators.required),
  });

  constructor(
    @Inject(DialogRef) public dialogRef: DialogRef<any>,
    private referenceDocument: ReferenceDocumentsService,
    private toastr: ToastrService,
  ) {
  }

  submit() {
    if (this.form.invalid) {
      return;
    }

    this.isCreating.set(true);

    this.referenceDocument
      .createDocument(convertToFormData(this.form.value))
      .pipe(
        untilDestroyed(this),
        catchError((e) => {
          this.toastr.error(extractErrorFromResponse(e) ?? "Failed creating document");

          return EMPTY;
        }),
        finalize(() => {
          this.isCreating.set(false);
        })
      )
      .subscribe(() => {
        this.toastr.success('Reference document successfully created');
        this.dialogRef.close(true);
      });
  }

  close() {
    this.dialogRef.close(false);
  }
}
