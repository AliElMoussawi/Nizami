export interface PaymentSourceBrief {
  type: string | null;
  company: string | null;
  last_four: string | null;
}

export interface Payment {
  id: string;
  status: string;
  amount: number;
  amount_format?: string | null;
  currency: string;
  description?: string | null;
  fee?: number;
  fee_format?: string | null;
  created_at: string;
  updated_at: string;
  metadata?: any;
  source?: PaymentSourceBrief | null;
}


