/**
 * Riders: which student rides which route, stop and vehicle type. Assigning,
 * changing, pausing or ending a ride updates the student's transport fee by itself.
 */
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Alert,
  Autocomplete,
  Box,
  Button,
  Checkbox,
  Chip,
  FormControlLabel,
  IconButton,
  InputAdornment,
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
import {
  Block as CancelIcon,
  DirectionsBus as BusIcon,
  Edit as EditIcon,
  PauseCircle as PauseIcon,
  PersonAdd as AssignIcon,
  StopCircle as StopIcon,
} from '@mui/icons-material';
import { Assignment, Route, transitAPI, TransportType, Vehicle } from '../../services/transitService';
import { searchStudents, StudentLite } from '../../services/billingService';
import { Lookups } from '../../hooks/useLookups';
import {
  apiError,
  ConfirmDialog,
  ConfirmRequest,
  EmptyState,
  FieldRow,
  FormDialog,
  formatDate,
  formatMonth,
  Loading,
  money,
  Panel,
  StatusChip,
  todayISO,
  useNotify,
} from '../ui';

interface Props {
  lookups: Lookups;
  types: TransportType[];
  vehicles: Vehicle[];
  routes: Route[];
}

const monthOf = (value: string) => value.slice(0, 7);

const rideStatus = (assignment: Assignment): { status: string; label?: string } => {
  const today = todayISO();
  if (!assignment.is_active) return { status: 'CANCELLED' };
  if (assignment.end_date && assignment.end_date < today) return { status: 'ENDED', label: `Ended ${formatDate(assignment.end_date)}` };
  if (assignment.start_date > today) return { status: 'PENDING', label: `Starts ${formatDate(assignment.start_date)}` };
  const month = monthOf(today);
  if (assignment.pauses.some((pause) => pause.is_active && monthOf(pause.from_period) <= month && month <= monthOf(pause.to_period))) {
    return { status: 'PAUSED' };
  }
  return { status: 'RIDING', label: assignment.end_date ? `Riding until ${formatDate(assignment.end_date)}` : 'Riding' };
};

// ---------------------------------------------------------------------------
// Assign a student, or change an existing ride
// ---------------------------------------------------------------------------

interface AssignProps extends Props {
  open: boolean;
  sessionYearId: number;
  existing: Assignment | null;
  onClose: () => void;
  onDone: (warnings: string[]) => void;
}

const AssignDialog: React.FC<AssignProps> = ({ open, sessionYearId, existing, types, vehicles, routes, onClose, onDone }) => {
  const [student, setStudent] = useState<StudentLite | null>(null);
  const [options, setOptions] = useState<StudentLite[]>([]);
  const [query, setQuery] = useState('');
  const [typeId, setTypeId] = useState<number | ''>('');
  const [routeId, setRouteId] = useState<number | ''>('');
  const [stopId, setStopId] = useState<number | ''>('');
  const [distance, setDistance] = useState('');
  const [date, setDate] = useState(todayISO());
  const [pickup, setPickup] = useState('');
  const [drop, setDrop] = useState('');
  const [override, setOverride] = useState(false);
  const [amount, setAmount] = useState('');
  const [overCapacity, setOverCapacity] = useState(false);
  const [remarks, setRemarks] = useState('');
  const [quote, setQuote] = useState<{ monthly_amount: string | null; basis: string | null } | null>(null);
  const [quoteError, setQuoteError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    setStudent(null);
    setQuery('');
    setTypeId(existing?.transport_type_id ?? '');
    setRouteId(existing?.route_id ?? '');
    setStopId(existing?.route_stop_id ?? '');
    setDistance(existing?.distance_km ? String(Number(existing.distance_km)) : '');
    setDate(todayISO());
    setPickup(existing?.pickup_location || '');
    setDrop(existing?.drop_location || '');
    setOverride(Boolean(existing?.amount_overridden));
    setAmount(existing?.amount_overridden ? String(Number(existing.monthly_amount)) : '');
    setOverCapacity(false);
    setRemarks('');
    setQuote(null);
    setQuoteError(null);
    setError(null);
  }, [open, existing]);

  // Student search for a new assignment
  useEffect(() => {
    if (!open || existing) return;
    let cancelled = false;
    const timer = setTimeout(() => {
      searchStudents({ search: query.trim(), per_page: 20 })
        .then((found) => !cancelled && setOptions(found.students))
        .catch(() => undefined);
    }, 250);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [open, existing, query]);

  const route = routes.find((item) => item.id === routeId);
  const stops = route?.stops.filter((stop) => stop.is_active || stop.id === stopId) || [];

  const pickRoute = (id: number | '') => {
    setRouteId(id);
    setStopId('');
    setDistance(''); // the new stop brings its own distance
    const vehicle = vehicles.find((item) => item.id === routes.find((r) => r.id === id)?.vehicle_id);
    if (vehicle) setTypeId(vehicle.transport_type_id);
  };

  const placement = useMemo(
    () => ({
      transport_type_id: typeId === '' ? null : typeId,
      route_id: routeId === '' ? null : routeId,
      route_stop_id: stopId === '' ? null : stopId,
      distance_km: distance === '' ? null : Number(distance).toFixed(2),
    }),
    [typeId, routeId, stopId, distance]
  );

  // What the rate table says for this placement
  useEffect(() => {
    if (!open || (typeId === '' && routeId === '' && stopId === '')) {
      setQuote(null);
      return;
    }
    let cancelled = false;
    const timer = setTimeout(() => {
      transitAPI
        .quote({ session_year_id: sessionYearId, ...placement })
        .then((result) => {
          if (cancelled) return;
          setQuote(result);
          setQuoteError(null);
        })
        .catch((failure) => {
          if (cancelled) return;
          setQuote(null);
          setQuoteError(apiError(failure));
        });
    }, 300);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [open, sessionYearId, placement, typeId, routeId, stopId]);

  const noRate = quote && quote.monthly_amount == null;
  const ready = (existing || student) && (typeId !== '' || routeId !== '' || stopId !== '') && date && (!override || Number(amount) >= 0) && (override ? amount !== '' : !noRate);

  const submit = async () => {
    setBusy(true);
    setError(null);
    const common = {
      ...placement,
      pickup_location: pickup.trim() || null,
      drop_location: drop.trim() || null,
      monthly_amount: override ? Number(amount).toFixed(2) : null,
      remarks: remarks.trim() || null,
      allow_over_capacity: overCapacity,
    };
    try {
      const result = existing
        ? await transitAPI.change(existing.id, { ...common, effective_date: date })
        : await transitAPI.assign({ ...common, student_id: student!.id, session_year_id: sessionYearId, start_date: date });
      onDone(result.warnings || []);
      onClose();
    } catch (failure) {
      setError(apiError(failure));
    } finally {
      setBusy(false);
    }
  };

  return (
    <FormDialog
      open={open}
      title={existing ? 'Change transport' : 'Assign transport'}
      subtitle={existing ? `${existing.student_name} · ${existing.admission_number}` : 'The transport fee is added to the student by itself'}
      onClose={onClose}
      onSubmit={submit}
      submitLabel={existing ? 'Save change' : 'Assign'}
      busy={busy}
      disabled={!ready}
      error={error}
      maxWidth="md"
    >
      {!existing && (
        <Autocomplete
          options={options}
          value={student}
          onChange={(_, value) => setStudent(value)}
          onInputChange={(_, value) => setQuery(value)}
          filterOptions={(items) => items}
          getOptionLabel={(option) => `${option.first_name} ${option.last_name} (${option.admission_number})`}
          isOptionEqualToValue={(option, value) => option.id === value.id}
          renderOption={(props, option) => (
            <li {...props} key={option.id}>
              <Box>
                <Typography sx={{ fontSize: '0.9rem', fontWeight: 600 }}>
                  {option.first_name} {option.last_name}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {option.admission_number} · {option.class_name || ''}
                </Typography>
              </Box>
            </li>
          )}
          renderInput={(params) => <TextField {...params} label="Student" placeholder="Type a name or admission number" required autoFocus />}
        />
      )}
      <FieldRow columns={3}>
        <TextField select label="Route" value={routeId} onChange={(event) => pickRoute(event.target.value === '' ? '' : Number(event.target.value))} slotProps={{ select: { displayEmpty: true }, inputLabel: { shrink: true } }}>
          <MenuItem value="">No fixed route</MenuItem>
          {routes
            .filter((item) => item.is_active || item.id === routeId)
            .map((item) => (
              <MenuItem key={item.id} value={item.id}>
                {item.name}
              </MenuItem>
            ))}
        </TextField>
        <TextField select label="Stop" value={stopId} onChange={(event) => {
            setStopId(event.target.value === '' ? '' : Number(event.target.value));
            setDistance('');
          }} disabled={!route} slotProps={{ select: { displayEmpty: true }, inputLabel: { shrink: true } }}>
          <MenuItem value="">{route ? 'No stop chosen' : 'Pick a route first'}</MenuItem>
          {stops.map((stop) => (
            <MenuItem key={stop.id} value={stop.id}>
              {stop.sequence}. {stop.name}
            </MenuItem>
          ))}
        </TextField>
        <TextField select label="Vehicle type" value={typeId} onChange={(event) => setTypeId(event.target.value === '' ? '' : Number(event.target.value))} helperText={route?.vehicle_id ? 'From the route’s vehicle' : undefined}>
          {types
            .filter((item) => item.is_active || item.id === typeId)
            .map((item) => (
              <MenuItem key={item.id} value={item.id}>
                {item.name}
              </MenuItem>
            ))}
        </TextField>
      </FieldRow>
      <FieldRow columns={3}>
        <TextField
          label="Distance"
          type="number"
          value={distance}
          onChange={(event) => setDistance(event.target.value)}
          helperText="Leave empty to use the stop’s distance"
          slotProps={{ htmlInput: { min: 0, step: 0.1 }, input: { endAdornment: <InputAdornment position="end">km</InputAdornment> } }}
        />
        <TextField
          label={existing ? 'New terms start on' : 'Starts riding on'}
          type="date"
          value={date}
          onChange={(event) => setDate(event.target.value)}
          required
          slotProps={{ inputLabel: { shrink: true } }}
        />
        <Box sx={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', px: 2, py: 1, borderRadius: '12px', background: 'rgba(37,99,235,0.06)', border: '1px dashed rgba(37,99,235,0.3)' }}>
          <Typography variant="caption" color="text.secondary">
            Monthly fee from the rate table
          </Typography>
          <Typography sx={{ fontWeight: 800, fontSize: '1.15rem', color: noRate || quoteError ? 'error.main' : 'primary.main' }}>
            {quoteError ? 'Not available' : quote ? (quote.monthly_amount != null ? money(quote.monthly_amount) : 'No rate found') : '—'}
          </Typography>
        </Box>
      </FieldRow>
      {quoteError && <Alert severity="warning">{quoteError}</Alert>}
      {noRate && !override && <Alert severity="warning">No rate matches this placement. Add one on the Rates tab, or set the amount yourself below.</Alert>}
      <FieldRow>
        <TextField label="Pickup point" value={pickup} onChange={(event) => setPickup(event.target.value)} slotProps={{ htmlInput: { maxLength: 200 } }} />
        <TextField label="Drop point" value={drop} onChange={(event) => setDrop(event.target.value)} slotProps={{ htmlInput: { maxLength: 200 } }} />
      </FieldRow>
      <FieldRow>
        <Box>
          <FormControlLabel control={<Checkbox checked={override} onChange={(event) => setOverride(event.target.checked)} />} label="Set the monthly fee myself" />
          {override && (
            <TextField
              fullWidth
              label="Monthly fee"
              type="number"
              value={amount}
              onChange={(event) => setAmount(event.target.value)}
              required
              slotProps={{ htmlInput: { min: 0, step: 0.01 }, input: { startAdornment: <InputAdornment position="start">₹</InputAdornment> } }}
            />
          )}
        </Box>
        <FormControlLabel control={<Checkbox checked={overCapacity} onChange={(event) => setOverCapacity(event.target.checked)} />} label="Allow even if the vehicle is full" />
      </FieldRow>
      <TextField label="Remarks" value={remarks} onChange={(event) => setRemarks(event.target.value)} />
    </FormDialog>
  );
};

// ---------------------------------------------------------------------------
// Pause and end
// ---------------------------------------------------------------------------

const PauseDialog: React.FC<{ assignment: Assignment | null; onClose: () => void; onDone: (message: string) => void }> = ({ assignment, onClose, onDone }) => {
  const [from, setFrom] = useState(monthOf(todayISO()));
  const [to, setTo] = useState(monthOf(todayISO()));
  const [reason, setReason] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setFrom(monthOf(todayISO()));
    setTo(monthOf(todayISO()));
    setReason('');
    setError(null);
  }, [assignment]);

  const act = async (call: () => Promise<unknown>, message: string) => {
    setBusy(true);
    setError(null);
    try {
      await call();
      onDone(message);
      onClose();
    } catch (failure) {
      setError(apiError(failure));
    } finally {
      setBusy(false);
    }
  };

  const pauses = assignment?.pauses.filter((pause) => pause.is_active) || [];

  return (
    <FormDialog
      open={Boolean(assignment)}
      title="Pause transport"
      subtitle={assignment ? `${assignment.student_name} · paused months are not billed` : undefined}
      onClose={onClose}
      onSubmit={() => assignment && act(() => transitAPI.pause(assignment.id, { from_period: `${from}-01`, to_period: `${to}-01`, reason: reason.trim() }), 'Transport paused.')}
      submitLabel="Pause"
      busy={busy}
      disabled={!from || !to || to < from}
      error={error}
    >
      {pauses.length > 0 && (
        <Box>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Current pauses (remove one to bill those months again)
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {pauses.map((pause) => (
              <Chip
                key={pause.id}
                color="warning"
                variant="outlined"
                label={pause.from_period === pause.to_period ? formatMonth(pause.from_period) : `${formatMonth(pause.from_period)} to ${formatMonth(pause.to_period)}`}
                onDelete={busy ? undefined : () => act(() => transitAPI.removePause(pause.id), 'Pause removed.')}
              />
            ))}
          </Box>
        </Box>
      )}
      <FieldRow>
        <TextField label="First paused month" type="month" value={from} onChange={(event) => setFrom(event.target.value)} required slotProps={{ inputLabel: { shrink: true } }} />
        <TextField label="Last paused month" type="month" value={to} onChange={(event) => setTo(event.target.value)} required slotProps={{ inputLabel: { shrink: true }, htmlInput: { min: from } }} />
      </FieldRow>
      <TextField label="Reason" value={reason} onChange={(event) => setReason(event.target.value)} />
    </FormDialog>
  );
};

const DiscontinueDialog: React.FC<{ assignment: Assignment | null; onClose: () => void; onDone: () => void }> = ({ assignment, onClose, onDone }) => {
  const [date, setDate] = useState(todayISO());
  const [reason, setReason] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setDate(todayISO());
    setReason('');
    setError(null);
  }, [assignment]);

  const submit = async () => {
    if (!assignment) return;
    setBusy(true);
    setError(null);
    try {
      await transitAPI.discontinue(assignment.id, { end_date: date, reason: reason.trim() });
      onDone();
      onClose();
    } catch (failure) {
      setError(apiError(failure));
    } finally {
      setBusy(false);
    }
  };

  return (
    <FormDialog
      open={Boolean(assignment)}
      title="Stop transport"
      subtitle={assignment ? `${assignment.student_name} · months after the last day are not billed` : undefined}
      onClose={onClose}
      onSubmit={submit}
      submitLabel="Stop transport"
      submitColor="error"
      busy={busy}
      disabled={!date}
      error={error}
      maxWidth="xs"
    >
      <TextField label="Last day of riding" type="date" value={date} onChange={(event) => setDate(event.target.value)} required slotProps={{ inputLabel: { shrink: true }, htmlInput: { min: assignment?.start_date } }} />
      <TextField label="Reason" value={reason} onChange={(event) => setReason(event.target.value)} multiline minRows={2} />
    </FormDialog>
  );
};

// ---------------------------------------------------------------------------
// List
// ---------------------------------------------------------------------------

const AssignmentsTab: React.FC<Props> = (props) => {
  const { lookups, types, routes } = props;
  const { notify, notifyError, node } = useNotify();
  const [sessionId, setSessionId] = useState<number | null>(lookups.currentSessionId);
  const [routeFilter, setRouteFilter] = useState<number | ''>('');
  const [search, setSearch] = useState('');
  const [ridingToday, setRidingToday] = useState(true);
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [loading, setLoading] = useState(true);

  const [assignOpen, setAssignOpen] = useState(false);
  const [changing, setChanging] = useState<Assignment | null>(null);
  const [pausing, setPausing] = useState<Assignment | null>(null);
  const [stopping, setStopping] = useState<Assignment | null>(null);
  const [confirm, setConfirm] = useState<ConfirmRequest | null>(null);

  const load = useCallback(async () => {
    if (sessionId == null) return;
    setLoading(true);
    try {
      setAssignments(
        await transitAPI.listAssignments({ session_year_id: sessionId, route_id: routeFilter, active_on: ridingToday ? todayISO() : undefined })
      );
    } catch (failure) {
      notifyError(failure);
    } finally {
      setLoading(false);
    }
  }, [sessionId, routeFilter, ridingToday, notifyError]);

  useEffect(() => {
    load();
  }, [load]);

  const typeName = (id: number) => types.find((item) => item.id === id)?.name || '—';
  const placeName = (assignment: Assignment) => {
    const route = routes.find((item) => item.id === assignment.route_id);
    const stop = route?.stops.find((item) => item.id === assignment.route_stop_id);
    if (!route) return assignment.distance_km ? `${Number(assignment.distance_km)} km` : 'No fixed route';
    return stop ? `${route.name} · ${stop.name}` : route.name;
  };

  const term = search.trim().toLowerCase();
  const visible = term
    ? assignments.filter((item) => `${item.student_name} ${item.admission_number}`.toLowerCase().includes(term))
    : assignments;

  const done = (message: string, warnings: string[] = []) => {
    if (warnings.length) notify(`${message} Note: ${warnings.join(' ')}`, 'warning');
    else notify(message);
    load();
  };

  return (
    <Panel
      title="Riders"
      subtitle={loading ? 'Loading…' : `${visible.length} ${ridingToday ? 'riding today' : 'assignments'}`}
      padded={false}
      actions={
        <>
          <TextField size="small" placeholder="Search student" value={search} onChange={(event) => setSearch(event.target.value)} sx={{ width: 170 }} />
          <TextField select size="small" label="Session" value={sessionId ?? ''} onChange={(event) => setSessionId(Number(event.target.value))} sx={{ minWidth: 120 }}>
            {lookups.sessionYears.map((year) => (
              <MenuItem key={year.id} value={year.id}>
                {year.name}
              </MenuItem>
            ))}
          </TextField>
          <TextField select size="small" label="Route" value={routeFilter} onChange={(event) => setRouteFilter(event.target.value === '' ? '' : Number(event.target.value))} sx={{ minWidth: 150 }} slotProps={{ select: { displayEmpty: true }, inputLabel: { shrink: true } }}>
            <MenuItem value="">All routes</MenuItem>
            {routes.map((item) => (
              <MenuItem key={item.id} value={item.id}>
                {item.name}
              </MenuItem>
            ))}
          </TextField>
          <FormControlLabel control={<Switch checked={ridingToday} onChange={(event) => setRidingToday(event.target.checked)} />} label="Riding today" sx={{ mr: 0 }} />
          <Button variant="contained" startIcon={<AssignIcon />} onClick={() => setAssignOpen(true)} disabled={sessionId == null}>
            Assign student
          </Button>
        </>
      }
    >
      {loading ? (
        <Loading />
      ) : visible.length === 0 ? (
        <EmptyState
          title={ridingToday ? 'Nobody is riding today' : 'No transport assignments'}
          hint={types.length === 0 ? 'Add vehicle types and rates first, then assign students.' : 'Assign a student to a route to start billing their transport.'}
          icon={<BusIcon />}
        />
      ) : (
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Student</TableCell>
                <TableCell>Route and stop</TableCell>
                <TableCell>Vehicle type</TableCell>
                <TableCell align="right">Monthly fee</TableCell>
                <TableCell>Since</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {visible.map((assignment) => {
                const state = rideStatus(assignment);
                const live = state.status === 'RIDING' || state.status === 'PAUSED' || state.status === 'PENDING';
                return (
                  <TableRow key={assignment.id} hover sx={{ opacity: live ? 1 : 0.6 }}>
                    <TableCell>
                      <Typography sx={{ fontWeight: 600, fontSize: '0.875rem' }}>{assignment.student_name}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {assignment.admission_number}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      {placeName(assignment)}
                      {assignment.pickup_location && (
                        <Typography variant="caption" color="text.secondary" component="div">
                          Pickup: {assignment.pickup_location}
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>{typeName(assignment.transport_type_id)}</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 700 }}>
                      {money(assignment.monthly_amount)}
                      {assignment.amount_overridden && (
                        <Typography variant="caption" color="warning.main" component="div">
                          set by hand
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>{formatDate(assignment.start_date)}</TableCell>
                    <TableCell>
                      <StatusChip status={state.status} label={state.label} />
                    </TableCell>
                    <TableCell align="right" sx={{ whiteSpace: 'nowrap' }}>
                      {live && (
                        <>
                          <Tooltip title="Change route, stop or fee">
                            <IconButton size="small" color="primary" onClick={() => setChanging(assignment)}>
                              <EditIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Pause for some months">
                            <IconButton size="small" color="warning" onClick={() => setPausing(assignment)}>
                              <PauseIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Stop transport">
                            <IconButton size="small" color="error" onClick={() => setStopping(assignment)}>
                              <StopIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Entered by mistake: cancel it">
                            <IconButton
                              size="small"
                              onClick={() =>
                                setConfirm({
                                  title: 'Cancel assignment',
                                  message: `Cancel ${assignment.student_name}'s transport as if it was never entered? Its unpaid transport dues are cancelled. This is refused once money was paid against it; stop the transport instead.`,
                                  confirmLabel: 'Cancel assignment',
                                  danger: true,
                                  reason: { label: 'Reason', required: true },
                                  onConfirm: async (reason) => {
                                    await transitAPI.cancel(assignment.id, reason);
                                    done('Assignment cancelled.');
                                  },
                                })
                              }
                            >
                              <CancelIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </>
                      )}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {sessionId != null && (
        <AssignDialog
          {...props}
          open={assignOpen || Boolean(changing)}
          sessionYearId={sessionId}
          existing={changing}
          onClose={() => {
            setAssignOpen(false);
            setChanging(null);
          }}
          onDone={(warnings) => done(changing ? 'Transport changed. The fee follows from the new start date.' : 'Student assigned. The transport fee was added to their fee plan.', warnings)}
        />
      )}
      <PauseDialog assignment={pausing} onClose={() => setPausing(null)} onDone={(message) => done(message)} />
      <DiscontinueDialog assignment={stopping} onClose={() => setStopping(null)} onDone={() => done('Transport stopped.')} />
      <ConfirmDialog request={confirm} onClose={() => setConfirm(null)} />
      {node}
    </Panel>
  );
};

export default AssignmentsTab;
