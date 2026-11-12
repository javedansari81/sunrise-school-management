/**
 * Small building blocks shared by the fee, transport and platform screens:
 * hero banner, stat cards, panels, pill tabs, status chips, notifications.
 */
import React, { useCallback, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Paper,
  Snackbar,
  Tab,
  Tabs,
  TextField,
  Typography,
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import { Close as CloseIcon, Inbox as InboxIcon } from '@mui/icons-material';
import { brand, ease } from '../../theme';

// ---------------------------------------------------------------------------
// Formatting
// ---------------------------------------------------------------------------

/** Amounts arrive as exact strings ("1500.00"); show them as rupees. */
export const money = (value: string | number | null | undefined, currency = 'INR'): string => {
  const amount = Number(value ?? 0);
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency,
    minimumFractionDigits: Number.isInteger(amount) ? 0 : 2,
    maximumFractionDigits: 2,
  }).format(amount);
};

export const formatDate = (value?: string | null): string => {
  if (!value) return '—';
  const date = new Date(value.length === 10 ? `${value}T00:00:00` : value);
  return Number.isNaN(date.getTime())
    ? value
    : date.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
};

export const formatMonth = (value?: string | null): string => {
  if (!value) return '—';
  const date = new Date(`${value.slice(0, 10)}T00:00:00`);
  return date.toLocaleDateString('en-IN', { month: 'short', year: 'numeric' });
};

export const todayISO = (): string => {
  const now = new Date();
  const local = new Date(now.getTime() - now.getTimezoneOffset() * 60000);
  return local.toISOString().slice(0, 10);
};

/** The message of a failed API call, including FastAPI validation errors. */
export const apiError = (error: any, fallback = 'Something went wrong. Please try again.'): string => {
  const detail = error?.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail) && detail.length) {
    return detail
      .map((item: any) => {
        const field = Array.isArray(item.loc) ? item.loc.filter((part: any) => part !== 'body').join('.') : '';
        return field ? `${field}: ${item.msg}` : item.msg;
      })
      .join('; ');
  }
  if (error?.message === 'Network Error') return 'Cannot reach the server. Check your connection.';
  return error?.message || fallback;
};

// ---------------------------------------------------------------------------
// Hero banner
// ---------------------------------------------------------------------------

interface PageHeroProps {
  title: string;
  subtitle?: string;
  icon?: React.ReactNode;
  actions?: React.ReactNode;
  children?: React.ReactNode;
}

export const PageHero: React.FC<PageHeroProps> = ({ title, subtitle, icon, actions, children }) => (
  <Box
    sx={{
      position: 'relative',
      overflow: 'hidden',
      mb: 3,
      p: { xs: 2.5, sm: 3.5 },
      borderRadius: '24px',
      color: '#fff',
      background: brand.gradientHero,
      boxShadow: '0 24px 60px rgba(29,78,216,0.28)',
      // Drifting lights and a fine grid
      '&::before, &::after': {
        content: '""',
        position: 'absolute',
        borderRadius: '50%',
        filter: 'blur(50px)',
        pointerEvents: 'none',
        animation: 'floatSlow 10s ease-in-out infinite',
      },
      '&::before': { width: 260, height: 260, top: -120, right: -40, background: 'rgba(244,114,182,0.45)' },
      '&::after': { width: 220, height: 220, bottom: -130, left: '30%', background: 'rgba(56,189,248,0.40)', animationDelay: '-5s' },
    }}
  >
    <Box
      aria-hidden
      sx={{
        position: 'absolute',
        inset: 0,
        opacity: 0.18,
        backgroundImage:
          'linear-gradient(rgba(255,255,255,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.5) 1px, transparent 1px)',
        backgroundSize: '36px 36px',
        maskImage: 'linear-gradient(90deg, transparent, #000 60%)',
        WebkitMaskImage: 'linear-gradient(90deg, transparent, #000 60%)',
      }}
    />
    <Box sx={{ position: 'relative', display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
      {icon && (
        <Box
          sx={{
            display: 'grid',
            placeItems: 'center',
            width: 56,
            height: 56,
            borderRadius: '18px',
            background: 'rgba(255,255,255,0.16)',
            border: '1px solid rgba(255,255,255,0.28)',
            backdropFilter: 'blur(8px)',
            '& svg': { fontSize: 30 },
          }}
        >
          {icon}
        </Box>
      )}
      <Box sx={{ flexGrow: 1, minWidth: 220 }}>
        <Typography sx={{ fontSize: { xs: '1.35rem', sm: '1.7rem' }, fontWeight: 800, letterSpacing: '-0.02em', lineHeight: 1.2 }}>
          {title}
        </Typography>
        {subtitle && <Typography sx={{ mt: 0.5, opacity: 0.85, fontSize: '0.92rem', maxWidth: 720 }}>{subtitle}</Typography>}
      </Box>
      {actions && <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>{actions}</Box>}
    </Box>
    {children && <Box sx={{ position: 'relative', mt: 2.5 }}>{children}</Box>}
  </Box>
);

/** Button for use on the dark hero banner. */
export const heroButtonSx = {
  color: '#fff',
  background: 'rgba(255,255,255,0.16)',
  border: '1px solid rgba(255,255,255,0.32)',
  backdropFilter: 'blur(8px)',
  boxShadow: 'none',
  '&:hover': { background: 'rgba(255,255,255,0.28)', boxShadow: '0 10px 24px rgba(11,20,55,0.3)' },
};

// ---------------------------------------------------------------------------
// Stat card
// ---------------------------------------------------------------------------

type Tone = 'blue' | 'green' | 'orange' | 'red' | 'violet' | 'slate';

const tones: Record<Tone, { main: string; gradient: string }> = {
  blue: { main: '#2563eb', gradient: 'linear-gradient(135deg, #3b82f6, #2563eb)' },
  green: { main: '#16a34a', gradient: 'linear-gradient(135deg, #34d399, #059669)' },
  orange: { main: '#ea580c', gradient: 'linear-gradient(135deg, #fbbf24, #f97316)' },
  red: { main: '#dc2626', gradient: 'linear-gradient(135deg, #fb7185, #dc2626)' },
  violet: { main: '#7c3aed', gradient: 'linear-gradient(135deg, #a78bfa, #7c3aed)' },
  slate: { main: '#475569', gradient: 'linear-gradient(135deg, #94a3b8, #475569)' },
};

interface StatCardProps {
  label: string;
  value: React.ReactNode;
  hint?: React.ReactNode;
  icon?: React.ReactNode;
  tone?: Tone;
  delay?: number;
}

export const StatCard: React.FC<StatCardProps> = ({ label, value, hint, icon, tone = 'blue', delay = 0 }) => {
  const color = tones[tone];
  return (
    <Box
      sx={{
        position: 'relative',
        overflow: 'hidden',
        p: 2.25,
        borderRadius: '18px',
        background: 'rgba(255,255,255,0.86)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(15,23,42,0.06)',
        boxShadow: brand.shadowSoft,
        animation: `fadeUp 0.5s ${ease} both`,
        animationDelay: `${delay}ms`,
        transition: `transform 0.35s ${ease}, box-shadow 0.35s ${ease}`,
        // Coloured glow in the corner that grows on hover
        '&::after': {
          content: '""',
          position: 'absolute',
          width: 120,
          height: 120,
          right: -40,
          top: -40,
          borderRadius: '50%',
          background: color.gradient,
          opacity: 0.14,
          transition: `transform 0.5s ${ease}, opacity 0.5s ${ease}`,
        },
        '&:hover': { transform: 'translateY(-4px)', boxShadow: `0 18px 40px ${alpha(color.main, 0.22)}` },
        '&:hover::after': { transform: 'scale(1.6)', opacity: 0.2 },
      }}
    >
      <Box sx={{ position: 'relative', zIndex: 1, display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 1 }}>
        <Box sx={{ minWidth: 0 }}>
          <Typography sx={{ fontSize: '0.74rem', fontWeight: 700, letterSpacing: '0.06em', textTransform: 'uppercase', color: 'text.secondary' }}>
            {label}
          </Typography>
          <Typography sx={{ mt: 0.5, fontSize: { xs: '1.3rem', sm: '1.55rem' }, fontWeight: 800, letterSpacing: '-0.02em', lineHeight: 1.2, color: brand.ink }}>
            {value}
          </Typography>
          {hint && <Typography sx={{ mt: 0.5, fontSize: '0.78rem', color: 'text.secondary' }}>{hint}</Typography>}
        </Box>
        {icon && (
          <Box
            sx={{
              display: 'grid',
              placeItems: 'center',
              flexShrink: 0,
              width: 44,
              height: 44,
              borderRadius: '14px',
              color: '#fff',
              background: color.gradient,
              boxShadow: `0 8px 18px ${alpha(color.main, 0.4)}`,
              '& svg': { fontSize: 22 },
            }}
          >
            {icon}
          </Box>
        )}
      </Box>
    </Box>
  );
};

export const StatGrid: React.FC<{ children: React.ReactNode; min?: number }> = ({ children, min = 210 }) => (
  <Box sx={{ display: 'grid', gap: 2, mb: 3, gridTemplateColumns: `repeat(auto-fit, minmax(${min}px, 1fr))` }}>{children}</Box>
);

// ---------------------------------------------------------------------------
// Panel
// ---------------------------------------------------------------------------

interface PanelProps {
  title?: React.ReactNode;
  subtitle?: React.ReactNode;
  actions?: React.ReactNode;
  children: React.ReactNode;
  padded?: boolean;
  sx?: object;
}

export const Panel: React.FC<PanelProps> = ({ title, subtitle, actions, children, padded = true, sx }) => (
  <Paper
    elevation={0}
    sx={{
      borderRadius: '20px',
      border: '1px solid rgba(15,23,42,0.06)',
      background: 'rgba(255,255,255,0.9)',
      backdropFilter: 'blur(12px)',
      boxShadow: brand.shadowSoft,
      overflow: 'hidden',
      animation: `fadeUp 0.5s ${ease} both`,
      ...sx,
    }}
  >
    {(title || actions) && (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, flexWrap: 'wrap', px: 2.5, py: 2, borderBottom: '1px solid rgba(15,23,42,0.06)' }}>
        <Box sx={{ flexGrow: 1, minWidth: 0 }}>
          <Typography sx={{ fontWeight: 700, fontSize: '1.02rem' }}>{title}</Typography>
          {subtitle && (
            <Typography variant="body2" color="text.secondary">
              {subtitle}
            </Typography>
          )}
        </Box>
        {actions && <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', alignItems: 'center' }}>{actions}</Box>}
      </Box>
    )}
    <Box sx={padded ? { p: 2.5 } : undefined}>{children}</Box>
  </Paper>
);

// ---------------------------------------------------------------------------
// Pill tabs
// ---------------------------------------------------------------------------

interface PillTabsProps {
  value: string;
  onChange: (value: string) => void;
  tabs: { value: string; label: string; icon?: React.ReactElement }[];
}

export const PillTabs: React.FC<PillTabsProps> = ({ value, onChange, tabs }) => (
  <Tabs
    value={value}
    onChange={(_, next) => onChange(next)}
    variant="scrollable"
    scrollButtons="auto"
    allowScrollButtonsMobile
    sx={{
      mb: 3,
      p: 0.75,
      minHeight: 0,
      borderRadius: '16px',
      background: 'rgba(255,255,255,0.75)',
      backdropFilter: 'blur(12px)',
      border: '1px solid rgba(15,23,42,0.06)',
      boxShadow: brand.shadowSoft,
      '& .MuiTabs-indicator': {
        height: '100%',
        borderRadius: '12px',
        background: brand.gradient,
        boxShadow: '0 8px 20px rgba(37,99,235,0.35)',
        transition: `all 0.45s ${ease}`,
      },
      '& .MuiTab-root': {
        zIndex: 1,
        minHeight: 42,
        px: 2,
        borderRadius: '12px',
        color: 'text.secondary',
        '&.Mui-selected': { color: '#fff' },
        '&:not(.Mui-selected):hover': { color: 'primary.main', background: alpha(brand.primary, 0.06) },
      },
    }}
  >
    {tabs.map((tab) => (
      <Tab key={tab.value} value={tab.value} label={tab.label} icon={tab.icon} iconPosition="start" />
    ))}
  </Tabs>
);

// ---------------------------------------------------------------------------
// Status chip, empty and loading states
// ---------------------------------------------------------------------------

const statusTone: Record<string, Tone> = {
  PAID: 'green', ACTIVE: 'green', PUBLISHED: 'green', PAYMENT: 'green', RIDING: 'green',
  PARTIAL: 'orange', DRAFT: 'orange', PAUSED: 'orange',
  PENDING: 'blue', DUE: 'blue',
  OVERDUE: 'red', SUSPENDED: 'red', REVERSAL: 'red', CANCELLED: 'slate',
  ARCHIVED: 'slate', WAIVED: 'violet', INACTIVE: 'slate', ENDED: 'slate',
};

export const StatusChip: React.FC<{ status: string; label?: string }> = ({ status, label }) => {
  const color = tones[statusTone[status?.toUpperCase()] || 'slate'].main;
  return (
    <Chip
      size="small"
      label={label || status.charAt(0) + status.slice(1).toLowerCase().replace(/_/g, ' ')}
      sx={{
        height: 24,
        color,
        background: alpha(color, 0.1),
        border: `1px solid ${alpha(color, 0.25)}`,
        '&::before': {
          content: '""',
          width: 6,
          height: 6,
          ml: 1,
          borderRadius: '50%',
          background: color,
          boxShadow: `0 0 8px ${color}`,
        },
      }}
    />
  );
};

export const EmptyState: React.FC<{ title: string; hint?: string; action?: React.ReactNode; icon?: React.ReactNode }> = ({
  title,
  hint,
  action,
  icon,
}) => (
  <Box sx={{ py: 6, px: 2, textAlign: 'center', color: 'text.secondary' }}>
    <Box
      sx={{
        display: 'inline-grid',
        placeItems: 'center',
        width: 68,
        height: 68,
        mb: 1.5,
        borderRadius: '22px',
        color: 'primary.main',
        background: alpha(brand.primary, 0.08),
        animation: 'floatSlow 5s ease-in-out infinite',
        '& svg': { fontSize: 32 },
      }}
    >
      {icon || <InboxIcon />}
    </Box>
    <Typography sx={{ fontWeight: 700, color: 'text.primary' }}>{title}</Typography>
    {hint && (
      <Typography variant="body2" sx={{ mt: 0.5, maxWidth: 460, mx: 'auto' }}>
        {hint}
      </Typography>
    )}
    {action && <Box sx={{ mt: 2 }}>{action}</Box>}
  </Box>
);

export const Loading: React.FC<{ label?: string }> = ({ label = 'Loading…' }) => (
  <Box sx={{ py: 6, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 1.5, color: 'text.secondary' }}>
    <CircularProgress size={30} thickness={5} />
    <Typography variant="body2">{label}</Typography>
  </Box>
);

// ---------------------------------------------------------------------------
// Dialog shell with a gradient title
// ---------------------------------------------------------------------------

interface FormDialogProps {
  open: boolean;
  title: string;
  subtitle?: string;
  onClose: () => void;
  onSubmit?: () => void;
  submitLabel?: string;
  submitColor?: 'primary' | 'error' | 'success' | 'warning';
  busy?: boolean;
  disabled?: boolean;
  error?: string | null;
  maxWidth?: 'xs' | 'sm' | 'md' | 'lg';
  children: React.ReactNode;
}

export const FormDialog: React.FC<FormDialogProps> = ({
  open,
  title,
  subtitle,
  onClose,
  onSubmit,
  submitLabel = 'Save',
  submitColor = 'primary',
  busy = false,
  disabled = false,
  error,
  maxWidth = 'sm',
  children,
}) => (
  <Dialog open={open} onClose={busy ? undefined : onClose} maxWidth={maxWidth} fullWidth>
    <Box
      component="form"
      onSubmit={(event: React.FormEvent) => {
        event.preventDefault();
        if (!busy && !disabled) onSubmit?.();
      }}
      sx={{ display: 'flex', flexDirection: 'column', minHeight: 0, overflow: 'hidden' }}
    >
      <DialogTitle sx={{ position: 'relative', overflow: 'hidden', color: '#fff', background: brand.gradientHero, pr: 7 }}>
        {title}
        {subtitle && <Typography sx={{ fontSize: '0.85rem', opacity: 0.85, fontWeight: 400 }}>{subtitle}</Typography>}
        <IconButton onClick={onClose} disabled={busy} aria-label="Close" sx={{ position: 'absolute', right: 12, top: 12, color: '#fff' }}>
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      <DialogContent sx={{ pt: '20px !important', display: 'flex', flexDirection: 'column', gap: 2 }}>
        {error && <Alert severity="error">{error}</Alert>}
        {children}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={busy} color="inherit">
          {onSubmit ? 'Cancel' : 'Close'}
        </Button>
        {onSubmit && (
          <Button
            type="submit"
            variant="contained"
            color={submitColor}
            disabled={busy || disabled}
            startIcon={busy ? <CircularProgress size={16} color="inherit" /> : undefined}
          >
            {submitLabel}
          </Button>
        )}
      </DialogActions>
    </Box>
  </Dialog>
);

/** Two form fields side by side (one column on phones). */
export const FieldRow: React.FC<{ children: React.ReactNode; columns?: number }> = ({ children, columns = 2 }) => (
  <Box sx={{ display: 'grid', gap: 2, gridTemplateColumns: { xs: '1fr', sm: `repeat(${columns}, 1fr)` } }}>{children}</Box>
);

// ---------------------------------------------------------------------------
// Confirm with an optional reason
// ---------------------------------------------------------------------------

export interface ConfirmRequest {
  title: string;
  message: string;
  confirmLabel?: string;
  danger?: boolean;
  /** Ask for a reason; `required` blocks confirming without one. */
  reason?: { label: string; required?: boolean };
  onConfirm: (reason: string) => Promise<void>;
}

export const ConfirmDialog: React.FC<{ request: ConfirmRequest | null; onClose: () => void }> = ({ request, onClose }) => {
  const [reason, setReason] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const close = () => {
    setReason('');
    setError(null);
    onClose();
  };

  const submit = async () => {
    if (!request) return;
    setBusy(true);
    setError(null);
    try {
      await request.onConfirm(reason.trim());
      close();
    } catch (failure) {
      setError(apiError(failure));
    } finally {
      setBusy(false);
    }
  };

  return (
    <FormDialog
      open={Boolean(request)}
      title={request?.title || ''}
      onClose={close}
      onSubmit={submit}
      submitLabel={request?.confirmLabel || 'Confirm'}
      submitColor={request?.danger ? 'error' : 'primary'}
      busy={busy}
      disabled={Boolean(request?.reason?.required) && !reason.trim()}
      error={error}
      maxWidth="xs"
    >
      <Typography>{request?.message}</Typography>
      {request?.reason && (
        <TextField
          label={request.reason.label}
          value={reason}
          onChange={(event) => setReason(event.target.value)}
          required={request.reason.required}
          multiline
          minRows={2}
          autoFocus
        />
      )}
    </FormDialog>
  );
};

// ---------------------------------------------------------------------------
// Notifications
// ---------------------------------------------------------------------------

type Severity = 'success' | 'error' | 'info' | 'warning';

export const useNotify = () => {
  const [state, setState] = useState<{ message: string; severity: Severity } | null>(null);
  const notify = useCallback((message: string, severity: Severity = 'success') => setState({ message, severity }), []);
  const notifyError = useCallback((error: any) => setState({ message: apiError(error), severity: 'error' }), []);
  const node = (
    <Snackbar
      open={Boolean(state)}
      autoHideDuration={state?.severity === 'error' ? 8000 : 4000}
      onClose={(_, reason) => reason !== 'clickaway' && setState(null)}
      anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
    >
      {state ? (
        <Alert severity={state.severity} variant="filled" onClose={() => setState(null)} sx={{ boxShadow: '0 16px 40px rgba(15,23,42,0.25)' }}>
          {state.message}
        </Alert>
      ) : undefined}
    </Snackbar>
  );
  return { notify, notifyError, node };
};
