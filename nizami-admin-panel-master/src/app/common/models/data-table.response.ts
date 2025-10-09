export interface DataTableResponse<T> {
  recordsTotal: any;
  recordsFiltered: any;
  data: T[],
}
