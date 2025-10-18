/**
 * Subscription-related type definitions
 */

export interface User {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  profile_image?: string;
}

export interface Plan {
  uuid: string;
  name: string;
  description: string;
  price: number;
  price_cents: number;
  tier: string;
  is_deleted: boolean;
  credit_amount: number | null;
  credit_type: string | null;
  is_unlimited: boolean;
  created_at: string;
  updated_at: string;
  currency: string;
  interval_unit: string | null;
  interval_count: number | null;
  is_active: boolean;
  rollover_allowed: boolean;
}

export interface UserSubscription {
  uuid: string;
  user: User;
  plan: Plan;
  is_active: boolean;
  credit_amount: number | null;
  credit_type: string;
  is_unlimited: boolean;
  expiry_date: string;
  last_renewed: string | null;
  deactivated_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateSubscriptionRequest {
  user_email: string;
  plan: string;
  credit_amount?: number | null;
  credit_type?: string;
  is_unlimited?: boolean;
  expiry_date: string;
}

export interface UpdateSubscriptionRequest {
  is_active?: boolean;
  credit_amount?: number | null;
  credit_type?: string;
  is_unlimited?: boolean;
  expiry_date?: string;
}

export interface PaginatedResponse<T> {
  current_page: number;
  per_page: number;
  last_page: number;
  data: T[];
}

export interface DataTableResponse<T> {
  data: T[];
  recordsTotal: number;
  recordsFiltered: number;
  draw: number;
}
