/**
 * CareerLoom INR CTC & Compensation Intelligence Formatter
 * Compliant with frontend-skill design principles and Indian Tech Market Benchmarks.
 */

export interface CTCInfo {
  display: string;
  isEstimated: boolean;
  tierBadge: string;
  tierName?: string;
  benchmarkDetails?: string;
}

const TIER_1_UNICORNS = new Set([
  'swiggy', 'cred', 'meesho', 'groww', 'inmobi', 'glance', 'slice', 'paytm',
  'pocket fm', 'sarvam ai', 'atlan', 'signoz', 'navi', 'zeta', 'mindtickle',
  'cars24', 'nobroker', 'ixigo', 'upstox', 'hackerrank', 'entropik tech',
  'bluestone', 'fampay', 'porter', 'kredx', 'lendingkart', 'unacademy'
]);

const GCC_ENTERPRISE = new Set([
  'thoughtworks', 'highradius', 'zenoti', 'druva', 'tcs', 'freshworks',
  'truecaller', 'truecaller india', 'kovai.co', 'shipsy', 'acceldata',
  'entrupy', 'target india gcc', 'walmart global tech india',
  'morgan stanley india gcc', 'goldman sachs india gcc', 'jp morgan india gcc'
]);

const INDIAN_CITIES = [
  'bengaluru', 'bangalore', 'blr',
  'delhi', 'gurgaon', 'gurugram', 'noida', 'ncr', 'new delhi',
  'hyderabad', 'hyd', 'secunderabad',
  'pune', 'pun',
  'mumbai', 'bombay', 'bom', 'navi mumbai', 'thane',
  'chennai', 'madras', 'maa',
  'ahmedabad', 'kolkata', 'kochi', 'indore', 'jaipur'
];

export function isIndianJob(country?: string, location?: string): boolean {
  if (country && country.toLowerCase().trim() === 'india') return true;
  if (!location) return false;
  const loc = location.toLowerCase();
  return INDIAN_CITIES.some(city => loc.includes(city));
}

/**
 * Parses explicit compensation mentions from text (title, summary, tags).
 */
export function extractExplicitCTC(text: string): string | null {
  if (!text) return null;

  // Pattern 1: ₹ 20 - 35 LPA / ₹25-40 Lakhs / 20-35 LPA
  const rangeMatch = text.match(/(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*(?:-|to)\s*(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*(?:lpa|lakhs?|lac|l\b)/i);
  if (rangeMatch) {
    return `₹${rangeMatch[1]} - ${rangeMatch[2]} LPA`;
  }

  // Pattern 2: ₹ 45 LPA+ / ₹30 Lakhs
  const singleMatch = text.match(/(?:₹|rs\.?|inr)\s*(\d+(?:\.\d+)?)\s*(?:lpa|lakhs?|lac|l\b)\+?/i);
  if (singleMatch) {
    return `₹${singleMatch[1]} LPA`;
  }

  // Pattern 3: Explicit LPA without currency symbol (e.g. "30 LPA", "25-35 LPA")
  const lpaMatch = text.match(/(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)\s*(?:lpa)/i);
  if (lpaMatch) {
    return `₹${lpaMatch[1]} - ${lpaMatch[2]} LPA`;
  }

  // Pattern 4: Monthly stipend (internships): ₹40,000 - ₹80,000 / month
  const stipendMatch = text.match(/(?:₹|rs\.?|inr)?\s*(\d+)(?:k|,000)?\s*(?:-|to)\s*(?:₹|rs\.?|inr)?\s*(\d+)(?:k|,000)?\s*(?:\/|\s*per\s*)?(?:month|mo)/i);
  if (stipendMatch) {
    return `₹${stipendMatch[1]}k - ${stipendMatch[2]}k / mo`;
  }

  return null;
}

/**
 * Returns CTC compensation intelligence for a job.
 * If verified CTC is available in the listing, returns verified badge.
 * Otherwise for Indian tech listings, computes market-calibrated benchmark.
 */
export function getCTCInfo(
  company: string,
  title: string,
  country: string,
  location: string,
  seniority: string = 'mid',
  category: string = 'software_engineering',
  rawTags: string[] = [],
  descriptionSummary: string = ''
): CTCInfo | null {
  // 1. Check for explicit compensation in tags, title, or description
  const combinedText = `${title} ${rawTags.join(' ')} ${descriptionSummary}`;
  const explicit = extractExplicitCTC(combinedText);
  if (explicit) {
    return {
      display: explicit,
      isEstimated: false,
      tierBadge: 'Verified CTC',
      benchmarkDetails: 'Direct from employer posting',
    };
  }

  // 2. Check if job is in India
  if (!isIndianJob(country, location)) {
    // Non-India job - check for USD/EUR ranges if present
    const usdMatch = combinedText.match(/\$(\d{2,3})k?\s*(?:-|to)\s*\$?(\d{2,3})k/i);
    if (usdMatch) {
      return {
        display: `$${usdMatch[1]}k - $${usdMatch[2]}k`,
        isEstimated: false,
        tierBadge: 'Verified Comp',
      };
    }
    return null;
  }

  // 3. Indian Tech Compensation Benchmark Engine
  const compLower = company.toLowerCase().trim();
  const sen = seniority.toLowerCase().trim();
  const isAI = category === 'data_ai';

  let tier = 'startup';
  let tierName = 'Indian Tech Ecosystem';
  if (TIER_1_UNICORNS.has(compLower)) {
    tier = 'tier1';
    tierName = 'Tier-1 Product Unicorn';
  } else if (GCC_ENTERPRISE.has(compLower) || compLower.includes('gcc') || compLower.includes('global tech')) {
    tier = 'gcc';
    tierName = 'Global GCC / Enterprise';
  }

  let range = '';
  if (tier === 'tier1') {
    if (isAI) {
      switch (sen) {
        case 'intern': range = '₹50k - ₹1.2L / mo'; break;
        case 'entry': range = '₹22 - ₹36 LPA'; break;
        case 'senior': range = '₹60 - ₹95 LPA'; break;
        case 'lead': range = '₹95L - ₹1.6 Cr'; break;
        case 'mid':
        default: range = '₹36 - ₹62 LPA'; break;
      }
    } else {
      switch (sen) {
        case 'intern': range = '₹40k - ₹1.0L / mo'; break;
        case 'entry': range = '₹18 - ₹32 LPA'; break;
        case 'senior': range = '₹55 - ₹85 LPA'; break;
        case 'lead': range = '₹85L - ₹1.4 Cr'; break;
        case 'mid':
        default: range = '₹32 - ₹55 LPA'; break;
      }
    }
  } else if (tier === 'gcc') {
    if (isAI) {
      switch (sen) {
        case 'intern': range = '₹30k - ₹60k / mo'; break;
        case 'entry': range = '₹14 - ₹25 LPA'; break;
        case 'senior': range = '₹42 - ₹68 LPA'; break;
        case 'lead': range = '₹68L - ₹1.1 Cr'; break;
        case 'mid':
        default: range = '₹25 - ₹42 LPA'; break;
      }
    } else {
      switch (sen) {
        case 'intern': range = '₹25k - ₹50k / mo'; break;
        case 'entry': range = '₹12 - ₹22 LPA'; break;
        case 'senior': range = '₹38 - ₹60 LPA'; break;
        case 'lead': range = '₹60 - ₹95 LPA'; break;
        case 'mid':
        default: range = '₹22 - ₹38 LPA'; break;
      }
    }
  } else {
    // Growth Tech Startups
    if (isAI) {
      switch (sen) {
        case 'intern': range = '₹25k - ₹50k / mo'; break;
        case 'entry': range = '₹10 - ₹18 LPA'; break;
        case 'senior': range = '₹35 - ₹55 LPA'; break;
        case 'lead': range = '₹55 - ₹90 LPA'; break;
        case 'mid':
        default: range = '₹18 - ₹35 LPA'; break;
      }
    } else {
      switch (sen) {
        case 'intern': range = '₹20k - ₹40k / mo'; break;
        case 'entry': range = '₹8 - ₹16 LPA'; break;
        case 'senior': range = '₹30 - ₹50 LPA'; break;
        case 'lead': range = '₹50 - ₹80 LPA'; break;
        case 'mid':
        default: range = '₹16 - ₹30 LPA'; break;
      }
    }
  }

  return {
    display: range,
    isEstimated: true,
    tierBadge: tier === 'tier1' ? 'Unicorn Benchmark' : tier === 'gcc' ? 'GCC Benchmark' : 'Market Benchmark',
    tierName,
    benchmarkDetails: `Estimated compensation band for ${sen.toUpperCase()} at ${tierName}`,
  };
}
