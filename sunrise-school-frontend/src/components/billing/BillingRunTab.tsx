/**
 * Billing run: the three steps that turn a published fee structure into dues.
 * Each is safe to run again; it only adds or corrects what is missing.
 */
import React, { useEffect, useState } from 'react';
import { Alert, Box, Button, CircularProgress, MenuItem, TextField, Typography } from '@mui/material';
import { alpha } from '@mui/material/styles';
import { AccountTree as PlanIcon, Autorenew as GenerateIcon, Gavel as LateIcon } from '@mui/icons-material';
import { billingAPI } from '../../services/billingService';
import { Lookups } from '../../hooks/useLookups';
import { apiError, formatDate, formatMonth, money, Panel, todayISO } from '../ui';
import { brand, ease } from '../../theme';

interface Props {
  lookups: Lookups;
}

interface StepProps {
  step: number;
  icon: React.ReactNode;
  color: string;
  title: string;
  description: string;
  action: string;
  busy: boolean;
  disabled?: boolean;
  onRun: () => void;
  error: string | null;
  result: React.ReactNode;
  children: React.ReactNode;
}

const Step: React.FC<StepProps> = ({ step, icon, color, title, description, action, busy, disabled, onRun, error, result, children }) => (
  <Box
    sx={{
      position: 'relative',
      display: 'flex',
      flexDirection: 'column',
      gap: 2,
      p: 2.5,
      borderRadius: '20px',
      background: '#fff',
      border: '1px solid rgba(15,23,42,0.07)',
      boxShadow: brand.shadowSoft,
      overflow: 'hidden',
      animation: `fadeUp 0.5s ${ease} both`,
      animationDelay: `${(step - 1) * 90}ms`,
      transition: `transform 0.35s ${ease}, box-shadow 0.35s ${ease}`,
      '&:hover': { transform: 'translateY(-4px)', boxShadow: `0 20px 44px ${alpha(color, 0.2)}` },
      '&::before': { content: '""', position: 'absolute', left: 0, right: 0, top: 0, height: 4, background: `linear-gradient(90deg, ${color}, ${alpha(color, 0.3)})` },
    }}
  >
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
      <Box sx={{ display: 'grid', placeItems: 'center', width: 46, height: 46, borderRadius: '14px', color: '#fff', background: color, boxShadow: `0 10px 22px ${alpha(color, 0.4)}` }}>
        {icon}
      </Box>
      <Box>
        <Typography sx={{ fontSize: '0.7rem', fontWeight: 700, letterSpacing: '0.12em', color }}>STEP {step}</Typography>
        <Typography sx={{ fontWeight: 800, fontSize: '1.05rem', lineHeight: 1.2 }}>{title}</Typography>
      </Box>
    </Box>
    <Typography variant="body2" color="text.secondary">
      {description}
    </Typography>
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>{children}</Box>
    {error && <Alert severity="error">{error}</Alert>}
    {result && (
      <Alert severity="success" sx={{ animation: `fadeUp 0.4s ${ease} both` }}>
        {result}
      </Alert>
    )}
    <Box sx={{ flexGrow: 1 }} />
    <Button variant="contained" onClick={onRun} disabled={busy || disabled} startIcon={busy ? <CircularProgress size={16} color="inherit" /> : undefined}>
      {busy ? 'Working…' : action}
    </Button>
  </Box>
);

const useRun = () => {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  const run = async (call: () => Promise<any>) => {
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      setResult(await call());
    } catch (failure) {
      setError(apiError(failure));
    } finally {
      setBusy(false);
    }
  };
  return { busy, error, result, run };
};

const BillingRunTab: React.FC<Props> = ({ lookups }) => {
  const [sessionId, setSessionId] = useState<number | ''>(lookups.currentSessionId ?? '');
  const [classId, setClassId] = useState<number | ''>('');
  const [effectiveFrom, setEffectiveFrom] = useState('');
  const [through, setThrough] = useState(todayISO().slice(0, 7));
  const [asOf, setAsOf] = useState(todayISO());

  const plans = useRun();
  const dues = useRun();
  const late = useRun();

  useEffect(() => {
    if (sessionId === '' && lookups.currentSessionId != null) setSessionId(lookups.currentSessionId);
  }, [lookups.currentSessionId, sessionId]);

  const scope = classId === '' ? 'the whole school' : lookups.className(classId);

  return (
    <>
      <Panel sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
          <Typography sx={{ flexGrow: 1, minWidth: 220 }} color="text.secondary" variant="body2">
            Run these for <strong>{scope}</strong> in session <strong>{lookups.sessionName(sessionId || null) || '—'}</strong>. Running a step
            again never bills anyone twice.
          </Typography>
          <TextField select size="small" label="Session" value={sessionId} onChange={(event) => setSessionId(Number(event.target.value))} sx={{ minWidth: 140 }}>
            {lookups.sessionYears.map((year) => (
              <MenuItem key={year.id} value={year.id}>
                {year.name}
              </MenuItem>
            ))}
          </TextField>
          <TextField select size="small" label="Class" value={classId} onChange={(event) => setClassId(event.target.value === '' ? '' : Number(event.target.value))} sx={{ minWidth: 170 }} slotProps={{ select: { displayEmpty: true }, inputLabel: { shrink: true } }}>
            <MenuItem value="">Whole school</MenuItem>
            {lookups.classes.map((item) => (
              <MenuItem key={item.id} value={item.id}>
                {item.description || item.name}
              </MenuItem>
            ))}
          </TextField>
        </Box>
      </Panel>

      <Box sx={{ display: 'grid', gap: 2.5, gridTemplateColumns: 'repeat(auto-fit, minmax(290px, 1fr))' }}>
        <Step
          step={1}
          icon={<PlanIcon />}
          color="#2563eb"
          title="Build fee plans"
          description="Gives each enrolled student the charges of the published fee structure for their class. Run it after publishing a structure and when new students join."
          action="Build plans"
          busy={plans.busy}
          disabled={sessionId === ''}
          error={plans.error}
          onRun={() => plans.run(() => billingAPI.buildPlans({ session_year_id: Number(sessionId), class_id: classId === '' ? null : classId, effective_from: effectiveFrom ? `${effectiveFrom}-01` : null }))}
          result={
            plans.result && (
              <>
                {plans.result.students} students checked: {plans.result.created} charges added, {plans.result.replaced} changed, {plans.result.ended} ended,{' '}
                {plans.result.unchanged} already right.
                {plans.result.dues_cancelled > 0 && ` ${plans.result.dues_cancelled} unpaid dues were cancelled to be billed again at the new price.`}
              </>
            )
          }
        >
          <TextField
            label="Price changes start from"
            type="month"
            size="small"
            value={effectiveFrom}
            onChange={(event) => setEffectiveFrom(event.target.value)}
            helperText="Leave empty: new students get the whole session, changes start this month"
            slotProps={{ inputLabel: { shrink: true } }}
          />
        </Step>

        <Step
          step={2}
          icon={<GenerateIcon />}
          color="#7c3aed"
          title="Generate dues"
          description="Creates what each student owes, month by month, up to the month you pick. It also applies concessions, late fees and any advance credit."
          action="Generate dues"
          busy={dues.busy}
          disabled={sessionId === '' || !through}
          error={dues.error}
          onRun={() => dues.run(() => billingAPI.generateDues({ session_year_id: Number(sessionId), class_id: classId === '' ? null : classId, through_period: `${through}-01` }))}
          result={
            dues.result && (
              <>
                Up to {formatMonth(dues.result.through_period)}: {dues.result.created} dues created ({money(dues.result.total_amount)}) for {dues.result.students} students
                {dues.result.repriced > 0 && `, ${dues.result.repriced} re-priced`}
                {dues.result.late_fees > 0 && `, ${dues.result.late_fees} late fees`}
                {Number(dues.result.credit_applied) > 0 && `, ${money(dues.result.credit_applied)} of credit used`}.
              </>
            )
          }
        >
          <TextField label="Bill up to and including" type="month" size="small" value={through} onChange={(event) => setThrough(event.target.value)} slotProps={{ inputLabel: { shrink: true } }} />
        </Step>

        <Step
          step={3}
          icon={<LateIcon />}
          color="#ea580c"
          title="Apply late fees"
          description="Adds a late fee to months that are still unpaid after the grace period, using the school's late fee settings. Always runs for the whole school."
          action="Apply late fees"
          busy={late.busy}
          disabled={!asOf}
          error={late.error}
          onRun={() => late.run(() => billingAPI.applyLateFees({ as_of: asOf, session_year_id: sessionId === '' ? null : sessionId }))}
          result={
            late.result &&
            (late.result.enabled
              ? `As of ${formatDate(late.result.as_of)}: ${late.result.created} late fees added (${money(late.result.total_amount)}).`
              : 'Late fees are switched off for this school, so nothing was added.')
          }
        >
          <TextField label="Overdue as of" type="date" size="small" value={asOf} onChange={(event) => setAsOf(event.target.value)} slotProps={{ inputLabel: { shrink: true } }} />
        </Step>
      </Box>
    </>
  );
};

export default BillingRunTab;
