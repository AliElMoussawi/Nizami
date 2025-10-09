export interface PaginationModel<T> {
  current_page: number;
  per_page: number;
  data: T[];
  last_page: number;
}
