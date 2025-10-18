import {Component, Inject} from '@angular/core';
import {FormControl, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';
import {UntilDestroy, untilDestroyed} from '@ngneat/until-destroy';
import {catchError, EMPTY} from 'rxjs';
import {ToastrService} from 'ngx-toastr';
import {ButtonComponent} from '../../../common/components/button/button.component';
import {FlatButtonComponent} from '../../../common/components/flat-button/flat-button.component';
import {InputComponent} from '../../../common/components/input/input.component';
import {ReferenceDocumentsService} from '../../services/reference-documents.service';
import {DIALOG_DATA, DialogRef} from '@angular/cdk/dialog';
import {HttpErrorResponse} from '@angular/common/http';
import {ControlErrorsComponent} from '../../../common/components/errors/control-errors.component';
import {extractErrorFromResponse} from '../../../common/utils';
import {LanguageSelectComponent} from '../../../common/components/language-select/language-select.component';

@UntilDestroy()
@Component({
  selector: 'app-edit-reference-document',
  imports: [
    ReactiveFormsModule,
    ButtonComponent,
    FlatButtonComponent,
    InputComponent,
    ControlErrorsComponent,
    LanguageSelectComponent
  ],
  templateUrl: './edit-reference-document.component.html',
  styleUrl: './edit-reference-document.component.scss'
})
export class EditReferenceDocumentComponent {

  form = new FormGroup({
    name: new FormControl('', [Validators.required]),
    description: new FormControl(null),
    language: new FormControl('ar', Validators.required),
  });

  constructor(
    @Inject(DialogRef) public dialogRef: DialogRef<any>,
    @Inject(DIALOG_DATA) public data: any,
    private refDocsService: ReferenceDocumentsService,
    private toastr: ToastrService,
  ) {
    this.form.patchValue(this.document);
  }

  get document() {
    return this.data.document;
  }

  submit() {
    if (this.form.invalid) {
      return;
    }
    this.form.enable();

    this.refDocsService
      .updateDocument(this.document!.id, this.form.value)
      .pipe(
        untilDestroyed(this),
        catchError((e) => {
          this.toastr.error(extractErrorFromResponse(e) ?? "Failed updating document");

          this.form.enable();

          return EMPTY;
        }),
      )
      .subscribe(() => {
        this.toastr.success('Document successfully updated');

        this.dialogRef.close(true);
      });
  }

  close() {
    this.dialogRef.close(false);
  }
}
