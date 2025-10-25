/**
 * Subscription-related constants
 */

export const CREDIT_TYPES = {
  MESSAGES: 'MESSAGES',
} as const;

export const CREDIT_TYPE_LABELS = {
  [CREDIT_TYPES.MESSAGES]: 'Messages',
} as const;

export const PLAN_TIERS = {
  BASIC: 'BASIC',
  PLUS: 'PLUS',
  PREMIUM: 'PREMIUM',
} as const;

export const PLAN_TIER_LABELS = {
  [PLAN_TIERS.BASIC]: 'Basic',
  [PLAN_TIERS.PLUS]: 'Plus',
  [PLAN_TIERS.PREMIUM]: 'Premium-Monthly',
} as const;

export const INTERVAL_UNITS = {
  MONTH: 'MONTH',
  YEAR: 'YEAR',
} as const;

export const INTERVAL_UNIT_LABELS = {
  [INTERVAL_UNITS.MONTH]: 'month',
  [INTERVAL_UNITS.YEAR]: 'year',
} as const;

export const SUBSCRIPTION_STATUS = {
  ACTIVE: 'ACTIVE',
  INACTIVE: 'INACTIVE',
} as const;

export const SUBSCRIPTION_STATUS_LABELS = {
  [SUBSCRIPTION_STATUS.ACTIVE]: 'Active',
  [SUBSCRIPTION_STATUS.INACTIVE]: 'Inactive',
} as const;
