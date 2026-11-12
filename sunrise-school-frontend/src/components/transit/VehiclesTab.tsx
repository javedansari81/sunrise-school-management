/** Vehicles the school runs, and the kinds of vehicle (bus, van, ...) rates are set for. */
import React, { useState } from 'react';
import {
  Box,
  Button,
  FormControlLabel,
  IconButton,
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
import { Add as AddIcon, AirportShuttle as TypeIcon, Delete as DeleteIcon, DirectionsBus as BusIcon, Edit as EditIcon } from '@mui/icons-material';
import { Route, transitAPI, TransportType, Vehicle } from '../../services/transitService';
import { apiError, ConfirmDialog, ConfirmRequest, EmptyState, FieldRow, FormDialog, Panel, StatusChip, useNotify } from '../ui';

interface Props {
  types: TransportType[];
  vehicles: Vehicle[];
  routes: Route[];
  reload: () => Promise<void>;
}

const VehiclesTab: React.FC<Props> = ({ types, vehicles, routes, reload }) => {
  const { notify, node } = useNotify();
  const [vehicleForm, setVehicleForm] = useState<any | null>(null);
  const [typeForm, setTypeForm] = useState<any | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confirm, setConfirm] = useState<ConfirmRequest | null>(null);

  const typeName = (id: number) => types.find((item) => item.id === id)?.name || '—';
  const routesOf = (vehicleId: number) => routes.filter((route) => route.vehicle_id === vehicleId).map((route) => route.name);

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

  const openVehicle = (vehicle?: Vehicle) => {
    setError(null);
    setVehicleForm(
      vehicle
        ? { ...vehicle, capacity: vehicle.capacity ?? '', driver_name: vehicle.driver_name || '', driver_phone: vehicle.driver_phone || '', remarks: vehicle.remarks || '' }
        : { id: null, transport_type_id: types.find((item) => item.is_active)?.id ?? '', registration_number: '', capacity: '', driver_name: '', driver_phone: '', remarks: '', is_active: true }
    );
  };

  const openType = (type?: TransportType) => {
    setError(null);
    setTypeForm(
      type
        ? { ...type, capacity: type.capacity ?? '', description: type.description || '' }
        : { id: null, name: '', description: '', capacity: '', sort_order: (types.length + 1) * 10, is_active: true }
    );
  };

  const saveVehicle = () => {
    const body = {
      transport_type_id: vehicleForm.transport_type_id,
      registration_number: vehicleForm.registration_number.trim().toUpperCase(),
      capacity: vehicleForm.capacity === '' ? null : Number(vehicleForm.capacity),
      driver_name: vehicleForm.driver_name.trim() || null,
      driver_phone: vehicleForm.driver_phone.trim() || null,
      remarks: vehicleForm.remarks.trim() || null,
      is_active: vehicleForm.is_active,
    };
    return run(() => (vehicleForm.id ? transitAPI.updateVehicle(vehicleForm.id, body) : transitAPI.createVehicle(body)), 'Vehicle saved.', () => setVehicleForm(null));
  };

  const saveType = () => {
    const body = {
      name: typeForm.name.trim(),
      description: typeForm.description.trim() || null,
      capacity: typeForm.capacity === '' ? null : Number(typeForm.capacity),
      sort_order: Number(typeForm.sort_order) || 0,
      is_active: typeForm.is_active,
    };
    return run(() => (typeForm.id ? transitAPI.updateType(typeForm.id, body) : transitAPI.createType(body)), 'Vehicle type saved.', () => setTypeForm(null));
  };

  const remove = (title: string, message: string, call: () => Promise<unknown>) =>
    setConfirm({
      title,
      message,
      confirmLabel: 'Delete',
      danger: true,
      onConfirm: async () => {
        await call();
        await reload();
        notify('Deleted.');
      },
    });

  return (
    <Box sx={{ display: 'grid', gap: 3, gridTemplateColumns: { xs: '1fr', lg: 'minmax(0, 1.7fr) minmax(0, 1fr)' }, alignItems: 'start' }}>
      <Panel
        title="Vehicles"
        subtitle={`${vehicles.filter((vehicle) => vehicle.is_active).length} in use`}
        padded={false}
        actions={
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => openVehicle()} disabled={types.length === 0}>
            New vehicle
          </Button>
        }
      >
        {vehicles.length === 0 ? (
          <EmptyState title="No vehicles yet" hint={types.length === 0 ? 'Add a vehicle type first.' : 'Add each bus, van or rickshaw with its driver.'} icon={<BusIcon />} />
        ) : (
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Vehicle</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell align="right">Seats</TableCell>
                  <TableCell>Driver</TableCell>
                  <TableCell>Routes</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {vehicles.map((vehicle) => (
                  <TableRow key={vehicle.id} hover sx={{ opacity: vehicle.is_active ? 1 : 0.6 }}>
                    <TableCell sx={{ fontWeight: 700, fontFamily: 'monospace' }}>{vehicle.registration_number}</TableCell>
                    <TableCell>{typeName(vehicle.transport_type_id)}</TableCell>
                    <TableCell align="right">{vehicle.capacity ?? types.find((item) => item.id === vehicle.transport_type_id)?.capacity ?? '—'}</TableCell>
                    <TableCell>
                      {vehicle.driver_name || '—'}
                      {vehicle.driver_phone && (
                        <Typography variant="caption" color="text.secondary" component="div">
                          {vehicle.driver_phone}
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>{routesOf(vehicle.id).join(', ') || '—'}</TableCell>
                    <TableCell>
                      <StatusChip status={vehicle.is_active ? 'ACTIVE' : 'INACTIVE'} label={vehicle.is_active ? 'In use' : 'Not in use'} />
                    </TableCell>
                    <TableCell align="right" sx={{ whiteSpace: 'nowrap' }}>
                      <Tooltip title="Edit">
                        <IconButton size="small" color="primary" onClick={() => openVehicle(vehicle)}>
                          <EditIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete">
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => remove('Delete vehicle', `Delete vehicle ${vehicle.registration_number}? A vehicle that serves a route cannot be deleted; mark it not in use instead.`, () => transitAPI.deleteVehicle(vehicle.id))}
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
      </Panel>

      <Panel
        title="Vehicle types"
        subtitle="Rates are set per type"
        padded={false}
        actions={
          <Button variant="outlined" startIcon={<AddIcon />} onClick={() => openType()}>
            New type
          </Button>
        }
      >
        {types.length === 0 ? (
          <EmptyState title="No vehicle types" hint="For example Bus, Van, E-Rickshaw." icon={<TypeIcon />} />
        ) : (
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Type</TableCell>
                  <TableCell align="right">Usual seats</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {types.map((type) => (
                  <TableRow key={type.id} hover sx={{ opacity: type.is_active ? 1 : 0.6 }}>
                    <TableCell>
                      <Typography sx={{ fontWeight: 600, fontSize: '0.875rem' }}>{type.name}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {[type.description, !type.is_active && 'not in use'].filter(Boolean).join(' · ')}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">{type.capacity ?? '—'}</TableCell>
                    <TableCell align="right" sx={{ whiteSpace: 'nowrap' }}>
                      <Tooltip title="Edit">
                        <IconButton size="small" color="primary" onClick={() => openType(type)}>
                          <EditIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete">
                        <IconButton size="small" color="error" onClick={() => remove('Delete vehicle type', `Delete "${type.name}"? A type with vehicles, rates or riders cannot be deleted; mark it not in use instead.`, () => transitAPI.deleteType(type.id))}>
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
      </Panel>

      <FormDialog
        open={Boolean(vehicleForm)}
        title={vehicleForm?.id ? 'Edit vehicle' : 'New vehicle'}
        onClose={() => setVehicleForm(null)}
        onSubmit={saveVehicle}
        busy={busy}
        disabled={!vehicleForm?.registration_number.trim() || vehicleForm?.transport_type_id === ''}
        error={error}
      >
        {vehicleForm && (
          <>
            <FieldRow>
              <TextField label="Registration number" value={vehicleForm.registration_number} onChange={(event) => setVehicleForm({ ...vehicleForm, registration_number: event.target.value })} required autoFocus slotProps={{ htmlInput: { maxLength: 30 } }} />
              <TextField select label="Type" value={vehicleForm.transport_type_id} onChange={(event) => setVehicleForm({ ...vehicleForm, transport_type_id: Number(event.target.value) })} required>
                {types
                  .filter((item) => item.is_active || item.id === vehicleForm.transport_type_id)
                  .map((item) => (
                    <MenuItem key={item.id} value={item.id}>
                      {item.name}
                    </MenuItem>
                  ))}
              </TextField>
            </FieldRow>
            <FieldRow columns={3}>
              <TextField label="Seats" type="number" value={vehicleForm.capacity} onChange={(event) => setVehicleForm({ ...vehicleForm, capacity: event.target.value })} helperText="Empty: the type’s usual seats" slotProps={{ htmlInput: { min: 1 } }} />
              <TextField label="Driver name" value={vehicleForm.driver_name} onChange={(event) => setVehicleForm({ ...vehicleForm, driver_name: event.target.value })} slotProps={{ htmlInput: { maxLength: 100 } }} />
              <TextField label="Driver phone" value={vehicleForm.driver_phone} onChange={(event) => setVehicleForm({ ...vehicleForm, driver_phone: event.target.value })} slotProps={{ htmlInput: { maxLength: 20 } }} />
            </FieldRow>
            <TextField label="Remarks" value={vehicleForm.remarks} onChange={(event) => setVehicleForm({ ...vehicleForm, remarks: event.target.value })} />
            <FormControlLabel control={<Switch checked={vehicleForm.is_active} onChange={(event) => setVehicleForm({ ...vehicleForm, is_active: event.target.checked })} />} label="In use" />
          </>
        )}
      </FormDialog>

      <FormDialog open={Boolean(typeForm)} title={typeForm?.id ? 'Edit vehicle type' : 'New vehicle type'} onClose={() => setTypeForm(null)} onSubmit={saveType} busy={busy} disabled={!typeForm?.name.trim()} error={error} maxWidth="xs">
        {typeForm && (
          <>
            <TextField label="Name" value={typeForm.name} onChange={(event) => setTypeForm({ ...typeForm, name: event.target.value })} required autoFocus slotProps={{ htmlInput: { maxLength: 50 } }} />
            <TextField label="Description" value={typeForm.description} onChange={(event) => setTypeForm({ ...typeForm, description: event.target.value })} />
            <TextField label="Usual seats" type="number" value={typeForm.capacity} onChange={(event) => setTypeForm({ ...typeForm, capacity: event.target.value })} slotProps={{ htmlInput: { min: 1 } }} />
            <FormControlLabel control={<Switch checked={typeForm.is_active} onChange={(event) => setTypeForm({ ...typeForm, is_active: event.target.checked })} />} label="In use" />
          </>
        )}
      </FormDialog>
      <ConfirmDialog request={confirm} onClose={() => setConfirm(null)} />
      {node}
    </Box>
  );
};

export default VehiclesTab;
