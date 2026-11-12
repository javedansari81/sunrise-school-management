/** Fee heads: the kinds of charge a school bills (tuition, exam, transport, ...). */
import React, { useEffect, useState } from 'react';
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
import { Add as AddIcon, Category as CategoryIcon, Delete as DeleteIcon, Edit as EditIcon, Lock as LockIcon } from '@mui/icons-material';
import { billingAPI, FeeHead, FREQUENCIES, frequencyLabel, HEAD_CATEGORIES } from '../../services/billingService';
import { apiError, ConfirmDialog, ConfirmRequest, EmptyState, FieldRow, FormDialog, Panel, StatusChip, useNotify } from '../ui';

interface Props {
  heads: FeeHead[];
  reload: () => Promise<void>;
}

const blank = { code: '', name: '', description: '', category: 'ACADEMIC', default_frequency: 'MONTHLY', sort_order: 0, is_active: true };

const FeeHeadsTab: React.FC<Props> = ({ heads, reload }) => {
  const { notify, notifyError, node } = useNotify();
  const [editing, setEditing] = useState<FeeHead | 'new' | null>(null);
  const [form, setForm] = useState<any>(blank);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confirm, setConfirm] = useState<ConfirmRequest | null>(null);

  useEffect(() => {
    if (!editing) return;
    setError(null);
    setForm(editing === 'new' ? { ...blank, sort_order: (heads.length + 1) * 10 } : { ...editing, description: editing.description || '' });
  }, [editing, heads.length]);

  const set = (field: string) => (event: React.ChangeEvent<HTMLInputElement>) => setForm((current: any) => ({ ...current, [field]: event.target.value }));
  const system = editing !== 'new' && Boolean(editing?.is_system);

  const save = async () => {
    setBusy(true);
    setError(null);
    const body = {
      code: form.code.trim().toUpperCase(),
      name: form.name.trim(),
      description: form.description.trim() || null,
      category: form.category,
      default_frequency: form.default_frequency,
      sort_order: Number(form.sort_order) || 0,
      is_active: form.is_active,
    };
    try {
      if (editing === 'new') await billingAPI.createHead(body);
      else if (editing) await billingAPI.updateHead(editing.id, system ? { name: body.name, description: body.description, sort_order: body.sort_order } : body);
      await reload();
      notify(editing === 'new' ? 'Fee head added.' : 'Fee head saved.');
      setEditing(null);
    } catch (failure) {
      setError(apiError(failure));
    } finally {
      setBusy(false);
    }
  };

  const toggleActive = async (head: FeeHead) => {
    try {
      await billingAPI.updateHead(head.id, { is_active: !head.is_active });
      await reload();
    } catch (failure) {
      notifyError(failure);
    }
  };

  return (
    <Panel
      title="Fee heads"
      subtitle="Every kind of charge. Prices are set per head in a fee structure."
      padded={false}
      actions={
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => setEditing('new')}>
          New fee head
        </Button>
      }
    >
      {heads.length === 0 ? (
        <EmptyState title="No fee heads yet" hint="Add Tuition first, then exam, admission and other charges." icon={<CategoryIcon />} />
      ) : (
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Code</TableCell>
                <TableCell>Category</TableCell>
                <TableCell>Usually billed</TableCell>
                <TableCell>Active</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {heads.map((head) => (
                <TableRow key={head.id} hover sx={{ opacity: head.is_active ? 1 : 0.55 }}>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography sx={{ fontWeight: 600, fontSize: '0.9rem' }}>{head.name}</Typography>
                      {head.is_system && (
                        <Tooltip title="Used by the system (transport billing or late fees). It cannot be deleted.">
                          <LockIcon sx={{ fontSize: 15, color: 'text.secondary' }} />
                        </Tooltip>
                      )}
                    </Box>
                    {head.description && (
                      <Typography variant="caption" color="text.secondary">
                        {head.description}
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>{head.code}</TableCell>
                  <TableCell>
                    <StatusChip status="PENDING" label={HEAD_CATEGORIES.find((item) => item.value === head.category)?.label || head.category} />
                  </TableCell>
                  <TableCell>{frequencyLabel(head.default_frequency)}</TableCell>
                  <TableCell>
                    <Switch size="small" checked={head.is_active} onChange={() => toggleActive(head)} disabled={head.is_system} slotProps={{ input: { 'aria-label': `${head.name} active` } }} />
                  </TableCell>
                  <TableCell align="right" sx={{ whiteSpace: 'nowrap' }}>
                    <Tooltip title="Edit">
                      <IconButton size="small" color="primary" onClick={() => setEditing(head)}>
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    {!head.is_system && (
                      <Tooltip title="Delete">
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() =>
                            setConfirm({
                              title: 'Delete fee head',
                              message: `Delete "${head.name}"? A head that is already priced or billed cannot be deleted; switch it off instead.`,
                              confirmLabel: 'Delete',
                              danger: true,
                              onConfirm: async () => {
                                await billingAPI.deleteHead(head.id);
                                await reload();
                                notify('Fee head deleted.');
                              },
                            })
                          }
                        >
                          <DeleteIcon fontSize="small" />
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

      <FormDialog
        open={Boolean(editing)}
        title={editing === 'new' ? 'New fee head' : 'Edit fee head'}
        onClose={() => setEditing(null)}
        onSubmit={save}
        busy={busy}
        disabled={!form.name?.trim() || !/^[A-Za-z0-9_]+$/.test(form.code || '')}
        error={error}
      >
        <FieldRow>
          <TextField label="Name" value={form.name} onChange={set('name')} required autoFocus slotProps={{ htmlInput: { maxLength: 100 } }} />
          <TextField
            label="Code"
            value={form.code}
            onChange={(event) => setForm((current: any) => ({ ...current, code: event.target.value.toUpperCase().replace(/[^A-Z0-9_]/g, '_') }))}
            required
            disabled={system}
            helperText="Capital letters, digits and _ (for example EXAM)"
            slotProps={{ htmlInput: { maxLength: 30 } }}
          />
        </FieldRow>
        <FieldRow>
          <TextField select label="Category" value={form.category} onChange={set('category')} disabled={system}>
            {HEAD_CATEGORIES.map((item) => (
              <MenuItem key={item.value} value={item.value}>
                {item.label}
              </MenuItem>
            ))}
          </TextField>
          <TextField select label="Usually billed" value={form.default_frequency} onChange={set('default_frequency')} disabled={system}>
            {FREQUENCIES.map((item) => (
              <MenuItem key={item.value} value={item.value}>
                {item.label}
              </MenuItem>
            ))}
          </TextField>
        </FieldRow>
        <TextField label="Description" value={form.description} onChange={set('description')} multiline minRows={2} />
        <FieldRow>
          <TextField label="Order in lists" type="number" value={form.sort_order} onChange={set('sort_order')} />
          <FormControlLabel
            control={<Switch checked={Boolean(form.is_active)} onChange={(event) => setForm((current: any) => ({ ...current, is_active: event.target.checked }))} disabled={system} />}
            label="Active"
          />
        </FieldRow>
      </FormDialog>
      <ConfirmDialog request={confirm} onClose={() => setConfirm(null)} />
      {node}
    </Panel>
  );
};

export default FeeHeadsTab;
