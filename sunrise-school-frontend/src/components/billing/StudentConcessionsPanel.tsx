/** A student's concessions for a session: what they get, give one, take one back. */
import React, { useCallback, useEffect, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  IconButton,
  InputAdornment,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import { Add as AddIcon, FamilyRestroom as SiblingIcon, LocalOffer as OfferIcon, RemoveCircle as RevokeIcon } from '@mui/icons-material';
import {
  billingAPI,
  CONCESSION_TYPES,
  ConcessionRule,
  concessionTypeLabel,
  FeeHead,
  SiblingPreview,
  StudentConcession,
} from '../../services/billingService';
import { apiError, ConfirmDialog, ConfirmRequest, EmptyState, FieldRow, FormDialog, formatMonth, Loading, StatusChip, useNotify } from '../ui';
import { concessionValue, headsLabel } from './ConcessionsTab';
import SiblingsManager from '../common/SiblingsManager';

interface Props {
  studentId: number;
  sessionYearId: number;
  heads: FeeHead[];
  /** Dues were re-priced: reload the student's figures. */
  onChanged: () => void;
}

const CUSTOM = 'custom';
const blank = { rule: CUSTOM as number | typeof CUSTOM, concession_type: 'SCHOLARSHIP', value_type: 'PERCENT', value: '', fee_head_ids: [] as number[], start: '', end: '', reason: '' };

const StudentConcessionsPanel: React.FC<Props> = ({ studentId, sessionYearId, heads, onChanged }) => {
  const { notify, node } = useNotify();
  const [concessions, setConcessions] = useState<StudentConcession[]>([]);
  const [sibling, setSibling] = useState<SiblingPreview | null>(null);
  const [rules, setRules] = useState<ConcessionRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [form, setForm] = useState<typeof blank | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confirm, setConfirm] = useState<ConfirmRequest | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [nextConcessions, nextSibling, nextRules] = await Promise.all([
        billingAPI.studentConcessions(studentId, sessionYearId),
        billingAPI.siblingPreview(studentId, sessionYearId),
        billingAPI.listRules(),
      ]);
      setConcessions(nextConcessions);
      setSibling(nextSibling);
      setRules(nextRules.filter((rule) => rule.is_active && rule.concession_type !== 'SIBLING'));
      setLoadError(null);
    } catch (failure) {
      setLoadError(apiError(failure));
    } finally {
      setLoading(false);
    }
  }, [studentId, sessionYearId]);

  useEffect(() => {
    load();
  }, [load]);

  /** A concession reaches unpaid dues when dues are generated, so do that straight away. */
  const reprice = async (studentIds: number[] = [studentId]) => {
    for (const id of Array.from(new Set(studentIds))) {
      await billingAPI.generateDues({ session_year_id: sessionYearId, student_id: id });
    }
    await load();
    onChanged();
  };

  /** Linking or removing a sibling changes the concession of everyone in the family. */
  const familyChanged = async (studentIds: number[]) => {
    try {
      await reprice(studentIds);
      notify('Family updated. Unpaid dues of the whole family now show the sibling concession.');
    } catch (failure) {
      setLoadError(apiError(failure));
    }
  };

  const custom = form?.rule === CUSTOM;
  const billable = heads.filter((head) => head.category !== 'PENALTY');
  const valid =
    form &&
    form.reason.trim() &&
    (!form.start || !form.end || form.end >= form.start) &&
    (!custom || (form.value !== '' && Number(form.value) > 0 && (form.value_type !== 'PERCENT' || Number(form.value) <= 100)));

  const grant = async () => {
    if (!form) return;
    setBusy(true);
    setError(null);
    try {
      await billingAPI.grantConcession(studentId, {
        session_year_id: sessionYearId,
        reason: form.reason.trim(),
        start_period: form.start ? `${form.start}-01` : undefined,
        end_period: form.end ? `${form.end}-01` : undefined,
        ...(custom
          ? {
              concession_type: form.concession_type,
              value_type: form.value_type,
              value: Number(form.value).toFixed(2),
              fee_head_ids: form.fee_head_ids.length ? form.fee_head_ids : undefined,
            }
          : { concession_rule_id: form.rule }),
      });
      await reprice();
      notify('Concession given. Unpaid dues now show it.');
      setForm(null);
    } catch (failure) {
      setError(apiError(failure));
    } finally {
      setBusy(false);
    }
  };

  if (loading && concessions.length === 0 && !sibling) return <Loading />;

  const siblingPercent = Number(sibling?.percent ?? 0);

  return (
    <>
      {loadError && <Alert severity="error" sx={{ m: 2 }}>{loadError}</Alert>}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap', p: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, flexGrow: 1, minWidth: 240 }}>
          <SiblingIcon color={siblingPercent > 0 ? 'secondary' : 'disabled'} />
          <Typography variant="body2" color="text.secondary">
            {!sibling || sibling.family_size < 2
              ? 'No linked siblings enrolled in this session, so no sibling concession. Link them below.'
              : siblingPercent > 0
              ? <>Child {sibling.position_from_eldest} of {sibling.family_size} in the family: <strong>{siblingPercent}% sibling concession</strong> on {headsLabel(sibling.fee_head_ids, heads).toLowerCase()}, applied by itself.</>
              : `Child ${sibling.position_from_eldest} of ${sibling.family_size} in the family. ${sibling.rule_id ? 'The sibling rule gives this child nothing off.' : 'The school has no sibling rule in use.'}`}
          </Typography>
        </Box>
        <Button
          variant="outlined"
          startIcon={<AddIcon />}
          onClick={() => {
            setError(null);
            setForm({ ...blank, rule: rules[0]?.id ?? CUSTOM });
          }}
        >
          Give a concession
        </Button>
      </Box>

      <Box sx={{ px: 2, pb: 2 }}>
        <Box sx={{ p: 2, borderRadius: '16px', border: '1px solid rgba(15,23,42,0.07)', background: 'rgba(124,58,237,0.03)' }}>
          <SiblingsManager studentId={studentId} onChanged={familyChanged} />
        </Box>
      </Box>

      {concessions.length === 0 ? (
        <EmptyState title="No concessions given to this student" hint="Staff-child discounts, scholarships and one-off reductions appear here." icon={<OfferIcon />} />
      ) : (
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Concession</TableCell>
                <TableCell>Off</TableCell>
                <TableCell>On</TableCell>
                <TableCell>Months</TableCell>
                <TableCell>Reason</TableCell>
                <TableCell>Status</TableCell>
                <TableCell />
              </TableRow>
            </TableHead>
            <TableBody>
              {concessions.map((item) => (
                <TableRow key={item.id} hover sx={{ opacity: item.is_active ? 1 : 0.55 }}>
                  <TableCell sx={{ fontWeight: 600 }}>{concessionTypeLabel(item.concession_type)}</TableCell>
                  <TableCell>{concessionValue(item.value_type, item.value)}</TableCell>
                  <TableCell>{headsLabel(item.fee_head_ids, heads)}</TableCell>
                  <TableCell>
                    {item.start_period || item.end_period
                      ? `${item.start_period ? formatMonth(item.start_period) : 'Start'} to ${item.end_period ? formatMonth(item.end_period) : 'end of session'}`
                      : 'Whole session'}
                  </TableCell>
                  <TableCell>{item.reason}</TableCell>
                  <TableCell>
                    <StatusChip status={item.is_active ? 'ACTIVE' : 'CANCELLED'} label={item.is_active ? 'In force' : 'Taken back'} />
                  </TableCell>
                  <TableCell align="right">
                    {item.is_active && (
                      <Tooltip title="Take this concession back">
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() =>
                            setConfirm({
                              title: 'Take back concession',
                              message: `Take back the ${concessionTypeLabel(item.concession_type).toLowerCase()} concession (${concessionValue(item.value_type, item.value)})? Unpaid dues go back to the full amount; paid ones stay as they are.`,
                              confirmLabel: 'Take back',
                              danger: true,
                              reason: { label: 'Reason' },
                              onConfirm: async (reason) => {
                                await billingAPI.revokeConcession(item.id, reason);
                                await reprice();
                                notify('Concession taken back.');
                              },
                            })
                          }
                        >
                          <RevokeIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <FormDialog open={Boolean(form)} title="Give a concession" subtitle="It comes off this student's unpaid dues" onClose={() => setForm(null)} onSubmit={grant} submitLabel="Give concession" busy={busy} disabled={!valid} error={error}>
        {form && (
          <>
            <TextField select label="Concession" value={form.rule} onChange={(event) => setForm({ ...form, rule: event.target.value === CUSTOM ? CUSTOM : Number(event.target.value) })}>
              {rules.map((rule) => (
                <MenuItem key={rule.id} value={rule.id}>
                  {rule.name} · {concessionValue(rule.value_type, rule.value)} · {headsLabel(rule.fee_head_ids, heads)}
                </MenuItem>
              ))}
              <MenuItem value={CUSTOM}>Something else, just for this student</MenuItem>
            </TextField>
            {custom && (
              <>
                <FieldRow columns={3}>
                  <TextField select label="Kind" value={form.concession_type} onChange={(event) => setForm({ ...form, concession_type: event.target.value })}>
                    {CONCESSION_TYPES.filter((type) => type.value !== 'SIBLING').map((type) => (
                      <MenuItem key={type.value} value={type.value}>
                        {type.label}
                      </MenuItem>
                    ))}
                  </TextField>
                  <TextField select label="Taken off as" value={form.value_type} onChange={(event) => setForm({ ...form, value_type: event.target.value })}>
                    <MenuItem value="PERCENT">Percentage</MenuItem>
                    <MenuItem value="FIXED">Fixed amount per due</MenuItem>
                  </TextField>
                  <TextField
                    label={form.value_type === 'PERCENT' ? 'Percent off' : 'Amount off'}
                    type="number"
                    value={form.value}
                    onChange={(event) => setForm({ ...form, value: event.target.value })}
                    required
                    slotProps={{
                      htmlInput: { min: 0.01, step: 0.01, max: form.value_type === 'PERCENT' ? 100 : undefined },
                      input: form.value_type === 'PERCENT' ? { endAdornment: <InputAdornment position="end">%</InputAdornment> } : { startAdornment: <InputAdornment position="start">₹</InputAdornment> },
                    }}
                  />
                </FieldRow>
                <TextField
                  select
                  label="Applies to"
                  value={form.fee_head_ids}
                  onChange={(event) => setForm({ ...form, fee_head_ids: event.target.value as unknown as number[] })}
                  helperText="Leave empty to take it off every fee"
                  slotProps={{
                    inputLabel: { shrink: true },
                    select: { multiple: true, displayEmpty: true, renderValue: (value: unknown) => headsLabel(value as number[], heads) },
                  }}
                >
                  {billable.map((head) => (
                    <MenuItem key={head.id} value={head.id}>
                      {head.name}
                    </MenuItem>
                  ))}
                </TextField>
              </>
            )}
            <FieldRow>
              <TextField label="From month" type="month" value={form.start} onChange={(event) => setForm({ ...form, start: event.target.value })} helperText="Empty: from the start of the session" slotProps={{ inputLabel: { shrink: true } }} />
              <TextField label="Until month" type="month" value={form.end} onChange={(event) => setForm({ ...form, end: event.target.value })} helperText="Empty: to the end of the session" error={Boolean(form.start && form.end && form.end < form.start)} slotProps={{ inputLabel: { shrink: true }, htmlInput: { min: form.start } }} />
            </FieldRow>
            <TextField label="Reason" value={form.reason} onChange={(event) => setForm({ ...form, reason: event.target.value })} required multiline minRows={2} />
          </>
        )}
      </FormDialog>
      <ConfirmDialog request={confirm} onClose={() => setConfirm(null)} />
      {node}
    </>
  );
};

export default StudentConcessionsPanel;
