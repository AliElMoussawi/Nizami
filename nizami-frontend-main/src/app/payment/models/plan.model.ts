export interface Plan {
  uuid: string;
  name: string;
  tier: string;
  description: string;
  price_cents: number;
  currency: string;
  interval_unit: string | null;
  interval_count: number | null;
  is_active: boolean;
  is_deleted: boolean;
  credit_amount: number | null;
  credit_type: string;
  is_unlimited: boolean;
  rollover_allowed: boolean;
}

