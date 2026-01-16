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
    // Make updateStatus available globally for DataTables
    (window as any).updateStatus = (id: number, status: 'new' | 'in_progress' | 'closed') => {
      const request = this.userRequests().find(r => r.id === id);
      if (request) {
        this.updateStatus(request, status);
      }
    };
    
    // Make showSummary available globally for DataTables
    (window as any).showSummary = (id: number) => {
      const request = this.userRequests().find(r => r.id === id);
      if (request) {
        this.showSummaryModal.set(true);
        this.selectedSummary.set(request.chat_summary || 'No summary available');
      }
    };
    
    // Initialize DataTable after view is ready
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
            // Hide "Mark In Progress" if status is closed
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
      searching: false, // We handle search manually
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
          console.error('Error loading user requests:', error);
          this.toastr.error('Failed to load user requests');
          this.isLoading.set(false);
          // Initialize empty table on error
          this.dtOptions.data = [];
          setTimeout(() => this.dtTrigger.next(this.dtOptions), 100);
          return EMPTY;
        }),
      )
      .subscribe((requests) => {
        console.log('Loaded user requests:', requests);
        const requestsList = Array.isArray(requests) ? requests : [];
        console.log('Requests list length:', requestsList.length);
        this.userRequests.set(requestsList);
        this.isLoading.set(false);
        
        // Update DataTable options with data
        this.dtOptions.data = requestsList;
        
        // Update DataTable after data is loaded
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

    console.log('Filtered data for DataTable:', filteredData);
    
    // Update DataTable options with filtered data
    this.dtOptions.data = filteredData;
    
    // Update DataTable if it's already initialized
    const dtElement = this.dtElement();
    if (dtElement) {
      try {
        // Check if dtInstance exists and is a Promise
        if (dtElement.dtInstance && typeof dtElement.dtInstance.then === 'function') {
          dtElement.dtInstance.then((instance: any) => {
            if (instance) {
              console.log('Updating DataTable with', filteredData.length, 'rows');
              instance.clear();
              if (filteredData.length > 0) {
                instance.rows.add(filteredData);
              }
              instance.draw();
            } else {
              console.warn('DataTable instance is null');
            }
          }).catch((error: any) => {
            console.error('Error updating DataTable:', error);
            // Redraw the table
            setTimeout(() => this.dtTrigger.next(this.dtOptions), 100);
          });
        } else {
          // DataTable not ready yet, trigger initialization
          console.log('DataTable not ready, triggering initialization');
          this.dtTrigger.next(this.dtOptions);
        }
      } catch (error) {
        console.error('Error accessing DataTable instance:', error);
        // Retry initialization
        setTimeout(() => this.dtTrigger.next(this.dtOptions), 100);
      }
    } else {
      // Element not found, trigger initialization
      console.log('DataTable element not found, triggering initialization');
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
    // Check if in_charge is required
    const requiresInCharge = 
      (request.status === 'new' && newStatus === 'in_progress') ||
      (request.status === 'in_progress' && newStatus === 'closed') ||
      (request.status === 'new' && newStatus === 'closed');
    
    let inCharge = request.in_charge;
    
    if (requiresInCharge && !inCharge) {
      // Prompt for in_charge
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
