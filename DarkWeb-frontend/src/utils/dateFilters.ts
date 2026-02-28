import { subDays, startOfDay, endOfDay } from 'date-fns';

export type DateRange = 'today' | '7days' | '30days' | '90days' | 'custom';

export interface DateFilterResult {
  startDate: Date;
  endDate: Date;
}

export function getDateRange(range: DateRange, customStart?: Date, customEnd?: Date): DateFilterResult {
  const now = new Date();
  const endDate = endOfDay(now);

  switch (range) {
    case 'today':
      return {
        startDate: startOfDay(now),
        endDate: endDate
      };
    case '7days':
      return {
        startDate: startOfDay(subDays(now, 7)),
        endDate: endDate
      };
    case '30days':
      return {
        startDate: startOfDay(subDays(now, 30)),
        endDate: endDate
      };
    case '90days':
      return {
        startDate: startOfDay(subDays(now, 90)),
        endDate: endDate
      };
    case 'custom':
      if (customStart && customEnd) {
        return {
          startDate: startOfDay(customStart),
          endDate: endOfDay(customEnd)
        };
      }
      return {
        startDate: startOfDay(subDays(now, 30)),
        endDate: endDate
      };
    default:
      return {
        startDate: startOfDay(subDays(now, 30)),
        endDate: endDate
      };
  }
}

export function formatDateForDB(date: Date): string {
  return date.toISOString().split('T')[0];
}
