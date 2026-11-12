/**
 * Concession rules: the discounts a school gives. The sibling rule is applied
 * by itself from linked siblings; the others are granted to a student on the
 * Collect tab.
 */
import React, { useCallback, useEffect, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  FormControlLabel,
  IconButton,
  InputAdornment,
  MenuItem,
  Switch,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import { Add as AddIcon, Delete as DeleteIcon, Edit as EditIcon, FamilyRestroom as SiblingIcon, LocalOffer as OfferIcon } from '@mui/icons-material';
import { billingAPI, CONCESSION_TYPES, ConcessionRule, concessionTypeLabel, FeeHead, SiblingTier } from '../../services/billingService';
import { apiError, EmptyState, FieldRow, FormDialog, Loading, money, Panel, StatusChip, useNotify } from '../ui';
import { brand, ease } from '../../theme';

interface Props {
  heads: FeeHead[];
}

/** "10% off", "₹200 off" */
export const concessionValue = (valueType: string, value: string) =>
  valueType === 'PERCENT' ? `${Number(value)}% off` : `${money(value)} off`;

export const headsLabel = (ids: number[] | null, heads: FeeHead[]) =>
  !ids || ids.length === 0 ? 'Every fee' : ids.map((id) => heads.find((head) => head.id === id)?.name || `Head ${id}`).join(', ');

const ordinal = (n: number) => `${n}${['th', 'st', 'nd', 'rd'][n % 100 > 10 && n % 100 < 14 ? 0 : Math.min(n % 10, 4) % 4]}`;

/** One tier in words: "Families of 3 or more: 2nd child onwards from the eldest gets 25% off". */
export const tierText = (tier: SiblingTier) => {
  const family =
    tier.max_siblings == null
      ? `${tier.min_siblings} or more children`
      : tier.max_siblings === tier.min_siblings
      ? `${tier.min_siblings} children`
      : `${tier.min_siblings} to ${tier.max_siblings} children`;
  const who =
    tier.position_to == null
      ? `the ${ordinal(tier.position_from)} child onwards`
      : tier.position_to === tier.position_from
      ? `the ${ordinal(tier.position_from)} child`
      : `the ${ordinal(tier.position_from)} to ${ordinal(tier.position_to)} child`;
  return `Families with ${family}: ${who}, counted from the ${tier.position_basis === 'ELDEST' ? 'eldest' : 'youngest'}, gets ${Number(tier.percent)}% off`;
};

const blankTier = { min_siblings: '2', max_siblings: '', position_basis: 'ELDEST', position_from: '2', position_to: '', percent: '' };
const blank = { id: null, name: '', description: '', concession_type: 'SCHOLARSHIP', value_type: 'PERCENT', value: '', fee_head_ids: [] as number[], tiers: [] as any[], is_active: true };

const ConcessionsTab: React.FC<Props> = ({ heads }) => {
  const { notify, notifyError, node } = useNotify();
  const [rules, setRules] = useState<ConcessionRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState<any | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      setRules(await billingAPI.listRules());
    } catch (failure) {
      notifyError(failure);
    } finally {
      setLoading(false);
    }
  }, [notifyError]);

  useEffect(() => {
    load();
  }, [load]);

  const billable = heads.filter((head) => head.category !== 'PENALTY');
  const hasSiblingRule = rules.some((rule) => rule.concession_type === 'SIBLING' && rule.is_active);

  const open = (rule?: ConcessionRule) => {
    setError(null);
    setForm(
      rule
        ? {
            ...rule,
            description: rule.description || '',
            value: String(Number(rule.value)),
            fee_head_ids: rule.fee_head_ids || [],
            tiers: (rule.tiers || []).map((tier) => ({
              ...tier,
              min_siblings: String(tier.min_siblings),
              max_siblings: tier.max_siblings == null ? '' : String(tier.max_siblings),
              position_from: String(tier.position_from),
              position_to: tier.position_to == null ? '' : String(tier.position_to),
              percent: String(Number(tier.percent)),
            })),
          }
        : { ...blank }
    );
  };

  const sibling = form?.concession_type === 'SIBLING';
  const setTier = (index: number, patch: object) =>
    setForm((current: any) => ({ ...current, tiers: current.tiers.map((tier: any, i: number) => (i === index ? { ...tier, ...patch } : tier)) }));

  const tiersValid =
    form &&
    form.tiers.length > 0 &&
    form.tiers.every(
      (tier: any) =>
        Number(tier.min_siblings) >= 2 &&
        (tier.max_siblings === '' || Number(tier.max_siblings) >= Number(tier.min_siblings)) &&
        Number(tier.position_from) >= 1 &&
        (tier.position_to === '' || Number(tier.position_to) >= Number(tier.position_from)) &&
        Number(tier.percent) > 0 &&
        Number(tier.percent) <= 100
    );
  const valid =
    form &&
    form.name.trim() &&
    (sibling ? tiersValid : form.value !== '' && Number(form.value) > 0 && (form.value_type !== 'PERCENT' || Number(form.value) <= 100));

  const save = async () => {
    setBusy(true);
    setError(null);
    const body: Record<string, any> = {
      name: form.name.trim(),
      description: form.description.trim() || null,
      fee_head_ids: form.fee_head_ids.length ? form.fee_head_ids : null,
      is_active: form.is_active,
    };
    if (sibling) {
      body.tiers = form.tiers.map((tier: any) => ({
        min_siblings: Number(tier.min_siblings),
        max_siblings: tier.max_siblings === '' ? null : Number(tier.max_siblings),
        position_basis: tier.position_basis,
        position_from: Number(tier.position_from),
        position_to: tier.position_to === '' ? null : Number(tier.position_to),
        percent: Number(tier.percent).toFixed(2),
      }));
    } else {
      body.value_type = form.value_type;
      body.value = Number(form.value).toFixed(2);
    }
    try {
      if (form.id) await billingAPI.updateRule(form.id, body);
      else await billingAPI.createRule({ ...body, concession_type: form.concession_type });
      notify(sibling ? 'Sibling rule saved. It reaches unpaid dues the next time dues are generated.' : 'Concession rule saved.');
      setForm(null);
      load();
    } catch (failure) {
      setError(apiError(failure));
    } finally {
      setBusy(false);
    }
  };

  const toggle = async (rule: ConcessionRule) => {
    try {
      await billingAPI.updateRule(rule.id, { is_active: !rule.is_active });
      load();
    } catch (failure) {
      notifyError(failure);
    }
  };

  return (
    <Panel
      title="Concession rules"
      subtitle="The sibling rule works by itself for linked siblings. Give the other concessions to a student from the Collect tab."
      actions={
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => open()}>
          New rule
        </Button>
      }
    >
      {loading ? (
        <Loading />
      ) : rules.length === 0 ? (
        <EmptyState title="No concession rules yet" hint="Add a sibling rule, a staff-child discount or a scholarship." icon={<OfferIcon />} />
      ) : (
        <Box sx={{ display: 'grid', gap: 2, gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))' }}>
          {rules.map((rule, index) => {
            const isSibling = rule.concession_type === 'SIBLING';
            const color = isSibling ? brand.violet : brand.primary;
            return (
              <Box
                key={rule.id}
                sx={{
                  position: 'relative',
                  overflow: 'hidden',
                  p: 2.25,
                  borderRadius: '18px',
                  border: '1px solid rgba(15,23,42,0.08)',
                  background: `linear-gradient(160deg, ${alpha(color, 0.07)}, #fff 55%)`,
                  opacity: rule.is_active ? 1 : 0.6,
                  animation: `fadeUp 0.45s ${ease} both`,
                  animationDelay: `${index * 50}ms`,
                  transition: `transform 0.35s ${ease}, box-shadow 0.35s ${ease}`,
                  '&:hover': { transform: 'translateY(-4px)', boxShadow: brand.shadowLift, opacity: 1 },
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.5 }}>
                  <Box sx={{ display: 'grid', placeItems: 'center', flexShrink: 0, width: 42, height: 42, borderRadius: '13px', color: '#fff', background: color, boxShadow: `0 8px 18px ${alpha(color, 0.4)}` }}>
                    {isSibling ? <SiblingIcon /> : <OfferIcon />}
                  </Box>
                  <Box sx={{ flexGrow: 1, minWidth: 0 }}>
                    <Typography sx={{ fontWeight: 700 }} noWrap title={rule.name}>
                      {rule.name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {concessionTypeLabel(rule.concession_type)} · {headsLabel(rule.fee_head_ids, heads)}
                    </Typography>
                  </Box>
                  {!isSibling && <StatusChip status="PAID" label={concessionValue(rule.value_type, rule.value)} />}
                </Box>
                {rule.description && (
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    {rule.description}
                  </Typography>
                )}
                {isSibling && (
                  <Box component="ul" sx={{ m: 0, mt: 1.25, pl: 2.5, color: 'text.secondary', fontSize: '0.85rem', '& li': { mb: 0.25 } }}>
                    {(rule.tiers || []).map((tier, i) => (
                      <li key={i}>{tierText(tier)}</li>
                    ))}
                  </Box>
                )}
                <Box sx={{ display: 'flex', alignItems: 'center', mt: 1.5 }}>
                  <FormControlLabel
                    control={<Switch size="small" checked={rule.is_active} onChange={() => toggle(rule)} />}
                    label={<Typography variant="body2">{rule.is_active ? 'In use' : 'Switched off'}</Typography>}
                    sx={{ flexGrow: 1 }}
                  />
                  <Tooltip title="Edit">
                    <IconButton size="small" color="primary" onClick={() => open(rule)}>
                      <EditIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
              </Box>
            );
          })}
        </Box>
      )}

      <FormDialog
        open={Boolean(form)}
        title={form?.id ? 'Edit concession rule' : 'New concession rule'}
        onClose={() => setForm(null)}
        onSubmit={save}
        busy={busy}
        disabled={!valid}
        error={error}
        maxWidth={sibling ? 'md' : 'sm'}
      >
        {form && (
          <>
            <FieldRow>
              <TextField label="Name" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} required autoFocus slotProps={{ htmlInput: { maxLength: 100 } }} />
              <TextField
                select
                label="Kind"
                value={form.concession_type}
                onChange={(event) => setForm({ ...form, concession_type: event.target.value, tiers: event.target.value === 'SIBLING' && form.tiers.length === 0 ? [{ ...blankTier }] : form.tiers })}
                disabled={Boolean(form.id)}
              >
                {CONCESSION_TYPES.map((type) => (
                  <MenuItem key={type.value} value={type.value} disabled={type.value === 'SIBLING' && hasSiblingRule}>
                    {type.label}
                    {type.value === 'SIBLING' && hasSiblingRule ? ' (already set up)' : ''}
                  </MenuItem>
                ))}
              </TextField>
            </FieldRow>
            <TextField label="Description" value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} />
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

            {sibling ? (
              <>
                <Alert severity="info">
                  Children are counted among brothers and sisters linked on their student profile and enrolled in the session, eldest first by date of birth.
                </Alert>
                {form.tiers.map((tier: any, index: number) => (
                  <Box key={index} sx={{ p: 1.5, borderRadius: '14px', border: '1px solid rgba(15,23,42,0.08)', background: alpha(brand.violet, 0.03) }}>
                    <Box sx={{ display: 'grid', gap: 1.5, alignItems: 'center', gridTemplateColumns: { xs: '1fr 1fr', md: '1fr 1fr 1.3fr 1fr 1fr 1fr auto' } }}>
                      <TextField size="small" type="number" label="Children from" value={tier.min_siblings} onChange={(event) => setTier(index, { min_siblings: event.target.value })} slotProps={{ htmlInput: { min: 2 } }} />
                      <TextField size="small" type="number" label="Up to" value={tier.max_siblings} onChange={(event) => setTier(index, { max_siblings: event.target.value })} placeholder="any" slotProps={{ htmlInput: { min: 2 }, inputLabel: { shrink: true } }} />
                      <TextField size="small" select label="Counted from" value={tier.position_basis} onChange={(event) => setTier(index, { position_basis: event.target.value })}>
                        <MenuItem value="ELDEST">The eldest</MenuItem>
                        <MenuItem value="YOUNGEST">The youngest</MenuItem>
                      </TextField>
                      <TextField size="small" type="number" label="Child no. from" value={tier.position_from} onChange={(event) => setTier(index, { position_from: event.target.value })} slotProps={{ htmlInput: { min: 1 } }} />
                      <TextField size="small" type="number" label="To" value={tier.position_to} onChange={(event) => setTier(index, { position_to: event.target.value })} placeholder="last" slotProps={{ htmlInput: { min: 1 }, inputLabel: { shrink: true } }} />
                      <TextField size="small" type="number" label="Off" value={tier.percent} onChange={(event) => setTier(index, { percent: event.target.value })} slotProps={{ htmlInput: { min: 0.01, max: 100, step: 0.01 }, input: { endAdornment: <InputAdornment position="end">%</InputAdornment> } }} />
                      <Tooltip title="Remove">
                        <IconButton size="small" color="error" onClick={() => setForm({ ...form, tiers: form.tiers.filter((_: any, i: number) => i !== index) })}>
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                    {Number(tier.percent) > 0 && Number(tier.min_siblings) >= 2 && Number(tier.position_from) >= 1 && (
                      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                        {tierText({
                          min_siblings: Number(tier.min_siblings),
                          max_siblings: tier.max_siblings === '' ? null : Number(tier.max_siblings),
                          position_basis: tier.position_basis,
                          position_from: Number(tier.position_from),
                          position_to: tier.position_to === '' ? null : Number(tier.position_to),
                          percent: tier.percent,
                        })}
                      </Typography>
                    )}
                  </Box>
                ))}
                <Box>
                  <Button size="small" variant="outlined" startIcon={<AddIcon />} onClick={() => setForm({ ...form, tiers: [...form.tiers, { ...blankTier }] })}>
                    Add a line
                  </Button>
                </Box>
              </>
            ) : (
              <FieldRow>
                <TextField select label="Taken off as" value={form.value_type} onChange={(event) => setForm({ ...form, value_type: event.target.value })}>
                  <MenuItem value="PERCENT">A percentage of the fee</MenuItem>
                  <MenuItem value="FIXED">A fixed amount per due</MenuItem>
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
            )}
            <FormControlLabel control={<Switch checked={form.is_active} onChange={(event) => setForm({ ...form, is_active: event.target.checked })} />} label="In use" />
          </>
        )}
      </FormDialog>
      {node}
    </Panel>
  );
};

export default ConcessionsTab;
