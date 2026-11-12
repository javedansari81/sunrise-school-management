import { useMemo } from 'react';
import { useServiceConfiguration } from '../contexts/ConfigurationContext';
import { configurationService } from '../services/configurationService';

/**
 * The school's lists the fee and transport screens need (session years,
 * classes, payment methods, reversal reasons), from the fee-management configuration.
 */
export const useLookups = () => {
  const { isLoaded, isLoading, error } = useServiceConfiguration('fee-management');

  return useMemo(() => {
    const config = isLoaded ? configurationService.getServiceConfiguration('fee-management') : null;
    const active = <T extends { is_active?: boolean }>(list?: T[]): T[] =>
      (list || []).filter((item) => item.is_active !== false);

    const sessionYears = active(config?.session_years);
    const classes = [...active(config?.classes)].sort((a, b) => (a.sort_order ?? 0) - (b.sort_order ?? 0));
    const currentSessionId =
      sessionYears.find((year) => year.is_current)?.id ?? sessionYears[sessionYears.length - 1]?.id ?? null;

    const className = (id?: number | null): string => {
      if (id == null) return 'All classes';
      const found = classes.find((item) => item.id === id);
      return found ? found.description || found.name : `Class ${id}`;
    };
    const sessionName = (id?: number | null): string => sessionYears.find((year) => year.id === id)?.name || '';

    return {
      ready: isLoaded,
      loading: isLoading && !isLoaded,
      error,
      sessionYears,
      classes,
      paymentMethods: active(config?.payment_methods),
      reversalReasons: active(config?.reversal_reasons),
      currentSessionId,
      className,
      sessionName,
    };
  }, [isLoaded, isLoading, error]);
};

export type Lookups = ReturnType<typeof useLookups>;
