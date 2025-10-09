import {AfterViewInit, Component, OnDestroy, OnInit, signal, TemplateRef, viewChild, ViewChild} from '@angular/core';
import {TemplateComponent} from '../../../common/components/template/template.component';
import {Config} from "datatables.net";
import {UsersService} from '../../services/users.service';
import {DataTableDirective, DataTablesModule} from 'angular-datatables';
import {DatePipe} from '@angular/common';
import {catchError, debounceTime, distinctUntilChanged, EMPTY, Subject, take} from 'rxjs';
import {ActionsComponent} from '../../../common/components/actions/actions.component';
import {UntilDestroy, untilDestroyed} from '@ngneat/until-destroy';
import {InputComponent} from '../../../common/components/input/input.component';
import {FormsModule} from '@angular/forms';
import {RouterLink} from '@angular/router';
import {ToastrService} from 'ngx-toastr';
import {UserModel} from '../../../common/models/user.model';
import {
  DeleteConfirmationDialogComponent
} from '../../../common/components/delete-confirmation-dialog/delete-confirmation-dialog.component';
import {Dialog} from '@angular/cdk/dialog';
import {UserStatusComponent} from '../user-status/user-status.component';
import {FilterTagComponent} from '../../../common/components/filter-tag/filter-tag.component';
import {MatMenuItem} from '@angular/material/menu';
import {ResetPasswordDialogComponent} from '../reset-password-dialog/reset-password-dialog.component';
import {extractErrorFromResponse} from '../../../common/utils';
import {ProfileImageComponent} from '../profile-image/profile-image.component';

@UntilDestroy()
@Component({
  selector: 'app-users',
  imports: [
    TemplateComponent,
    DataTablesModule,
    ActionsComponent,
    ActionsComponent,
    InputComponent,
    FormsModule,
    RouterLink,
    UserStatusComponent,
    FilterTagComponent,
    MatMenuItem,
    ProfileImageComponent,
  ],
  providers: [
    DatePipe,
  ],
  templateUrl: './users.component.html',
  styleUrl: './users.component.scss'
})
export class UsersComponent implements OnInit, AfterViewInit, OnDestroy {
  dtOptions: Config = {};
  dtElement = viewChild(DataTableDirective);
  @ViewChild('actions') actions!: TemplateRef<ActionsComponent>;
  @ViewChild('status') status!: TemplateRef<UserStatusComponent>;
  @ViewChild('profileImage') profileImage!: TemplateRef<ProfileImageComponent>;

  dtTrigger = new Subject<any>();
  searchText = null;
  statusFilter = signal<string | null>(null);
  searchChange = new Subject<string>();

  constructor(
    private usersService: UsersService,
    private datePipe: DatePipe,
    private toastr: ToastrService,
    private dialog: Dialog,
  ) {
    this.searchChange
      .pipe(
        untilDestroyed(this),
        debounceTime(500),
        distinctUntilChanged(),
      )
      .subscribe((x) => {
        this.onSearch()
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

  deleteUser(data: any) {
    let user = data as UserModel;

    this.dialog.open<boolean>(DeleteConfirmationDialogComponent, {
      data: {
        what: user?.first_name + ' ' + user?.last_name,
        body: 'Are you sure you would like to delete this user?',
      },
    })
      .closed
      .pipe(
        take(1),
        untilDestroyed(this),
      ).subscribe((x) => {
      if (x) {
        this.deleteUserConfirmed(user);
      }
    });
  }

  deleteUserConfirmed(user: UserModel) {
    this.usersService
      .deleteUser(user.id)
      .pipe(
        untilDestroyed(this),
        catchError((e) => {
          this.toastr.error(extractErrorFromResponse(e) ?? "Failed deleting the user");
          return EMPTY;
        }),
      )
      .subscribe(() => {
        this.toastr.success("User successfully deleted");
        this.dtElement()!.dtInstance.then(dtInstance => dtInstance.draw());
      });
  }

  filterClicked(status: string) {
    if (this.statusFilter() == status) {
      this.statusFilter.set(null);
    } else {
      this.statusFilter.set(status);
    }

    this.redraw();
  }

  toggleUserStatus(data: any, is_active: boolean) {
    let user = data as UserModel;

    this
      .usersService
      .changeStatus(user.id, {is_active: is_active})
      .pipe(
        take(1),
        untilDestroyed(this),
      )
      .subscribe(() => {
        this.redraw();

        let message = 'unblocked';
        if (is_active) {
          message = 'blocked';
        }

        this.toastr.success(`User has been ${message} successfully.`);
      });
  }

  resetPassword(data: any) {
    let user = data as UserModel;

    this.dialog
      .open(ResetPasswordDialogComponent, {
        data: {
          user,
        },
      })
      .closed
      .pipe(
        take(1),
        untilDestroyed(this),
      )
      .subscribe();
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
          let extraFilters = {};

          if (this.searchText) {
            extraFilters = {
              ...extraFilters,
              search_term: this.searchText,
            };
          }

          if (this.statusFilter()) {
            extraFilters = {
              ...extraFilters,
              is_active: this.statusFilter() == 'active',
            };
          }

          dataTablesParameters = {
            ...extraFilters,
            ...dataTablesParameters
          };

          this.usersService
            .getUsers(dataTablesParameters)
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
          {
            data: 'profile_image',
            name: 'profile_image',
            title: 'Name',
            searchable: false,
            width: '4rem',
            orderable: false,
            ngTemplateRef: {
              ref: this.profileImage,
            },
          },
          {data: 'full_name', name: 'full_name', title: ''},
          {data: 'email', name: 'email', title: 'Email'},
          {
            data: 'is_active',
            name: 'is_active',
            width: '100px',
            title: 'Status',
            ngTemplateRef: {
              ref: this.status,
            }
          } as any,
          {
            data: 'date_joined',
            searchable: false,
            ngPipeInstance: this.datePipe,
            ngPipeArgs: ['HH:mm:ss dd/MM/YYYY'],
            className: 'whitespace-nowrap',
            title: 'Date of joining'
          },
          {data: 'company_name', name: 'company_name', title: 'Company Name'},
          {
            data: null,
            title: "",
            searchable: false,
            orderable: false,
            width: '10%',
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
