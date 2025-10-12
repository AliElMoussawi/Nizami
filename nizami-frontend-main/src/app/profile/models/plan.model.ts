export interface Plan {
  uuid: string;
  name: string;
  tier: string;
  description: string;
  price_cents: number;
  currency: string;
  interval_unit: string;
  interval_count: number;
  is_active: boolean;
  is_deleted: boolean;
  credit_amount: number;
  credit_type: string;
  is_unlimited: boolean;
  rollover_allowed: boolean;
}

export interface PlansResponse {
  data: Plan[];
  current_page: number;
  last_page: number;
  per_page: number;
  total: number;
}
