export interface FormattedDate {
  relative: string;
  exact: string;
  tier: 'fresh' | 'moderate' | 'standard';
}

export function formatJobDate(dateStr: string): FormattedDate {
  if (!dateStr) {
    return { relative: 'Recently', exact: 'Date unavailable', tier: 'standard' };
  }

  const date = new Date(dateStr);
  if (isNaN(date.getTime())) {
    return { relative: 'Recently', exact: dateStr, tier: 'standard' };
  }

  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  let relative = '';
  let tier: 'fresh' | 'moderate' | 'standard' = 'standard';

  if (diffHours < 1) {
    relative = 'Just now';
    tier = 'fresh';
  } else if (diffHours < 24) {
    relative = `${diffHours}h ago`;
    tier = 'fresh';
  } else if (diffDays === 1) {
    relative = 'Yesterday';
    tier = 'fresh';
  } else if (diffDays < 7) {
    relative = `${diffDays} days ago`;
    tier = diffDays <= 3 ? 'fresh' : 'moderate';
  } else if (diffDays < 14) {
    relative = '1 week ago';
    tier = 'moderate';
  } else if (diffDays < 30) {
    const weeks = Math.floor(diffDays / 7);
    relative = `${weeks} weeks ago`;
    tier = 'moderate';
  } else {
    const months = Math.floor(diffDays / 30);
    relative = `${months} ${months === 1 ? 'month' : 'months'} ago`;
    tier = 'standard';
  }

  const exact = date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });

  return { relative, exact, tier };
}
