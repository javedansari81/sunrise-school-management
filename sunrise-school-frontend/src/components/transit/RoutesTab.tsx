/** Routes and their stops in riding order, with the list of who rides on a day. */
import React, { useEffect, useState } from 'react';
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
import {
  Add as AddIcon,
  ArrowDownward as DownIcon,
  ArrowUpward as UpIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Groups as RosterIcon,
  Place as PlaceIcon,
  Route as RouteIcon,
} from '@mui/icons-material';
import { Route, RouteRoster, Stop, transitAPI, TransportType, Vehicle } from '../../services/transitService';
import {
  apiError,
  ConfirmDialog,
  ConfirmRequest,
  EmptyState,
  FieldRow,
  FormDialog,
  Loading,
  Panel,
  StatusChip,
  todayISO,
  useNotify,
} from '../ui';
import { brand, ease } from '../../theme';

interface Props {
  types: TransportType[];
  vehicles: Vehicle[];
  routes: Route[];
  reload: () => Promise<void>;
}

const time = (value: string | null) => (value ? value.slice(0, 5) : '');

// ---------------------------------------------------------------------------
// Roster
// ---------------------------------------------------------------------------

const RosterDialog: React.FC<{ route: Route | null; onClose: () => void }> = ({ route, onClose }) => {
  const [date, setDate] = useState(todayISO());
  const [roster, setRoster] = useState<RouteRoster | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!route) return;
    let cancelled = false;
    setRoster(null);
    setError(null);
    transitAPI
      .routeRoster(route.id, date)
      .then((result) => !cancelled && setRoster(result))
      .catch((failure) => !cancelled && setError(apiError(failure)));
    return () => {
      cancelled = true;
    };
  }, [route, date]);

  return (
    <FormDialog open={Boolean(route)} title={`Riders on ${route?.name || ''}`} onClose={onClose} error={error} maxWidth="sm">
      <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
        <TextField size="small" type="date" label="Day" value={date} onChange={(event) => setDate(event.target.value)} slotProps={{ inputLabel: { shrink: true } }} />
        {roster && (
          <Typography variant="body2" color="text.secondary">
            <strong>{roster.riding}</strong> riding{roster.seats != null && ` of ${roster.seats} seats`}
            {roster.paused > 0 && `, ${roster.paused} paused`}
            {roster.vehicle && ` · ${roster.vehicle.registration_number}`}
          </Typography>
        )}
      </Box>
      {roster?.over_capacity && <Alert severity="warning">More riders than seats on this route.</Alert>}
      {!roster && !error && <Loading />}
      {roster && roster.riding + roster.paused === 0 && <EmptyState title="Nobody rides this route on that day" icon={<RosterIcon />} />}
      {roster?.stops
        .filter((group) => group.riders.length > 0)
        .map((group, index) => (
          <Box key={group.stop?.id ?? `none-${index}`}>
            <Typography sx={{ fontWeight: 700, fontSize: '0.9rem', mb: 0.5 }}>
              {group.stop ? `${group.stop.sequence}. ${group.stop.name}` : 'No stop chosen'}{' '}
              <Typography component="span" variant="caption" color="text.secondary">
                ({group.riders.length})
              </Typography>
            </Typography>
            {group.riders.map((rider) => (
              <Box key={rider.assignment_id} sx={{ display: 'flex', alignItems: 'center', gap: 1, py: 0.5, pl: 2, borderLeft: `2px solid ${alpha(brand.primary, 0.25)}` }}>
                <Typography sx={{ flexGrow: 1, fontSize: '0.875rem' }}>
                  {rider.student_name}{' '}
                  <Typography component="span" variant="caption" color="text.secondary">
                    {rider.admission_number}
                    {rider.class_name ? ` · ${rider.class_name}` : ''}
                  </Typography>
                </Typography>
                {rider.paused && <StatusChip status="PAUSED" />}
              </Box>
            ))}
          </Box>
        ))}
    </FormDialog>
  );
};

// ---------------------------------------------------------------------------
// Routes and stops
// ---------------------------------------------------------------------------

const RoutesTab: React.FC<Props> = ({ types, vehicles, routes, reload }) => {
  const { notify, notifyError, node } = useNotify();
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [routeForm, setRouteForm] = useState<any | null>(null);
  const [stopForm, setStopForm] = useState<any | null>(null);
  const [rosterFor, setRosterFor] = useState<Route | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confirm, setConfirm] = useState<ConfirmRequest | null>(null);

  const selected = routes.find((route) => route.id === selectedId) || routes[0] || null;
  const stops = selected ? [...selected.stops].sort((a, b) => a.sequence - b.sequence) : [];

  const vehicleLabel = (id: number | null) => {
    const vehicle = vehicles.find((item) => item.id === id);
    if (!vehicle) return 'No vehicle yet';
    const type = types.find((item) => item.id === vehicle.transport_type_id);
    return `${vehicle.registration_number}${type ? ` · ${type.name}` : ''}`;
  };

  const run = async (call: () => Promise<unknown>, message: string, close: () => void) => {
    setBusy(true);
    setError(null);
    try {
      await call();
      await reload();
      notify(message);
      close();
    } catch (failure) {
      setError(apiError(failure));
    } finally {
      setBusy(false);
    }
  };

  const saveRoute = () => {
    const body = {
      name: routeForm.name.trim(),
      description: routeForm.description.trim() || null,
      vehicle_id: routeForm.vehicle_id === '' ? null : routeForm.vehicle_id,
      is_active: routeForm.is_active,
    };
    return run(
      async () => {
        if (routeForm.id) await transitAPI.updateRoute(routeForm.id, body);
        else setSelectedId((await transitAPI.createRoute(body)).id);
      },
      routeForm.id ? 'Route saved.' : 'Route added. Now add its stops.',
      () => setRouteForm(null)
    );
  };

  const saveStop = () => {
    if (!selected) return;
    const body = {
      name: stopForm.name.trim(),
      distance_km: stopForm.distance_km === '' ? null : Number(stopForm.distance_km).toFixed(2),
      pickup_time: stopForm.pickup_time || null,
      drop_time: stopForm.drop_time || null,
      is_active: stopForm.is_active,
    };
    return run(
      () => (stopForm.id ? transitAPI.updateStop(stopForm.id, body) : transitAPI.addStop(selected.id, body)),
      stopForm.id ? 'Stop saved.' : 'Stop added.',
      () => setStopForm(null)
    );
  };

  const move = async (index: number, by: number) => {
    if (!selected) return;
    const order = stops.map((stop) => stop.id);
    [order[index], order[index + by]] = [order[index + by], order[index]];
    try {
      await transitAPI.reorderStops(selected.id, order);
      await reload();
    } catch (failure) {
      notifyError(failure);
    }
  };

  const openStop = (stop?: Stop) => {
    setError(null);
    setStopForm(
      stop
        ? { id: stop.id, name: stop.name, distance_km: stop.distance_km ? String(Number(stop.distance_km)) : '', pickup_time: time(stop.pickup_time), drop_time: time(stop.drop_time), is_active: stop.is_active }
        : { id: null, name: '', distance_km: '', pickup_time: '', drop_time: '', is_active: true }
    );
  };

  const openRoute = (route?: Route) => {
    setError(null);
    setRouteForm(
      route
        ? { id: route.id, name: route.name, description: route.description || '', vehicle_id: route.vehicle_id ?? '', is_active: route.is_active }
        : { id: null, name: '', description: '', vehicle_id: '', is_active: true }
    );
  };

  return (
    <Box sx={{ display: 'grid', gap: 3, gridTemplateColumns: { xs: '1fr', md: '320px minmax(0, 1fr)' }, alignItems: 'start' }}>
      <Panel
        title="Routes"
        subtitle={`${routes.length} route${routes.length === 1 ? '' : 's'}`}
        actions={
          <Button size="small" variant="contained" startIcon={<AddIcon />} onClick={() => openRoute()}>
            New
          </Button>
        }
      >
        {routes.length === 0 ? (
          <EmptyState title="No routes yet" hint="A route is the path one vehicle drives, stop by stop." icon={<RouteIcon />} />
        ) : (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            {routes.map((route, index) => {
              const active = selected?.id === route.id;
              return (
                <Box
                  key={route.id}
                  component="button"
                  type="button"
                  onClick={() => setSelectedId(route.id)}
                  sx={{
                    p: 1.5,
                    textAlign: 'left',
                    font: 'inherit',
                    cursor: 'pointer',
                    borderRadius: '14px',
                    border: '1px solid',
                    borderColor: active ? alpha(brand.primary, 0.45) : 'rgba(15,23,42,0.07)',
                    background: active ? `linear-gradient(135deg, ${alpha(brand.primary, 0.1)}, ${alpha(brand.violet, 0.06)})` : '#fff',
                    boxShadow: active ? `0 10px 24px ${alpha(brand.primary, 0.18)}` : 'none',
                    opacity: route.is_active ? 1 : 0.6,
                    animation: `fadeUp 0.4s ${ease} both`,
                    animationDelay: `${index * 40}ms`,
                    transition: `all 0.3s ${ease}`,
                    '&:hover': { transform: 'translateX(4px)', borderColor: alpha(brand.primary, 0.35) },
                  }}
                >
                  <Typography sx={{ fontWeight: 700, fontSize: '0.92rem' }}>{route.name}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {route.stops.length} stop{route.stops.length === 1 ? '' : 's'} · {vehicleLabel(route.vehicle_id)}
                    {!route.is_active && ' · not in use'}
                  </Typography>
                </Box>
              );
            })}
          </Box>
        )}
      </Panel>

      {!selected ? (
        <Panel>
          <EmptyState title="Add a route to begin" icon={<RouteIcon />} action={<Button variant="contained" onClick={() => openRoute()}>New route</Button>} />
        </Panel>
      ) : (
        <Panel
          key={selected.id}
          title={selected.name}
          subtitle={selected.description || vehicleLabel(selected.vehicle_id)}
          actions={
            <>
              <Button size="small" variant="outlined" startIcon={<RosterIcon />} onClick={() => setRosterFor(selected)}>
                Riders
              </Button>
              <Tooltip title="Edit route">
                <IconButton size="small" color="primary" onClick={() => openRoute(selected)}>
                  <EditIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Delete route">
                <IconButton
                  size="small"
                  color="error"
                  onClick={() =>
                    setConfirm({
                      title: 'Delete route',
                      message: `Delete "${selected.name}" and its stops? A route students are assigned to cannot be deleted; mark it not in use instead.`,
                      confirmLabel: 'Delete',
                      danger: true,
                      onConfirm: async () => {
                        await transitAPI.deleteRoute(selected.id);
                        setSelectedId(null);
                        await reload();
                        notify('Route deleted.');
                      },
                    })
                  }
                >
                  <DeleteIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Button size="small" variant="contained" startIcon={<AddIcon />} onClick={() => openStop()}>
                Add stop
              </Button>
            </>
          }
        >
          {stops.length === 0 ? (
            <EmptyState title="No stops on this route" hint="Add the stops in the order the vehicle reaches them." icon={<PlaceIcon />} />
          ) : (
            <Box sx={{ position: 'relative', pl: 1 }}>
              {stops.map((stop, index) => (
                <Box key={stop.id} sx={{ position: 'relative', display: 'flex', gap: 2, pb: index === stops.length - 1 ? 0 : 2, animation: `fadeUp 0.4s ${ease} both`, animationDelay: `${index * 50}ms` }}>
                  {/* Line joining the stops */}
                  {index < stops.length - 1 && (
                    <Box sx={{ position: 'absolute', left: 17, top: 36, bottom: 0, width: 2, background: `linear-gradient(180deg, ${brand.primary}, ${alpha(brand.violet, 0.35)})` }} />
                  )}
                  <Box sx={{ zIndex: 1, flexShrink: 0, display: 'grid', placeItems: 'center', width: 36, height: 36, borderRadius: '50%', color: '#fff', fontWeight: 800, fontSize: '0.85rem', background: stop.is_active ? brand.gradient : '#94a3b8', boxShadow: stop.is_active ? '0 6px 16px rgba(37,99,235,0.4)' : 'none' }}>
                    {index + 1}
                  </Box>
                  <Box
                    sx={{
                      flexGrow: 1,
                      minWidth: 0,
                      display: 'flex',
                      alignItems: 'center',
                      gap: 1,
                      flexWrap: 'wrap',
                      p: 1.5,
                      borderRadius: '14px',
                      border: '1px solid rgba(15,23,42,0.07)',
                      background: '#fff',
                      opacity: stop.is_active ? 1 : 0.6,
                      transition: `all 0.3s ${ease}`,
                      '&:hover': { boxShadow: brand.shadowLift, transform: 'translateX(4px)' },
                    }}
                  >
                    <Box sx={{ flexGrow: 1, minWidth: 140 }}>
                      <Typography sx={{ fontWeight: 700, fontSize: '0.92rem' }}>{stop.name}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {[stop.distance_km != null && `${Number(stop.distance_km)} km`, stop.pickup_time && `Pickup ${time(stop.pickup_time)}`, stop.drop_time && `Drop ${time(stop.drop_time)}`, !stop.is_active && 'not in use']
                          .filter(Boolean)
                          .join(' · ') || 'No distance or times set'}
                      </Typography>
                    </Box>
                    <Tooltip title="Earlier">
                      <span>
                        <IconButton size="small" disabled={index === 0} onClick={() => move(index, -1)}>
                          <UpIcon fontSize="small" />
                        </IconButton>
                      </span>
                    </Tooltip>
                    <Tooltip title="Later">
                      <span>
                        <IconButton size="small" disabled={index === stops.length - 1} onClick={() => move(index, 1)}>
                          <DownIcon fontSize="small" />
                        </IconButton>
                      </span>
                    </Tooltip>
                    <Tooltip title="Edit stop">
                      <IconButton size="small" color="primary" onClick={() => openStop(stop)}>
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete stop">
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() =>
                          setConfirm({
                            title: 'Delete stop',
                            message: `Delete the stop "${stop.name}"? A stop students ride from cannot be deleted; mark it not in use instead.`,
                            confirmLabel: 'Delete',
                            danger: true,
                            onConfirm: async () => {
                              await transitAPI.deleteStop(stop.id);
                              await reload();
                              notify('Stop deleted.');
                            },
                          })
                        }
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </Box>
              ))}
            </Box>
          )}
        </Panel>
      )}

      <FormDialog open={Boolean(routeForm)} title={routeForm?.id ? 'Edit route' : 'New route'} onClose={() => setRouteForm(null)} onSubmit={saveRoute} busy={busy} disabled={!routeForm?.name.trim()} error={error}>
        {routeForm && (
          <>
            <TextField label="Route name" value={routeForm.name} onChange={(event) => setRouteForm({ ...routeForm, name: event.target.value })} required autoFocus slotProps={{ htmlInput: { maxLength: 100 } }} />
            <TextField label="Description" value={routeForm.description} onChange={(event) => setRouteForm({ ...routeForm, description: event.target.value })} />
            <FieldRow>
              <TextField select label="Vehicle" value={routeForm.vehicle_id} onChange={(event) => setRouteForm({ ...routeForm, vehicle_id: event.target.value === '' ? '' : Number(event.target.value) })} slotProps={{ select: { displayEmpty: true }, inputLabel: { shrink: true } }}>
                <MenuItem value="">No vehicle yet</MenuItem>
                {vehicles
                  .filter((vehicle) => vehicle.is_active || vehicle.id === routeForm.vehicle_id)
                  .map((vehicle) => (
                    <MenuItem key={vehicle.id} value={vehicle.id}>
                      {vehicleLabel(vehicle.id)}
                    </MenuItem>
                  ))}
              </TextField>
              <FormControlLabel control={<Switch checked={routeForm.is_active} onChange={(event) => setRouteForm({ ...routeForm, is_active: event.target.checked })} />} label="In use" />
            </FieldRow>
          </>
        )}
      </FormDialog>

      <FormDialog open={Boolean(stopForm)} title={stopForm?.id ? 'Edit stop' : 'Add stop'} subtitle={selected?.name} onClose={() => setStopForm(null)} onSubmit={saveStop} busy={busy} disabled={!stopForm?.name.trim()} error={error}>
        {stopForm && (
          <>
            <FieldRow>
              <TextField label="Stop name" value={stopForm.name} onChange={(event) => setStopForm({ ...stopForm, name: event.target.value })} required autoFocus slotProps={{ htmlInput: { maxLength: 100 } }} />
              <TextField
                label="Distance from school"
                type="number"
                value={stopForm.distance_km}
                onChange={(event) => setStopForm({ ...stopForm, distance_km: event.target.value })}
                helperText="Used for distance-based rates"
                slotProps={{ htmlInput: { min: 0, step: 0.1 }, input: { endAdornment: <InputAdornment position="end">km</InputAdornment> } }}
              />
            </FieldRow>
            <FieldRow>
              <TextField label="Pickup time" type="time" value={stopForm.pickup_time} onChange={(event) => setStopForm({ ...stopForm, pickup_time: event.target.value })} slotProps={{ inputLabel: { shrink: true } }} />
              <TextField label="Drop time" type="time" value={stopForm.drop_time} onChange={(event) => setStopForm({ ...stopForm, drop_time: event.target.value })} slotProps={{ inputLabel: { shrink: true } }} />
            </FieldRow>
            <FormControlLabel control={<Switch checked={stopForm.is_active} onChange={(event) => setStopForm({ ...stopForm, is_active: event.target.checked })} />} label="In use" />
          </>
        )}
      </FormDialog>

      <RosterDialog route={rosterFor} onClose={() => setRosterFor(null)} />
      <ConfirmDialog request={confirm} onClose={() => setConfirm(null)} />
      {node}
    </Box>
  );
};

export default RoutesTab;
