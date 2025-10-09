import {AfterViewInit, Component, OnDestroy, OnInit, TemplateRef, ViewChild, viewChild} from '@angular/core';
import {TemplateComponent} from '../../../common/components/template/template.component';
import {ActionsComponent} from "../../../common/components/actions/actions.component";
import {DataTableDirective, DataTablesModule} from "angular-datatables";
import {InputComponent} from "../../../common/components/input/input.component";
import {NgIcon} from "@ng-icons/core";
import {FormsModule} from '@angular/forms';
import {Config} from 'datatables.net';
import {catchError, debounceTime, distinctUntilChanged, EMPTY, Subject, take} from 'rxjs';
import {DatePipe} from '@angular/common';
import {ToastrService} from 'ngx-toastr';
import {UntilDestroy, untilDestroyed} from '@ngneat/until-destroy';
import {ReferenceDocumentsService} from '../../services/reference-documents.service';
import {ReferenceDocumentModel} from '../../models/reference-document.model';
import {FileSizePipe} from '../../../common/pipes/file-size.pipe';
import {
  DeleteConfirmationDialogComponent
} from '../../../common/components/delete-confirmation-dialog/delete-confirmation-dialog.component';
import {MatMenuItem} from '@angular/material/menu';
import {Dialog} from '@angular/cdk/dialog';
import {CreateReferenceDocumentComponent} from '../create-reference-document/create-reference-document.component';
import {EditReferenceDocumentComponent} from '../edit-reference-document/edit-reference-document.component';
import {extractErrorFromResponse} from '../../../common/utils';
import {FlagComponent} from '../../../common/components/flag/flag.component';
import {ButtonComponent} from '../../../common/components/button/button.component';

@UntilDestroy()
@Component({
  selector: 'app-reference-documents',
  imports: [
    TemplateComponent,
    ActionsComponent,
    DataTablesModule,
    InputComponent,
    NgIcon,
    FormsModule,
    MatMenuItem,
    ButtonComponent
  ],
  providers: [
    DatePipe,
    FileSizePipe,
  ],
  templateUrl: './reference-documents.component.html',
  styleUrl: './reference-documents.component.scss'
})
export class ReferenceDocumentsComponent implements OnInit, AfterViewInit, OnDestroy {
  dtOptions: Config = {};
  dtElement = viewChild(DataTableDirective);
  @ViewChild('actions') actions!: TemplateRef<ActionsComponent>;
  @ViewChild('language') language!: TemplateRef<HTMLDivElement>;
  dtTrigger = new Subject<any>();
  searchText = null;
  searchChange = new Subject<string>();

  constructor(
    private refDocsService: ReferenceDocumentsService,
    private datePipe: DatePipe,
    private fileSizePipe: FileSizePipe,
    private dialog: Dialog,
    private toastr: ToastrService,
  ) {
    this.searchChange
      .pipe(
        untilDestroyed(this),
        debounceTime(500),
        distinctUntilChanged(),
      )
      .subscribe((x) => {
        this.onSearch();
      });
  }

  ngOnDestroy() {
    this.dtTrigger.unsubscribe();
  }

  ngAfterViewInit() {
    setTimeout(() => {
      this.dtTrigger.next(this.dtOptions);
    }, 20);
  }

  ngOnInit(): void {
    this.initializeDataTable();
  }

  async select(x: any) {
  }

  onSearch() {
    this.redraw();
  }

  deleteDocument(data: any) {
    let document = data as ReferenceDocumentModel;

    this.dialog.open<boolean>(DeleteConfirmationDialogComponent, {
      data: {
        what: document.name,
        body: 'Are you sure you would like to delete this document?',
      },
    })
      .closed
      .pipe(
        take(1),
        untilDestroyed(this),
      ).subscribe((x) => {
      if (x) {
        this.deleteDocumentConfirmed(document);
      }
    });
  }

  deleteDocumentConfirmed(document: ReferenceDocumentModel) {
    this.refDocsService
      .deleteDocument(document!.id)
      .pipe(
        untilDestroyed(this),
        catchError((e) => {
          this.toastr.error(extractErrorFromResponse(e) ?? "Failed deleting the reference document");
          return EMPTY;
        }),
      )
      .subscribe(() => {
        this.toastr.success("Reference document successfully deleted");
        this.dtElement()!.dtInstance.then(dtInstance => dtInstance.draw());
      });
  }

  downloadFile(data: any) {
    this.refDocsService
      .downloadDocument(data as ReferenceDocumentModel)
      .pipe(
        untilDestroyed(this),
        take(1),
      )
      .subscribe()
  }

  addNewDocument() {
    this.dialog.open(CreateReferenceDocumentComponent)
      .closed
      .pipe()
      .subscribe((x) => {
        if (x) {
          this.redraw();
        }
      })
  }

  editDocument(data: any) {
    this.dialog.open(EditReferenceDocumentComponent, {
      data: {
        document: data as ReferenceDocumentModel,
      }
    })
      .closed
      .pipe()
      .subscribe((x) => {
        if (x) {
          this.redraw();
        }
      });
  }

  onChange($event: any) {
    this.searchChange.next($event);
  }

  private initializeDataTable() {
    let self = this;

    setTimeout(() => {
      this.dtOptions = {
        paging: true,
        serverSide: true,
        scrollX: true,
        processing: true,
        orderCellsTop: true,
        searchDelay: 2000,
        dom: 'rt<"info"il>p<"clear">',
        language: {
          paginate: {
            previous: '<span>Previous</span>',
            next: '<span>Next</span>',
            last: '<span>Last</span>',
            first: '<span>First</span>',
          }
        },
        ajax: (dataTablesParameters: any, callback: any) => {
          if (this.searchText) {
            dataTablesParameters = {
              ...dataTablesParameters,
              search_term: this.searchText,
            };
          }

          this.refDocsService
            .getDocuments(dataTablesParameters)
            .pipe(
              take(1),
              untilDestroyed(this),
            )
            .subscribe(resp => {
              callback({
                recordsTotal: resp.recordsTotal,
                recordsFiltered: resp.recordsFiltered,
                data: resp.data,
              });
            });
        },
        columns: [
          {data: 'name', name: 'name', title: 'Document Name'},
          {data: 'extension', name: 'extension', title: 'Type'},
          {
            data: 'size',
            name: 'size',
            title: 'Size',
            ngPipeInstance: this.fileSizePipe,
            className: 'whitespace-nowrap'
          },
          {
            data: 'language',
            name: 'language',
            title: 'Language',
            ngTemplateRef: {
              ref: this.language,
            },
          },
          {
            data: 'created_at',
            searchable: false,
            ngPipeInstance: this.datePipe,
            ngPipeArgs: ['HH:mm:ss dd/MM/YYYY'],
            className: 'whitespace-nowrap',
            title: 'Uploaded Date'
          },
          {
            data: 'updated_at',
            searchable: false,
            ngPipeInstance: this.datePipe,
            ngPipeArgs: ['HH:mm:ss dd/MM/YYYY'],
            className: 'whitespace-nowrap',
            title: 'Last modification'
          },
          {
            data: 'created_by_full_name',
            searchable: false,
            title: 'Uploaded By'
          },
          {
            data: null,
            title: "",
            searchable: false,
            orderable: false,
            fixed: true,
            ngTemplateRef: {
              ref: this.actions,
              context: {
                select: self.select.bind(this),
              },
            },
          } as any,
        ],
        autoWidth: false,
      };
    });

  }

  private redraw() {
    this.dtElement()!.dtInstance.then(dtInstance => dtInstance.draw());
  }
}
