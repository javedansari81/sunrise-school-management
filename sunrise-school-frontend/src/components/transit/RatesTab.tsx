/**
 * Transport rates for a session. An assignment takes the first rate that
 * matches: its stop, then its distance, then its vehicle type.
 */
import React, { useCallback, useEffect, useState } from 'react';
import {
  Alert,
  Button,
  IconButton,
  InputAdornment,
  ListSubheader,
  MenuItem,
  Switch,
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
import { Add as AddIcon, ContentCopy as CopyIcon, Delete as DeleteIcon, Edit as EditIcon, PriceChange as RateIcon } from '@mui/icons-material';
import { Rate, RATE_BASES, RateBasis, Route, transitAPI, TransportType } from '../../services/transitService';
import { Lookups } from '../../hooks/useLookups';
import { apiError, ConfirmDialog, ConfirmRequest, EmptyState, FieldRow, FormDialog, Loading, money, Panel, StatusChip, useNotify } from '../ui';

interface Props {
  lookups: Lookups;
  types: TransportType[];
  routes: Route[];
}

const km = (value: string | null) => (value == null ? '' : String(Number(value)));

const RatesTab: React.FC<Props> = ({ lookups, types, routes }) => {
  const { notify, notifyError, node } = useNotify();
  const [sessionId, setSessionId] = useState<number | null>(lookups.currentSessionId);
  const [rates, setRates] = useState<Rate[]>([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState<any | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copyFrom, setCopyFrom] = useState<number | '' | null>(null);
  const [confirm, setConfirm] = useState<ConfirmRequest | null>(null);

  const load = useCallback(async () => {
    if (sessionId == null) return;
    setLoading(true);
    try {
      setRates(await transitAPI.listRates(sessionId));
    } catch (failure) {
      notifyError(failure);
    } finally {
      setLoading(false);
    }
  }, [sessionId, notifyError]);

  useEffect(() => {
    load();
  }, [load]);

  const typeName = (id: number | null) => (id == null ? 'Any vehicle type' : types.find((item) => item.id === id)?.name || '—');
  const stopName = (id: number | null) => {
    for (const route of routes) {
      const stop = route.stops.find((item) => item.id === id);
      if (stop) return `${route.name} · ${stop.name}`;
    }
    return '—';
  };
  const appliesTo = (rate: Rate) => {
    if (rate.basis === 'PER_STOP') return `${stopName(rate.route_stop_id)}${rate.transport_type_id ? ` (${typeName(rate.transport_type_id)})` : ''}`;
    if (rate.basis === 'DISTANCE_SLAB') return `${km(rate.distance_from_km)} to ${km(rate.distance_to_km)} km · ${typeName(rate.transport_type_id)}`;
    return typeName(rate.transport_type_id);
  };

  const open = (rate?: Rate) => {
    setError(null);
    setForm(
      rate
        ? { id: rate.id, basis: rate.basis, transport_type_id: rate.transport_type_id ?? '', route_stop_id: rate.route_stop_id ?? '', from: km(rate.distance_from_km), to: km(rate.distance_to_km), amount: String(Number(rate.monthly_amount)), description: rate.description || '' }
        : { id: null, basis: 'FLAT' as RateBasis, transport_type_id: '', route_stop_id: '', from: '', to: '', amount: '', description: '' }
    );
  };

  const basis: RateBasis | undefined = form?.basis;
  const valid =
    form &&
    form.amount !== '' &&
    Number(form.amount) >= 0 &&
    (basis === 'FLAT'
      ? form.transport_type_id !== ''
      : basis === 'PER_STOP'
      ? form.route_stop_id !== ''
      : form.from !== '' && form.to !== '' && Number(form.to) > Number(form.from));

  const save = async () => {
    if (!form || sessionId == null) return;
    setBusy(true);
    setError(null);
    const amount = Number(form.amount).toFixed(2);
    const slab = basis === 'DISTANCE_SLAB' ? { distance_from_km: Number(form.from).toFixed(2), distance_to_km: Number(form.to).toFixed(2) } : {};
    try {
      if (form.id) {
        await transitAPI.updateRate(form.id, { monthly_amount: amount, description: form.description.trim() || null, ...slab });
      } else {
        await transitAPI.createRate({
          session_year_id: sessionId,
          basis,
          transport_type_id: form.transport_type_id,
          route_stop_id: basis === 'PER_STOP' ? form.route_stop_id : undefined,
          monthly_amount: amount,
          description: form.description.trim(),
          ...slab,
        });
      }
      notify('Rate saved. It applies to assignments made or changed from now on.');
      setForm(null);
      load();
    } catch (failure) {
      setError(apiError(failure));
    } finally {
      setBusy(false);
    }
  };

  const copy = async () => {
    if (!copyFrom || sessionId == null) return;
    setBusy(true);
    setError(null);
    try {
      const result = await transitAPI.copyRates(copyFrom, sessionId);
      notify(result.copied ? `${result.copied} rates copied.` : 'That session has no rates to copy.', result.copied ? 'success' : 'info');
      setCopyFrom(null);
      load();
    } catch (failure) {
      setError(apiError(failure));
    } finally {
      setBusy(false);
    }
  };

  const toggle = async (rate: Rate) => {
    try {
      await transitAPI.updateRate(rate.id, { is_active: !rate.is_active });
      load();
    } catch (failure) {
      notifyError(failure);
    }
  };

  const order: Record<RateBasis, number> = { PER_STOP: 0, DISTANCE_SLAB: 1, FLAT: 2 };
  const sorted = [...rates].sort((a, b) => order[a.basis] - order[b.basis] || Number(a.distance_from_km ?? 0) - Number(b.distance_from_km ?? 0) || a.id - b.id);

  return (
    <Panel
      title="Transport rates"
      subtitle="A student pays the rate of their stop if there is one, else of their distance, else of their vehicle type."
      padded={false}
      actions={
        <>
          <TextField select size="small" label="Session" value={sessionId ?? ''} onChange={(event) => setSessionId(Number(event.target.value))} sx={{ minWidth: 130 }}>
            {lookups.sessionYears.map((year) => (
              <MenuItem key={year.id} value={year.id}>
                {year.name}
              </MenuItem>
            ))}
          </TextField>
          <Button
            variant="outlined"
            startIcon={<CopyIcon />}
            onClick={() => {
              setError(null);
              setCopyFrom('');
            }}
          >
            Copy from a session
          </Button>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => open()} disabled={sessionId == null}>
            New rate
          </Button>
        </>
      }
    >
      {loading ? (
        <Loading />
      ) : sorted.length === 0 ? (
        <EmptyState title="No rates for this session" hint="Add a flat rate per vehicle type, or copy last session's rates." icon={<RateIcon />} />
      ) : (
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Kind</TableCell>
                <TableCell>Applies to</TableCell>
                <TableCell align="right">Monthly fee</TableCell>
                <TableCell>Note</TableCell>
                <TableCell>Active</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {sorted.map((rate) => (
                <TableRow key={rate.id} hover sx={{ opacity: rate.is_active ? 1 : 0.55 }}>
                  <TableCell>
                    <StatusChip status={rate.basis === 'FLAT' ? 'PENDING' : rate.basis === 'PER_STOP' ? 'WAIVED' : 'PARTIAL'} label={RATE_BASES.find((item) => item.value === rate.basis)?.label} />
                  </TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>{appliesTo(rate)}</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 800 }}>
                    {money(rate.monthly_amount)}
                  </TableCell>
                  <TableCell>{rate.description || '—'}</TableCell>
                  <TableCell>
                    <Switch size="small" checked={rate.is_active} onChange={() => toggle(rate)} slotProps={{ input: { 'aria-label': 'Rate active' } }} />
                  </TableCell>
                  <TableCell align="right" sx={{ whiteSpace: 'nowrap' }}>
                    <Tooltip title="Edit amount">
                      <IconButton size="small" color="primary" onClick={() => open(rate)}>
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() =>
                          setConfirm({
                            title: 'Delete rate',
                            message: `Delete the rate for ${appliesTo(rate)} (${money(rate.monthly_amount)})? Students already assigned keep the fee they have.`,
                            confirmLabel: 'Delete',
                            danger: true,
                            onConfirm: async () => {
                              await transitAPI.deleteRate(rate.id);
                              notify('Rate deleted.');
                              load();
                            },
                          })
                        }
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <FormDialog open={Boolean(form)} title={form?.id ? 'Edit rate' : 'New rate'} subtitle={`Session ${lookups.sessionName(sessionId)}`} onClose={() => setForm(null)} onSubmit={save} busy={busy} disabled={!valid} error={error}>
        {form && (
          <>
            <TextField select label="Kind of rate" value={form.basis} onChange={(event) => setForm({ ...form, basis: event.target.value, route_stop_id: '', from: '', to: '' })} disabled={Boolean(form.id)} helperText={RATE_BASES.find((item) => item.value === form.basis)?.hint}>
              {RATE_BASES.map((item) => (
                <MenuItem key={item.value} value={item.value}>
                  {item.label}
                </MenuItem>
              ))}
            </TextField>
            {form.id && <Alert severity="info">Only the amount, slab and note of an existing rate can be changed. Add a new rate for anything else.</Alert>}
            {basis === 'PER_STOP' && (
              <TextField select label="Stop" value={form.route_stop_id} onChange={(event) => setForm({ ...form, route_stop_id: Number(event.target.value) })} required disabled={Boolean(form.id)}>
                {routes.flatMap((route) => [
                  <ListSubheader key={`route-${route.id}`}>{route.name}</ListSubheader>,
                  ...route.stops.map((stop) => (
                    <MenuItem key={stop.id} value={stop.id}>
                      {stop.sequence}. {stop.name}
                    </MenuItem>
                  )),
                ])}
              </TextField>
            )}
            {basis === 'DISTANCE_SLAB' && (
              <FieldRow>
                <TextField label="From" type="number" value={form.from} onChange={(event) => setForm({ ...form, from: event.target.value })} required slotProps={{ htmlInput: { min: 0, step: 0.1 }, input: { endAdornment: <InputAdornment position="end">km</InputAdornment> } }} />
                <TextField label="Up to" type="number" value={form.to} onChange={(event) => setForm({ ...form, to: event.target.value })} required error={form.to !== '' && Number(form.to) <= Number(form.from)} slotProps={{ htmlInput: { min: 0, step: 0.1 }, input: { endAdornment: <InputAdornment position="end">km</InputAdornment> } }} />
              </FieldRow>
            )}
            <FieldRow>
              <TextField select label="Vehicle type" value={form.transport_type_id} onChange={(event) => setForm({ ...form, transport_type_id: event.target.value === '' ? '' : Number(event.target.value) })} required={basis === 'FLAT'} disabled={Boolean(form.id)} slotProps={{ select: { displayEmpty: true }, inputLabel: { shrink: true } }}>
                {basis !== 'FLAT' && <MenuItem value="">Any vehicle type</MenuItem>}
                {types
                  .filter((item) => item.is_active || item.id === form.transport_type_id)
                  .map((item) => (
                    <MenuItem key={item.id} value={item.id}>
                      {item.name}
                    </MenuItem>
                  ))}
              </TextField>
              <TextField label="Monthly fee" type="number" value={form.amount} onChange={(event) => setForm({ ...form, amount: event.target.value })} required slotProps={{ htmlInput: { min: 0, step: 0.01 }, input: { startAdornment: <InputAdornment position="start">₹</InputAdornment> } }} />
            </FieldRow>
            <TextField label="Note" value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} slotProps={{ htmlInput: { maxLength: 255 } }} />
          </>
        )}
      </FormDialog>

      <FormDialog open={copyFrom !== null} title="Copy rates" subtitle={`Into session ${lookups.sessionName(sessionId)}`} onClose={() => setCopyFrom(null)} onSubmit={copy} submitLabel="Copy" busy={busy} disabled={!copyFrom} error={error} maxWidth="xs">
        <Typography variant="body2" color="text.secondary">
          This works while the session has no rates of its own yet.
        </Typography>
        <TextField select label="Copy from session" value={copyFrom ?? ''} onChange={(event) => setCopyFrom(Number(event.target.value))}>
          {lookups.sessionYears
            .filter((year) => year.id !== sessionId)
            .map((year) => (
              <MenuItem key={year.id} value={year.id}>
                {year.name}
              </MenuItem>
            ))}
        </TextField>
      </FormDialog>
      <ConfirmDialog request={confirm} onClose={() => setConfirm(null)} />
      {node}
    </Panel>
  );
};

export default RatesTab;
