import {Injectable} from '@angular/core';
import {Plan} from '../types/subscription.types';
import {PLAN_TIER_LABELS, INTERVAL_UNIT_LABELS} from '../constants/subscription.constants';

@Injectable({
  providedIn: 'root'
})
export class SubscriptionUtilsService {

  /**
   * Format plan display name with tier and pricing
   */
  formatPlanDisplayName(plan: Plan): string {
    const tierLabel = PLAN_TIER_LABELS[plan.tier as keyof typeof PLAN_TIER_LABELS] || plan.tier;
    const price = plan.price || (plan.price_cents ? plan.price_cents / 100 : 0);
    const interval = plan.interval_unit ? INTERVAL_UNIT_LABELS[plan.interval_unit as keyof typeof INTERVAL_UNIT_LABELS] || plan.interval_unit.toLowerCase() : 'month';
    
    return `${plan.name} - ${tierLabel} ($${price}/${interval})`;
  }

  /**
   * Format plan properties for display
   */
  formatPlanProperties(plan: Plan): string {
    if (plan.is_unlimited) {
      return `Unlimited ${plan.credit_type || 'credits'}`;
    }
    return `${plan.credit_amount} ${plan.credit_type || 'credits'}`;
  }

  /**
   * Check if plan is advanced tier
   */
  isAdvancedPlan(plan: Plan): boolean {
    return plan.tier === 'ADVANCED_PLUS';
  }

  /**
   * Get plan price in dollars
   */
  getPlanPriceInDollars(plan: Plan): number {
    return plan.price || (plan.price_cents ? plan.price_cents / 100 : 0);
  }

  /**
   * Get interval unit label
   */
  getIntervalUnitLabel(plan: Plan): string {
    return plan.interval_unit ? 
      INTERVAL_UNIT_LABELS[plan.interval_unit as keyof typeof INTERVAL_UNIT_LABELS] || plan.interval_unit.toLowerCase() : 
      'month';
  }
}
