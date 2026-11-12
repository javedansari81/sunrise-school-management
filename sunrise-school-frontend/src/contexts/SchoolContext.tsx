import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import { apiConfig } from '../config/apiConfig';
import { SCHOOL_CODE } from '../config/school';

export interface SchoolBranding {
  code: string | null;
  name: string;
  shortName: string;
  /** Null when the school has no logo; show its initial instead. */
  logoUrl: string | null;
  address?: string | null;
  phone?: string | null;
  email?: string | null;
  website?: string | null;
  currency: string;
}

interface SchoolContextType {
  school: SchoolBranding;
  /** False until the API answered (or failed); the defaults are shown meanwhile. */
  ready: boolean;
  /** Set when this address belongs to no school, or to a suspended one. */
  problem: string | null;
}

// The logo shipped with the app belongs to the school the app started with
const HOME_SCHOOL_CODE = (process.env.REACT_APP_DEFAULT_SCHOOL_CODE || 'sunrise').toLowerCase();
const HOME_LOGO = '/images/logo/school_logo.jpeg';
const logoFor = (code: string | null, logoUrl?: string | null): string | null =>
  logoUrl || (code === null || code === HOME_SCHOOL_CODE ? HOME_LOGO : null);
const DEFAULT_NAME = process.env.REACT_APP_SCHOOL_NAME || 'School Portal';

const fallback: SchoolBranding = {
  code: SCHOOL_CODE,
  name: DEFAULT_NAME,
  shortName: DEFAULT_NAME,
  logoUrl: logoFor(SCHOOL_CODE),
  currency: 'INR',
};

const CACHE_KEY = `schoolBranding:${SCHOOL_CODE || 'default'}`;

const readCache = (): SchoolBranding | null => {
  try {
    const raw = sessionStorage.getItem(CACHE_KEY);
    return raw ? (JSON.parse(raw) as SchoolBranding) : null;
  } catch {
    return null;
  }
};

const SchoolContext = createContext<SchoolContextType>({ school: fallback, ready: false, problem: null });

export const useSchool = (): SchoolContextType => useContext(SchoolContext);

const setFavicon = (href: string) => {
  document.querySelectorAll<HTMLLinkElement>('link[rel~="icon"], link[rel="apple-touch-icon"]').forEach((link) => {
    link.href = href;
  });
};

export const SchoolProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const cached = useMemo(readCache, []);
  const [school, setSchool] = useState<SchoolBranding>(cached || fallback);
  const [ready, setReady] = useState(false);
  const [problem, setProblem] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    axios
      .create(apiConfig)
      .get('/public/school')
      .then(({ data }) => {
        if (cancelled) return;
        const branding: SchoolBranding = {
          code: data.code,
          name: data.name,
          shortName: data.short_name || data.name,
          logoUrl: logoFor(data.code, data.logo_url),
          address: data.address,
          phone: data.phone,
          email: data.email,
          website: data.website,
          currency: data.currency || 'INR',
        };
        setSchool(branding);
        try {
          sessionStorage.setItem(CACHE_KEY, JSON.stringify(branding));
        } catch {
          /* private mode: branding is simply fetched again next time */
        }
      })
      .catch((error) => {
        if (cancelled) return;
        const status = error?.response?.status;
        if (status === 404) setProblem('No school is registered at this address.');
        else if (status === 403) setProblem('This school is currently suspended.');
        // Any other failure (API down): keep the defaults, the pages report their own errors
      })
      .finally(() => !cancelled && setReady(true));
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!window.location.pathname.startsWith('/platform')) document.title = school.name;
    setFavicon(school.logoUrl || '/favicon.ico');
  }, [school]);

  const value = useMemo(() => ({ school, ready, problem }), [school, ready, problem]);
  return <SchoolContext.Provider value={value}>{children}</SchoolContext.Provider>;
};

export default SchoolContext;
