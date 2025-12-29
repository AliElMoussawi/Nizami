import {AfterViewInit, Component, OnDestroy, OnInit, signal, TemplateRef, viewChild, ViewChild} from '@angular/core';
import {TemplateComponent} from '../../../common/components/template/template.component';
import {Config} from "datatables.net";
import {PaymentsService} from '../../services/payments.service';
import {Payment} from '../../types/payment.types';
import {DataTableDirective, DataTablesModule} from 'angular-datatables';
import {DatePipe, CommonModule} from '@angular/common';
import {catchError, debounceTime, distinctUntilChanged, EMPTY, Subject, take} from 'rxjs';
import {ActionsComponent} from '../../../common/components/actions/actions.component';
import {UntilDestroy, untilDestroyed} from '@ngneat/until-destroy';
import {InputComponent} from '../../../common/components/input/input.component';
import {FormsModule} from '@angular/forms';
import {ToastrService} from 'ngx-toastr';
import {FilterTagComponent} from '../../../common/components/filter-tag/filter-tag.component';
import {extractErrorFromResponse} from '../../../common/utils';
import {PaymentDetailsModalComponent} from '../payment-details-modal/payment-details-modal.component';
import {MatMenuItem} from '@angular/material/menu';

@UntilDestroy()
@Component({
  selector: 'app-payments',
  imports: [
    CommonModule,
    TemplateComponent,
    DataTablesModule,
    ActionsComponent,
    InputComponent,
    FormsModule,
    FilterTagComponent,
    PaymentDetailsModalComponent,
    MatMenuItem,
  ],
  providers: [
    DatePipe,
  ],
  templateUrl: './payments.component.html',
  styleUrl: './payments.component.scss'
})
export class PaymentsComponent implements OnInit, AfterViewInit, OnDestroy {
  dtOptions: Config = {};
  dtElement = viewChild(DataTableDirective);
  @ViewChild('actions') actions!: TemplateRef<ActionsComponent>;
  @ViewChild('status') status!: TemplateRef<any>;

  dtTrigger = new Subject<any>();
  searchText = null;
  statusFilter = signal<string | null>(null);
  currencyFilter = signal<string | null>(null);
  dateFilter = signal<string | null>(null);
  searchChange = new Subject<string>();
  
  // Modal state
  showPaymentModal = signal<boolean>(false);
  selectedPaymentId = signal<string | null>(null);
  
  // Basic transaction counts
  dailyCount = signal<number>(0);
  weeklyCount = signal<number>(0);
  monthlyCount = signal<number>(0);
  totalCount = signal<number>(0);

  constructor(
    private paymentsService: PaymentsService,
    private datePipe: DatePipe,
    private toastr: ToastrService,
  ) {
    this.searchChange
      .pipe(
        untilDestroyed(this),
        debounceTime(500),
        distinctUntilChanged(),
      )
      .subscribe((_x) => {
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
    this.loadTransactionCounts();
  }

  onRowSelect(selectedData: any) {
    // Handle row selection if needed
  }

  onSearch() {
    this.redraw();
  }

  filterClicked(filterType: string, value: string) {
    if (filterType === 'status') {
      if (this.statusFilter() == value) {
        this.statusFilter.set(null);
      } else {
        this.statusFilter.set(value);
      }
    } else if (filterType === 'currency') {
      if (this.currencyFilter() == value) {
        this.currencyFilter.set(null);
      } else {
        this.currencyFilter.set(value);
      }
    }

    this.redraw();
  }

  onSearchInputChange(searchTerm: string) {
    this.searchChange.next(searchTerm);
  }

  onDateFilterChange(date: string) {
    this.dateFilter.set(date);
    this.redraw();
  }

  viewPaymentDetails(payment: Payment) {
    if (!payment?.internal_uuid) {
      return;
    }
    
    this.selectedPaymentId.set(payment.internal_uuid);
    this.showPaymentModal.set(true);
  }

  closePaymentModal() {
    this.showPaymentModal.set(false);
    this.selectedPaymentId.set(null);
  }

  private loadTransactionCounts() {
    // Load basic transaction counts for today, this week, this month
    this.paymentsService.getPaymentStatistics(1).subscribe(stats => {
      this.dailyCount.set(stats.summary.total_payments);
    });

    this.paymentsService.getPaymentStatistics(7).subscribe(stats => {
      this.weeklyCount.set(stats.summary.total_payments);
    });

    this.paymentsService.getPaymentStatistics(30).subscribe(stats => {
      this.monthlyCount.set(stats.summary.total_payments);
    });

    // Load total payments count (all time)
    this.paymentsService.getTotalPaymentsCount().subscribe(count => {
      this.totalCount.set(count);
    });
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
          let extraFilters: any = {};

          if (this.searchText) {
            extraFilters = {
              ...extraFilters,
              search_term: this.searchText,
            };
          }

          if (this.statusFilter()) {
            extraFilters = {
              ...extraFilters,
              status: this.statusFilter(),
            };
          }

          if (this.currencyFilter()) {
            extraFilters = {
              ...extraFilters,
              currency: this.currencyFilter(),
            };
          }

          if (this.dateFilter()) {
            extraFilters = {
              ...extraFilters,
              date_filter: this.dateFilter(),
            };
          }

          dataTablesParameters = {
            ...extraFilters,
            ...dataTablesParameters
          };

          this.paymentsService
            .getPayments(dataTablesParameters)
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
            data: 'id',
            name: 'id',
            title: 'Payment ID',
            width: '200px',
            render: function(data: any, type: any, row: any) {
              return `<span class="font-mono text-sm">${data || 'N/A'}</span>`;
            }
          },
          {
            data: 'status',
            name: 'status',
            width: '120px',
            title: 'Status',
            ngTemplateRef: {
              ref: this.status,
            }
          } as any,
          {
            data: 'amount',
            name: 'amount',
            title: 'Amount',
            render: function(data: any, type: any, row: any) {
              const formatted = row.amount_format || `${data} ${row.currency}`;
              return `<span class="font-medium">${formatted}</span>`;
            }
          },
          {
            data: 'fee',
            name: 'fee',
            title: 'Fee',
            render: function(data: any, type: any, row: any) {
              if (data > 0) {
                const formatted = row.fee_format || `${data} ${row.currency}`;
                return `<span class="text-orange-600">${formatted}</span>`;
              }
              return '<span class="text-gray-400">-</span>';
            }
          },
          {
            data: 'source',
            name: 'source',
            title: 'Payment Method',
            render: function(data: any, type: any, row: any) {
              if (data) {
                const lastFour = data.last_four ? `****${data.last_four}` : '';
                return `
                  <div>
                    <div class="font-medium">${data.company || data.type}</div>
                    ${lastFour ? `<div class="text-sm text-gray-500">${lastFour}</div>` : ''}
                  </div>
                `;
              }
              return '<span class="text-gray-400">-</span>';
            }
          },
          {
            data: 'description',
            name: 'description',
            title: 'Description',
            render: function(data: any, type: any, row: any) {
              return data ? `<span class="text-sm">${data}</span>` : '<span class="text-gray-400">-</span>';
            }
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
                select: self.onRowSelect.bind(this),
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
