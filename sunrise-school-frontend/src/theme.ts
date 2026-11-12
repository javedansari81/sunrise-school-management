import { alpha, createTheme } from '@mui/material/styles';

/** Colours and effects shared by the theme and the portal shell. */
export const brand = {
  primary: '#2563eb',
  primaryDark: '#1d4ed8',
  violet: '#7c3aed',
  accent: '#f97316',
  ink: '#0f172a',
  // Left panel
  navTop: '#0b1437',
  navMid: '#131c52',
  navBottom: '#1e1b6b',
  gradient: 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)',
  gradientWarm: 'linear-gradient(135deg, #f97316 0%, #ec4899 100%)',
  gradientHero: 'linear-gradient(120deg, #0b1437 0%, #1d4ed8 55%, #7c3aed 100%)',
  pageBackground:
    'radial-gradient(1100px 520px at 100% -10%, rgba(124,58,237,0.10), transparent 60%),' +
    'radial-gradient(900px 480px at -10% 0%, rgba(37,99,235,0.10), transparent 55%),' +
    '#f4f6fb',
  shadowSoft: '0 1px 2px rgba(15,23,42,0.04), 0 8px 24px rgba(15,23,42,0.06)',
  shadowLift: '0 2px 4px rgba(15,23,42,0.05), 0 18px 40px rgba(37,99,235,0.16)',
  shadowGlow: '0 8px 22px rgba(37,99,235,0.35)',
};

export const ease = 'cubic-bezier(0.22, 1, 0.36, 1)';

const heading = (weight: number, size: string, mobile: string) => ({
  fontWeight: weight,
  fontSize: size,
  letterSpacing: '-0.01em',
  '@media (max-width:600px)': { fontSize: mobile },
});

const theme = createTheme({
  palette: {
    primary: { main: brand.primary, dark: brand.primaryDark, light: '#60a5fa' },
    secondary: { main: brand.accent },
    success: { main: '#16a34a' },
    warning: { main: '#f59e0b' },
    error: { main: '#dc2626' },
    info: { main: '#0ea5e9' },
    background: { default: '#f4f6fb', paper: '#ffffff' },
    text: { primary: brand.ink, secondary: '#64748b' },
    divider: 'rgba(15,23,42,0.08)',
  },
  shape: { borderRadius: 12 },
  typography: {
    fontFamily: '"Plus Jakarta Sans", "Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: heading(800, '2.5rem', '2rem'),
    h2: heading(800, '2rem', '1.75rem'),
    h3: heading(700, '1.75rem', '1.5rem'),
    h4: heading(700, '1.5rem', '1.25rem'),
    h5: heading(700, '1.25rem', '1.125rem'),
    h6: heading(600, '1.125rem', '1rem'),
    button: { fontWeight: 600 },
  },
  breakpoints: { values: { xs: 0, sm: 600, md: 900, lg: 1200, xl: 1536 } },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: { background: brand.pageBackground, backgroundAttachment: 'fixed' },
      },
    },
    MuiContainer: {
      styleOverrides: {
        root: {
          paddingLeft: '8px',
          paddingRight: '8px',
          '@media (min-width: 600px)': { paddingLeft: '16px', paddingRight: '16px' },
          '@media (min-width: 900px)': { paddingLeft: '24px', paddingRight: '24px' },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: { backgroundImage: 'none' },
        rounded: { borderRadius: 16 },
        elevation1: { boxShadow: brand.shadowSoft },
        elevation2: { boxShadow: brand.shadowSoft },
        elevation3: { boxShadow: brand.shadowSoft },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          border: '1px solid rgba(15,23,42,0.06)',
          boxShadow: brand.shadowSoft,
          transition: `transform 0.35s ${ease}, box-shadow 0.35s ${ease}, border-color 0.35s ${ease}`,
          '&:hover': {
            transform: 'translateY(-3px)',
            boxShadow: brand.shadowLift,
            borderColor: alpha(brand.primary, 0.25),
          },
          '@media (max-width:600px)': { borderRadius: 12, margin: '8px 0' },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 10,
          transition: `transform 0.25s ${ease}, box-shadow 0.25s ${ease}, background 0.25s ${ease}`,
          '&:active': { transform: 'scale(0.97)' },
          '@media (max-width:600px)': { fontSize: '0.875rem', padding: '8px 16px' },
        },
        containedPrimary: {
          position: 'relative',
          overflow: 'hidden',
          background: brand.gradient,
          boxShadow: '0 4px 14px rgba(37,99,235,0.30)',
          // A band of light sweeps across on hover
          '&::after': {
            content: '""',
            position: 'absolute',
            inset: 0,
            background: 'linear-gradient(110deg, transparent 30%, rgba(255,255,255,0.35) 50%, transparent 70%)',
            transform: 'translateX(-120%)',
            transition: `transform 0.7s ${ease}`,
            pointerEvents: 'none',
          },
          '&:hover': { background: brand.gradient, boxShadow: brand.shadowGlow, transform: 'translateY(-1px)' },
          '&:hover::after': { transform: 'translateX(120%)' },
          '&.Mui-disabled': { background: 'rgba(15,23,42,0.12)', boxShadow: 'none' },
        },
        outlined: {
          borderColor: alpha(brand.primary, 0.35),
          '&:hover': { backgroundColor: alpha(brand.primary, 0.06), transform: 'translateY(-1px)' },
        },
      },
    },
    MuiIconButton: {
      styleOverrides: {
        root: {
          transition: `transform 0.25s ${ease}, background-color 0.25s ${ease}`,
          '&:hover': { transform: 'scale(1.08)' },
        },
      },
    },
    MuiChip: { styleOverrides: { root: { fontWeight: 600, borderRadius: 8 } } },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          backgroundColor: '#fff',
          transition: `box-shadow 0.25s ${ease}`,
          '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: alpha(brand.primary, 0.5) },
          '&.Mui-focused': { boxShadow: `0 0 0 4px ${alpha(brand.primary, 0.14)}` },
        },
      },
    },
    MuiTableHead: {
      styleOverrides: {
        root: {
          '& .MuiTableCell-head': {
            fontWeight: 700,
            fontSize: '0.75rem',
            letterSpacing: '0.04em',
            textTransform: 'uppercase',
            color: '#475569',
            backgroundColor: '#f1f5fd',
            borderBottom: '1px solid rgba(15,23,42,0.08)',
            whiteSpace: 'nowrap',
          },
        },
      },
    },
    MuiTableRow: {
      styleOverrides: {
        root: {
          transition: 'background-color 0.2s ease',
          '&.MuiTableRow-hover:hover': { backgroundColor: alpha(brand.primary, 0.045) },
        },
      },
    },
    MuiTableCell: { styleOverrides: { root: { borderBottomColor: 'rgba(15,23,42,0.06)' } } },
    MuiTable: { styleOverrides: { root: { '@media (max-width:600px)': { fontSize: '0.75rem' } } } },
    MuiTabs: {
      styleOverrides: { indicator: { height: 3, borderRadius: 3, background: brand.gradient } },
    },
    MuiTab: {
      styleOverrides: {
        root: { textTransform: 'none', fontWeight: 600, minHeight: 48, transition: 'color 0.2s ease' },
      },
    },
    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          backgroundColor: 'rgba(15,23,42,0.92)',
          backdropFilter: 'blur(6px)',
          borderRadius: 8,
          fontSize: '0.75rem',
          padding: '6px 10px',
        },
        arrow: { color: 'rgba(15,23,42,0.92)' },
      },
    },
    MuiMenu: {
      styleOverrides: {
        paper: {
          borderRadius: 14,
          border: '1px solid rgba(15,23,42,0.06)',
          boxShadow: '0 20px 50px rgba(15,23,42,0.18)',
        },
      },
    },
    MuiBackdrop: {
      styleOverrides: {
        root: {
          '&:not(.MuiBackdrop-invisible)': { backgroundColor: 'rgba(11,20,55,0.45)', backdropFilter: 'blur(4px)' },
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          borderRadius: 18,
          boxShadow: '0 30px 80px rgba(11,20,55,0.35)',
          '@media (max-width:600px)': {
            margin: '8px',
            width: 'calc(100% - 16px)',
            maxHeight: 'calc(100% - 16px)',
            borderRadius: '12px',
          },
        },
      },
    },
    MuiDialogTitle: {
      styleOverrides: {
        root: { fontWeight: 700, '@media (max-width:600px)': { fontSize: '1.125rem', padding: '12px 16px' } },
      },
    },
    MuiDialogContent: { styleOverrides: { root: { '@media (max-width:600px)': { padding: '8px 16px' } } } },
    MuiDialogActions: {
      styleOverrides: {
        root: {
          padding: '12px 24px 20px',
          '@media (max-width:600px)': {
            padding: '8px 16px 16px',
            gap: '8px',
            '& .MuiButton-root': { fontSize: '0.875rem', padding: '6px 12px' },
          },
        },
      },
    },
    MuiLinearProgress: {
      styleOverrides: { root: { borderRadius: 6, height: 6 }, bar: { borderRadius: 6 } },
    },
    MuiAlert: { styleOverrides: { root: { borderRadius: 12 } } },
  },
});

export default theme;
