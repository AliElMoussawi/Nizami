export interface PaginationModel<T> {
  current_page: number;
  per_page: number;
  data: T[];
  last_page: number;
}

export interface IdPaginationModel<T> {
  data: T[];
  last_id: number | null;
}
