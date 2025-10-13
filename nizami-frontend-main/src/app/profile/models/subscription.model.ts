import { Plan } from '../../payment/models/plan.model';

export interface UserSubscription {
  uuid: string;
  user: number;
  plan: Plan;
  is_active: boolean;
  expiry_date: string;
  last_renewed: string | null;
  deactivated_at: string | null;
  created_at: string;
  updated_at: string;
}

