export interface Payment {
  id: string;
  internal_uuid: string;
  status: string;
  amount: number;
  fee: number;
  currency: string;
  refunded: number;
  refunded_at?: string;
  captured: number;
  captured_at?: string;
  voided_at?: string;
  description?: string;
  amount_format?: string;
  fee_format?: string;
  created_at: string;
  updated_at: string;
  metadata: any;
  source?: {
    type: string;
    company?: string;
    last_four?: string;
  };
  admin_info?: {
    ip_address?: string;
    user_agent?: string;
    subscription_link?: {
      subscription_uuid: string;
      user_email: string;
      plan_name: string;
    };
  };
}

export interface PaymentStatistics {
  summary: {
    total_payments: number;
    period_days: number;
  };
}

export interface DataTableResponse<T> {
  data: T[];
  recordsTotal: number;
  recordsFiltered: number;
}
