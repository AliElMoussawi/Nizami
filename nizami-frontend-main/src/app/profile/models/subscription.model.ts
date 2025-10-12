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

export interface UserSubscription {
  uuid: string;
  user: string;
  plan: Plan;
  is_active: boolean;
  expiry_date: string;
  last_renewed: string | null;
  deactivated_at: string | null;
  created_at: string;
  updated_at: string;
}
