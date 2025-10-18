import {AfterViewInit, Component, OnDestroy, OnInit, TemplateRef, ViewChild} from '@angular/core';
import {TemplateComponent} from '../../../common/components/template/template.component';
import {DataTableDirective, DataTablesModule} from 'angular-datatables';
import {Config} from 'datatables.net';
import {PlansService} from '../../services/plans.service';
import {Subject, debounceTime, take} from 'rxjs';
import {ActionsComponent} from '../../../common/components/actions/actions.component';
import {Router, RouterLink} from '@angular/router';
import {ToastrService} from 'ngx-toastr';
import {PlanModel} from '../../../common/models/plan.model';
import {InputComponent} from '../../../common/components/input/input.component';
import {FormsModule} from '@angular/forms';

@Component({
  selector: 'app-plans',
  standalone: true,
  imports: [
    TemplateComponent,
    DataTablesModule,
    ActionsComponent,
    RouterLink,
    InputComponent,
    FormsModule,
  ],
  templateUrl: './plans.component.html',
  styleUrl: './plans.component.scss'
})
export class PlansComponent implements OnInit, AfterViewInit, OnDestroy {
  dtOptions: Config = {};
  dtTrigger = new Subject<any>();
  @ViewChild(DataTableDirective, { static: false }) dtElement?: DataTableDirective;
  @ViewChild('actions') actions!: TemplateRef<ActionsComponent>;

  searchText: string | null = null;
  private searchDebounce$ = new Subject<string>();
  private allPlans: PlanModel[] = [];
  private tableClickHandler?: (e: Event) => void;
  private tableContainer?: HTMLElement;

  constructor(
    private plansService: PlansService,
    private toastr: ToastrService,
    private router: Router,
  ) {}

  ngOnInit(): void {
    this.initializeDataTable();
    // Debounced frontend-triggered reload
    this.searchDebounce$.pipe(debounceTime(300)).subscribe(() => this.applyFilters());
  }

  ngAfterViewInit(): void {
    setTimeout(() => {
      this.dtTrigger.next(this.dtOptions);
      // Attach a single delegated click handler to avoid duplicate bindings
      this.dtElement?.dtInstance?.then((dt: any) => {
        this.tableContainer = dt.table().container() as HTMLElement;
        this.tableClickHandler = (e: Event) => this.onTableClick(e);
        this.tableContainer.addEventListener('click', this.tableClickHandler!);
        // Load data after table is initialized
        this.loadAll();
      });
    }, 20);
  }

  ngOnDestroy(): void {
    this.dtTrigger.unsubscribe();
    if (this.tableContainer && this.tableClickHandler) {
      this.tableContainer.removeEventListener('click', this.tableClickHandler);
    }
  }

  onSearch() { this.applyFilters(); }

  onSearchChange(value: string) {
    this.searchDebounce$.next(value ?? '');
  }


  redraw() {
    setTimeout(() => this.applyFilters());
  }

  private initializeDataTable() {
    this.dtOptions = {
      paging: true,
      serverSide: false,
      pageLength: 10,
      lengthChange: false,
      lengthMenu: [10],
      processing: true,
      orderCellsTop: true,
      dom: 'rt<"info"i>p<"clear">',
      language: {
        paginate: {
          previous: '<span>Previous</span>',
          next: '<span>Next</span>',
          last: '<span>Last</span>',
          first: '<span>First</span>',
        }
      },
      data: [],
      columns: [
        { title: 'Name', data: 'name' },
        { title: 'Tier', data: 'tier' },
        { title: 'Price (cents)', data: 'price_cents' },
        { title: 'Interval', data: null, render: (data: PlanModel) => `${data.interval_count ?? ''} ${data.interval_unit ?? ''}` },
        { title: 'Deleted', data: 'is_deleted', render: (data: boolean) => data ? '<span class="text-red-600">Yes</span>' : '<span class="text-green-600">No</span>' },
        { title: 'Actions', data: null, orderable: false, searchable: false, className: 'text-center px-4', render: (_: any, __: any, row: PlanModel) => {
            // Force explicit blue for Manage to avoid theme overrides
            const editBtn = `<button class="adt-edit px-3 py-1 rounded-lg text-white bg-blue-600 hover:bg-blue-700" data-action="edit" data-uuid="${row.uuid}">Manage</button>`;
            const activateBtn = `<button class="adt-activate px-3 py-1 rounded-lg text-white bg-green-600 hover:bg-green-700" data-action="activate" data-uuid="${row.uuid}">Activate</button>`;
            const deactivateBtn = `<button class="adt-deactivate px-3 py-1 rounded-lg text-white bg-red-600 hover:bg-red-700" data-action="deactivate" data-uuid="${row.uuid}">Deactivate</button>`;
            return '<div class="py-4 px-2 flex items-center gap-2 justify-center">' + editBtn + (row.is_deleted ? activateBtn : deactivateBtn) + '</div>';
          }
        },
      ],
      // No per-row event bindings; we use a single delegated handler
      rowCallback: (row: Node) => row,
      drawCallback: (settings: any) => {
        // Hide and disable pagination if total fits on one page
        try {
          const api = (settings.oInstance as any).api();
          const info = api.page.info();
          const container = api.table().container() as HTMLElement;
          const paginate = container.querySelector('.dataTables_paginate') as HTMLElement | null;
          const lengthElm = container.querySelector('.dataTables_length') as HTMLElement | null;
          const shouldHide = info.pages <= 1;
          if (paginate) {
            paginate.style.display = shouldHide ? 'none' : '';
            // Additionally disable page links when only one page
            const links = paginate.querySelectorAll('a, button');
            links.forEach((el: Element) => {
              if (shouldHide) {
                (el as HTMLElement).setAttribute('tabindex', '-1');
                (el as HTMLElement).classList.add('pointer-events-none', 'opacity-50');
              } else {
                (el as HTMLElement).removeAttribute('tabindex');
                (el as HTMLElement).classList.remove('pointer-events-none', 'opacity-50');
              }
            });
          }
          if (lengthElm) lengthElm.style.display = shouldHide ? 'none' : '';
        } catch {}
      }
    } as Config;
  }

  private loadAll(successMessage?: string) {
    const params = { page: 1, per_page: 1000 } as any;
    this.plansService
      .list(params)
      .pipe(take(1))
      .subscribe({
        next: (resp: any) => {
          this.allPlans = resp?.data ?? [];
          this.applyFilters();
          if (successMessage) {
            this.toastr.success(successMessage);
          }
        },
        error: () => this.toastr.error('Failed to load plans')
      });
  }

  private applyFilters() {
    const term = (this.searchText ?? '').toLowerCase().trim();
    let rows = this.allPlans;
    if (term) rows = rows.filter(p => (p.name ?? '').toLowerCase().includes(term));

    this.dtElement?.dtInstance?.then((dt: any) => {
      if (dt && dt.clear && dt.rows && dt.rows.add && dt.draw) {
        dt.clear();
        dt.rows.add(rows);
        dt.draw(false);
      }
    });
  }

  private onTableClick(e: Event) {
    const target = e.target as HTMLElement;
    const btn = target.closest('button[data-action]') as HTMLElement | null;
    if (!btn) return;
    const action = btn.dataset['action'];
    const uuid = btn.dataset['uuid'];
    if (!action || !uuid) return;
    const plan = this.allPlans.find(p => p.uuid === uuid);
    if (!plan) return;
    if (action === 'edit') this.onEdit(plan);
    if (action === 'activate') this.onActivate(plan);
    if (action === 'deactivate') this.onDeactivate(plan);
  }

  onAdd() { this.router.navigate(['/plans/create']); }
  onEdit(plan: PlanModel) { this.router.navigate(['/plans', plan.uuid, 'edit']); }
  onActivate(plan: PlanModel) {
    this.plansService.activate(plan.uuid).pipe(take(1)).subscribe({
      next: () => {
        // Immediately reload data from backend and show a single success toast
        this.loadAll('Plan activated');
      },
      error: () => this.toastr.error('Failed to activate'),
    });
  }
  onDeactivate(plan: PlanModel) {
    this.plansService.deactivate(plan.uuid).pipe(take(1)).subscribe({
      next: () => {
        // Immediately reload data from backend and show a single success toast
        this.loadAll('Plan deactivated');
      },
      error: () => this.toastr.error('Failed to deactivate'),
    });
  }
}


