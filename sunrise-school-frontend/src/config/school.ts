/**
 * Which school this browser tab is for.
 *
 * Order: REACT_APP_SCHOOL_CODE (fixed, single-school deployments and local
 * testing), then the subdomain under REACT_APP_BASE_DOMAIN
 * (sunrise.myschools.in -> sunrise), then a `<code>.localhost` hostname in
 * development. With none of these the API decides (its default school).
 */
const RESERVED = ['www', 'api', 'app', 'admin', 'platform'];
const CODE_RE = /^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$/;

const clean = (value?: string | null): string | null => {
  const code = (value || '').trim().toLowerCase();
  return CODE_RE.test(code) && !RESERVED.includes(code) ? code : null;
};

export const resolveSchoolCode = (hostname: string = window.location.hostname): string | null => {
  const fixed = clean(process.env.REACT_APP_SCHOOL_CODE);
  if (fixed) return fixed;

  const host = hostname.toLowerCase().replace(/\.$/, '');
  const bases = [(process.env.REACT_APP_BASE_DOMAIN || '').trim().toLowerCase().replace(/^\./, ''), 'localhost'];
  for (const base of bases) {
    if (base && host.endsWith(`.${base}`)) {
      const label = host.slice(0, -(base.length + 1));
      // Only a single label directly under the base domain is a school
      if (!label.includes('.')) return clean(label);
    }
  }
  return null;
};

export const SCHOOL_CODE = resolveSchoolCode();
export const SCHOOL_CODE_HEADER = 'X-School-Code';

/** Header that tells the API which school a request is for (empty when the host decides). */
export const schoolHeaders = (): Record<string, string> =>
  SCHOOL_CODE ? { [SCHOOL_CODE_HEADER]: SCHOOL_CODE } : {};
