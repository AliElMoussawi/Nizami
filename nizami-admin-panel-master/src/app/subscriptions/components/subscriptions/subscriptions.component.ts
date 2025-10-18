import {AfterViewInit, Component, OnDestroy, OnInit, signal, TemplateRef, viewChild, ViewChild} from '@angular/core';
import {TemplateComponent} from '../../../common/components/template/template.component';
import {Config} from "datatables.net";
import {SubscriptionsService, UserSubscriptionModel} from '../../services/subscriptions.service';
import {DataTableDirective, DataTablesModule} from 'angular-datatables';
import {DatePipe} from '@angular/common';
import {catchError, debounceTime, distinctUntilChanged, EMPTY, Subject, take} from 'rxjs';
import {ActionsComponent} from '../../../common/components/actions/actions.component';
import {UntilDestroy, untilDestroyed} from '@ngneat/until-destroy';
import {InputComponent} from '../../../common/components/input/input.component';
import {FormsModule} from '@angular/forms';
import {RouterLink} from '@angular/router';
import {ToastrService} from 'ngx-toastr';
import {FilterTagComponent} from '../../../common/components/filter-tag/filter-tag.component';
import {MatMenuItem} from '@angular/material/menu';
import {extractErrorFromResponse} from '../../../common/utils';

@UntilDestroy()
@Component({
  selector: 'app-subscriptions',
  imports: [
    TemplateComponent,
    DataTablesModule,
    ActionsComponent,
    InputComponent,
    FormsModule,
    RouterLink,
    FilterTagComponent,
    MatMenuItem,
  ],
  providers: [
    DatePipe,
  ],
  templateUrl: './subscriptions.component.html',
  styleUrl: './subscriptions.component.scss'
})
export class SubscriptionsComponent implements OnInit, AfterViewInit, OnDestroy {
  dtOptions: Config = {};
  dtElement = viewChild(DataTableDirective);
  @ViewChild('actions') actions!: TemplateRef<ActionsComponent>;
  @ViewChild('status') status!: TemplateRef<any>;

  dtTrigger = new Subject<any>();
  searchText = null;
  statusFilter = signal<string | null>(null);
  searchChange = new Subject<string>();

  constructor(
    private subscriptionsService: SubscriptionsService,
    private datePipe: DatePipe,
    private toastr: ToastrService,
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


  filterClicked(status: string) {
    if (this.statusFilter() == status) {
      this.statusFilter.set(null);
    } else {
      this.statusFilter.set(status);
    }

    this.redraw();
  }

  toggleSubscriptionStatus(data: any, is_active: boolean) {
    let subscription = data as UserSubscriptionModel;

    const action = is_active ? 
      this.subscriptionsService.activateSubscription(subscription.uuid) :
      this.subscriptionsService.deactivateSubscription(subscription.uuid);

    action
      .pipe(
        take(1),
        untilDestroyed(this),
        catchError((e) => {
          this.toastr.error(extractErrorFromResponse(e) ?? "Failed to update subscription status");
          return EMPTY;
        }),
      )
      .subscribe(() => {
        this.redraw();
        let message = is_active ? 'activated' : 'deactivated';
        this.toastr.success(`Subscription has been ${message} successfully.`);
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
              is_active: this.statusFilter() === 'active',
            };
          }

          dataTablesParameters = {
            ...extraFilters,
            ...dataTablesParameters
          };

          this.subscriptionsService
            .getSubscriptions(dataTablesParameters)
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
            data: 'user',
            name: 'user',
            title: 'User',
            searchable: false,
            width: '4rem',
            orderable: false,
            render: function(data: any, type: any, row: any) {
              return `
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center">
                    ${row.user.profile_image ? 
                      `<img src="${row.user.profile_image}" alt="${row.user.first_name}" class="w-10 h-10 rounded-full object-cover">` :
                      `<span class="text-gray-600 font-medium">${row.user.first_name.charAt(0)}${row.user.last_name.charAt(0)}</span>`
                    }
                  </div>
                  <div>
                    <div class="font-medium">${row.user.first_name} ${row.user.last_name}</div>
                    <div class="text-sm text-gray-500">${row.user.email}</div>
                  </div>
                </div>
              `;
            }
          },
          {
            data: 'plan',
            name: 'plan',
            title: 'Plan',
            render: function(data: any, type: any, row: any) {
              return `
                <div>
                  <div class="font-medium">${row.plan.name}</div>
                  <div class="text-sm text-gray-500">${row.plan.tier}</div>
                </div>
              `;
            }
          },
          {
            data: 'credit_amount',
            name: 'credit_amount',
            title: 'Credits',
            render: function(data: any, type: any, row: any) {
              if (row.is_unlimited) {
                return '<span class="text-green-600 font-medium">Unlimited</span>';
              }
              return row.credit_amount || '0';
            }
          },
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
            data: 'expiry_date',
            searchable: false,
            ngPipeInstance: this.datePipe,
            ngPipeArgs: ['HH:mm:ss dd/MM/YYYY'],
            className: 'whitespace-nowrap',
            title: 'Expiry Date'
          },
          {
            data: 'created_at',
            searchable: false,
            ngPipeInstance: this.datePipe,
            ngPipeArgs: ['HH:mm:ss dd/MM/YYYY'],
            className: 'whitespace-nowrap',
            title: 'Created At'
          },
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
