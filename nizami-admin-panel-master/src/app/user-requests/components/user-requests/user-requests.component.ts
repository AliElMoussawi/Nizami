import {AfterViewInit, Component, OnDestroy, OnInit, signal, viewChild} from '@angular/core';
import {TemplateComponent} from '../../../common/components/template/template.component';
import {Config} from "datatables.net";
import {UserRequestsService, UserRequest} from '../../services/user-requests.service';
import {DataTableDirective, DataTablesModule} from 'angular-datatables';
import {DatePipe, CommonModule} from '@angular/common';
import {catchError, EMPTY, Subject} from 'rxjs';
import {UntilDestroy, untilDestroyed} from '@ngneat/until-destroy';
import {InputComponent} from '../../../common/components/input/input.component';
import {FormsModule} from '@angular/forms';
import {ToastrService} from 'ngx-toastr';
import {FilterTagComponent} from '../../../common/components/filter-tag/filter-tag.component';

@UntilDestroy()
@Component({
  selector: 'app-user-requests',
  imports: [
    CommonModule,
    TemplateComponent,
    DataTablesModule,
    InputComponent,
    FormsModule,
    FilterTagComponent,
  ],
  providers: [
    DatePipe,
  ],
  templateUrl: './user-requests.component.html',
  styleUrl: './user-requests.component.scss'
})
export class UserRequestsComponent implements OnInit, AfterViewInit, OnDestroy {
  dtOptions: Config = {};
  dtElement = viewChild(DataTableDirective);

  dtTrigger = new Subject<any>();
  searchText = '';
  statusFilter = signal<string | null>(null);
  
  userRequests = signal<UserRequest[]>([]);
  isLoading = signal<boolean>(false);
  showSummaryModal = signal<boolean>(false);
  selectedSummary = signal<string>('');

  constructor(
    private userRequestsService: UserRequestsService,
    private datePipe: DatePipe,
    private toastr: ToastrService,
  ) {
  }

  ngOnDestroy() {
    this.dtTrigger.unsubscribe();
  }

  ngAfterViewInit() {
    (window as any).updateStatus = (id: number, status: 'new' | 'in_progress' | 'closed') => {
      const request = this.userRequests().find(r => r.id === id);
      if (request) {
        this.updateStatus(request, status);
      }
    };
    
    (window as any).showSummary = (id: number) => {
      const request = this.userRequests().find(r => r.id === id);
      if (request) {
        this.showSummaryModal.set(true);
        this.selectedSummary.set(request.chat_summary || 'No summary available');
      }
    };
    
    setTimeout(() => {
      this.dtTrigger.next(this.dtOptions);
    }, 100);
  }

  ngOnInit(): void {
    this.initializeDataTable();
    this.loadUserRequests();
  }

  initializeDataTable() {
    const self = this;
    this.dtOptions = {
      data: [],
      columns: [
        {
          title: 'ID',
          data: 'id',
        },
        {
          title: 'User Email',
          data: 'user_email',
        },
        {
          title: 'User Phone',
          data: 'user_phone',
          defaultContent: 'N/A',
        },
        {
          title: 'Chat Title',
          data: 'chat_title',
        },
        {
          title: 'Chat Summary',
          data: 'chat_summary',
          orderable: false,
          render: (data: any, type: any, row: UserRequest) => {
            return `<button class="px-3 py-1 text-sm bg-blue-100 text-blue-800 rounded hover:bg-blue-200" onclick="window.showSummary(${row.id})">Show</button>`;
          },
        },
        {
          title: 'Status',
          data: 'status',
          render: (data: any) => {
            return `<span class="status-badge status-${data}">${this.formatStatus(data)}</span>`;
          },
        },
        {
          title: 'In Charge',
          data: 'in_charge',
          defaultContent: '-',
          render: (data: any) => {
            return data || '-';
          },
        },
        {
          title: 'Created At',
          data: 'created_at_ts',
          render: (data: any) => {
            return this.datePipe.transform(data, 'short') || '';
          },
        },
        {
          title: 'Actions',
          data: null,
          orderable: false,
          defaultContent: '',
          render: (data: any, type: any, row: UserRequest) => {
            let buttons = '';
            if (row.status !== 'in_progress' && row.status !== 'closed') {
              buttons += `<button class="px-3 py-1 text-sm bg-yellow-100 text-yellow-800 rounded hover:bg-yellow-200 mr-2" onclick="window.updateStatus(${row.id}, 'in_progress')">Mark In Progress</button>`;
            }
            if (row.status !== 'closed') {
              buttons += `<button class="px-3 py-1 text-sm bg-green-100 text-green-800 rounded hover:bg-green-200" onclick="window.updateStatus(${row.id}, 'closed')">Mark Closed</button>`;
            }
            return buttons || '-';
          },
        },
      ],
      order: [[0, 'desc']],
      paging: true,
      pageLength: 10,
      searching: false,
      info: true,
      autoWidth: false,
      language: {
        emptyTable: 'No legal assistance requests found',
        zeroRecords: 'No matching requests found',
      },
    };
  }

  loadUserRequests() {
    this.isLoading.set(true);
    this.userRequestsService.getUserRequests()
      .pipe(
        untilDestroyed(this),
        catchError((error) => {
          this.toastr.error('Failed to load user requests');
          this.isLoading.set(false);
          this.dtOptions.data = [];
          setTimeout(() => this.dtTrigger.next(this.dtOptions), 100);
          return EMPTY;
        }),
      )
        .subscribe((requests) => {
        const requestsList = Array.isArray(requests) ? requests : [];
        this.userRequests.set(requestsList);
        this.isLoading.set(false);
        
        this.dtOptions.data = requestsList;
        
        setTimeout(() => {
          this.updateDataTable(requestsList);
        }, 150);
      });
  }

  updateDataTable(data: UserRequest[]) {
    let filteredData = data;

    if (this.statusFilter()) {
      filteredData = filteredData.filter(r => r.status === this.statusFilter());
    }

    if (this.searchText) {
      const searchLower = this.searchText.toLowerCase();
      filteredData = filteredData.filter(r =>
        r.user_email.toLowerCase().includes(searchLower) ||
        r.chat_title.toLowerCase().includes(searchLower) ||
        (r.user_phone && r.user_phone.toLowerCase().includes(searchLower))
      );
    }

    this.dtOptions.data = filteredData;
    
    const dtElement = this.dtElement();
    if (dtElement) {
      try {
        if (dtElement.dtInstance && typeof dtElement.dtInstance.then === 'function') {
          dtElement.dtInstance.then((instance: any) => {
            if (instance) {
              instance.clear();
              if (filteredData.length > 0) {
                instance.rows.add(filteredData);
              }
              instance.draw();
            }
          }).catch(() => {
            setTimeout(() => this.dtTrigger.next(this.dtOptions), 100);
          });
        } else {
          this.dtTrigger.next(this.dtOptions);
        }
      } catch {
        setTimeout(() => this.dtTrigger.next(this.dtOptions), 100);
      }
    } else {
      this.dtTrigger.next(this.dtOptions);
    }
  }

  onSearch() {
    this.updateDataTable(this.userRequests());
  }

  onSearchInputChange(value: string) {
    this.searchText = value;
    this.onSearch();
  }

  filterClicked(type: string, value: string) {
    if (this.statusFilter() === value) {
      this.statusFilter.set(null);
    } else {
      this.statusFilter.set(value);
    }
    this.onSearch();
  }

  formatStatus(status: string): string {
    return status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ');
  }

  updateStatus(request: UserRequest, newStatus: 'new' | 'in_progress' | 'closed') {
    const requiresInCharge = 
      (request.status === 'new' && newStatus === 'in_progress') ||
      (request.status === 'in_progress' && newStatus === 'closed') ||
      (request.status === 'new' && newStatus === 'closed');
    
    let inCharge = request.in_charge;
    
    if (requiresInCharge && !inCharge) {
      inCharge = prompt('Please enter the name of the person in charge (required):');
      if (!inCharge || !inCharge.trim()) {
        this.toastr.error('In Charge field is required for this status change');
        return;
      }
    }
    
    this.userRequestsService.updateUserRequestStatus(request.id, newStatus, inCharge || undefined)
      .pipe(
        untilDestroyed(this),
        catchError((error) => {
          const errorMessage = error?.error?.in_charge?.[0] || error?.error?.detail || 'Failed to update request status';
          this.toastr.error(errorMessage);
          return EMPTY;
        }),
      )
      .subscribe(() => {
        this.toastr.success('Request status updated');
        this.loadUserRequests();
      });
  }
  
  closeSummaryModal() {
    this.showSummaryModal.set(false);
    this.selectedSummary.set('');
  }

  getChatSummary(request: UserRequest): string {
    return request.chat_summary || 'No summary available';
  }
}
