/**
 * Fee structures: a session's price list. A draft is edited as one grid,
 * published when ready (the previous one is archived), and copied to start
 * next year's.
 */
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
import { alpha } from '@mui/material/styles';
import {
  Add as AddIcon,
  Archive as ArchiveIcon,
  ContentCopy as CopyIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  ListAlt as ListAltIcon,
  Publish as PublishIcon,
  Visibility as ViewIcon,
} from '@mui/icons-material';
import {
  APPLIES_TO,
  billingAPI,
  FeeHead,
  FeeStructure,
  FeeStructureSummary,
  FREQUENCIES,
  StructureItem,
} from '../../services/billingService';
import { Lookups } from '../../hooks/useLookups';
import { apiError, ConfirmDialog, ConfirmRequest, EmptyState, FieldRow, FormDialog, formatDate, Loading, Panel, StatusChip, useNotify } from '../ui';
import { brand, ease } from '../../theme';

interface Props {
  lookups: Lookups;
  heads: FeeHead[];
}

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

interface Row extends Omit<StructureItem, 'class_id'> {
  key: number;
  class_id: number | '';
}

let nextKey = 1;
const toRow = (item: StructureItem): Row => ({ ...item, key: nextKey++, class_id: item.class_id ?? '', amount: String(Number(item.amount)) });

// ---------------------------------------------------------------------------
// Editor
// ---------------------------------------------------------------------------

interface EditorProps {
  target: { id: number | null; sessionYearId: number } | null;
  lookups: Lookups;
  heads: FeeHead[];
  onClose: () => void;
  onSaved: () => void;
}

const StructureEditor: React.FC<EditorProps> = ({ target, lookups, heads, onClose, onSaved }) => {
  const [structure, setStructure] = useState<FeeStructure | null>(null);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [rows, setRows] = useState<Row[]>([]);
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const usableHeads = heads.filter((head) => head.category !== 'TRANSPORT' && head.category !== 'PENALTY');
  const readOnly = Boolean(structure && structure.status !== 'DRAFT');

  useEffect(() => {
    if (!target) return;
    setError(null);
    setStructure(null);
    if (target.id == null) {
      setName(`Fee structure ${lookups.sessionName(target.sessionYearId)}`.trim());
      setDescription('');
      setRows([]);
      return;
    }
    setLoading(true);
    billingAPI
      .getStructure(target.id)
      .then((loaded) => {
        setStructure(loaded);
        setName(loaded.name);
        setDescription(loaded.description || '');
        setRows(loaded.items.map(toRow));
      })
      .catch((failure) => setError(apiError(failure)))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [target]);

  const update = (key: number, patch: Partial<Row>) => setRows((current) => current.map((row) => (row.key === key ? { ...row, ...patch } : row)));

  const addRow = () => {
    const head = usableHeads.find((item) => item.is_active);
    if (!head) return;
    setRows((current) => [
      ...current,
      { key: nextKey++, fee_head_id: head.id, class_id: '', amount: '', frequency: head.default_frequency, billing_months: null, due_day: 10, applies_to: 'ALL' },
    ]);
  };

  /** One row per class for a head, ready for the amounts to be typed in. */
  const addForEveryClass = () => {
    const head = usableHeads.find((item) => item.code === 'TUITION' && item.is_active) || usableHeads.find((item) => item.is_active);
    if (!head) return;
    const taken = new Set(rows.filter((row) => row.fee_head_id === head.id).map((row) => row.class_id));
    setRows((current) => [
      ...current,
      ...lookups.classes
        .filter((item) => !taken.has(item.id))
        .map((item): Row => ({ key: nextKey++, fee_head_id: head.id, class_id: item.id, amount: '', frequency: head.default_frequency, billing_months: null, due_day: 10, applies_to: 'ALL' })),
    ]);
  };

  const save = async () => {
    if (!target) return;
    const incomplete = rows.findIndex((row) => row.amount === '' || Number(row.amount) < 0);
    if (incomplete >= 0) {
      setError(`Row ${incomplete + 1} needs an amount.`);
      return;
    }
    const items: StructureItem[] = rows.map((row) => ({
      fee_head_id: row.fee_head_id,
      class_id: row.class_id === '' ? null : row.class_id,
      amount: Number(row.amount).toFixed(2),
      frequency: row.frequency,
      billing_months: row.billing_months && row.billing_months.length ? row.billing_months : null,
      due_day: Number(row.due_day) || 10,
      applies_to: row.applies_to,
    }));
    setBusy(true);
    setError(null);
    try {
      if (target.id == null) {
        await billingAPI.createStructure({ session_year_id: target.sessionYearId, name: name.trim(), description: description.trim() || null, items });
      } else {
        await billingAPI.updateStructure(target.id, { name: name.trim(), description: description.trim() || null });
        await billingAPI.replaceItems(target.id, items);
      }
      onSaved();
      onClose();
    } catch (failure) {
      setError(apiError(failure));
    } finally {
      setBusy(false);
    }
  };

  const cellField = { size: 'small' as const, variant: 'outlined' as const, fullWidth: true };

  return (
    <FormDialog
      open={Boolean(target)}
      title={target?.id == null ? 'New fee structure' : readOnly ? 'Fee structure' : 'Edit fee structure'}
      subtitle={target ? `Session ${lookups.sessionName(target.sessionYearId)}` : undefined}
      onClose={onClose}
      onSubmit={readOnly ? undefined : save}
      submitLabel="Save draft"
      busy={busy}
      disabled={!name.trim() || loading}
      error={error}
      maxWidth="lg"
    >
      {loading ? (
        <Loading />
      ) : (
        <>
          {readOnly && (
            <Alert severity="info">
              This structure is {structure?.status.toLowerCase()}, so it cannot be changed. Copy it into a new draft to make changes.
            </Alert>
          )}
          <FieldRow>
            <TextField label="Name" value={name} onChange={(event) => setName(event.target.value)} required disabled={readOnly} slotProps={{ htmlInput: { maxLength: 150 } }} />
            <TextField label="Description" value={description} onChange={(event) => setDescription(event.target.value)} disabled={readOnly} />
          </FieldRow>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
            <Typography sx={{ fontWeight: 700, flexGrow: 1 }}>
              Prices <Typography component="span" color="text.secondary">({rows.length})</Typography>
            </Typography>
            {!readOnly && (
              <>
                <Button size="small" variant="outlined" onClick={addForEveryClass}>
                  Add tuition for every class
                </Button>
                <Button size="small" variant="contained" startIcon={<AddIcon />} onClick={addRow}>
                  Add price
                </Button>
              </>
            )}
          </Box>

          {rows.length === 0 ? (
            <EmptyState title="No prices yet" hint="Add one price per fee head. Leave the class as All classes when every class pays the same." icon={<ListAltIcon />} />
          ) : (
            <TableContainer sx={{ border: '1px solid rgba(15,23,42,0.08)', borderRadius: '14px', maxHeight: '52vh' }}>
              <Table size="small" stickyHeader sx={{ minWidth: 980 }}>
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ minWidth: 170 }}>Fee head</TableCell>
                    <TableCell sx={{ minWidth: 150 }}>Class</TableCell>
                    <TableCell sx={{ minWidth: 130 }}>Amount</TableCell>
                    <TableCell sx={{ minWidth: 140 }}>How often</TableCell>
                    <TableCell sx={{ minWidth: 170 }}>Billed in</TableCell>
                    <TableCell sx={{ width: 90 }}>Due day</TableCell>
                    <TableCell sx={{ minWidth: 160 }}>Who pays</TableCell>
                    <TableCell />
                  </TableRow>
                </TableHead>
                <TableBody>
                  {rows.map((row) => {
                    const single = row.frequency === 'ANNUAL' || row.frequency === 'ONE_TIME';
                    return (
                      <TableRow key={row.key} sx={{ animation: `fadeUp 0.3s ${ease} both`, '& td': { py: 0.75 } }}>
                        <TableCell>
                          <TextField
                            {...cellField}
                            select
                            value={row.fee_head_id}
                            disabled={readOnly}
                            onChange={(event) => {
                              const head = heads.find((item) => item.id === Number(event.target.value));
                              update(row.key, { fee_head_id: Number(event.target.value), frequency: head?.default_frequency || row.frequency, billing_months: null });
                            }}
                          >
                            {usableHeads
                              .filter((head) => head.is_active || head.id === row.fee_head_id)
                              .map((head) => (
                                <MenuItem key={head.id} value={head.id}>
                                  {head.name}
                                </MenuItem>
                              ))}
                          </TextField>
                        </TableCell>
                        <TableCell>
                          <TextField
                            {...cellField}
                            select
                            value={row.class_id}
                            disabled={readOnly}
                            onChange={(event) => update(row.key, { class_id: event.target.value === '' ? '' : Number(event.target.value) })}
                            slotProps={{ select: { displayEmpty: true } }}
                          >
                            <MenuItem value="">All classes</MenuItem>
                            {lookups.classes.map((item) => (
                              <MenuItem key={item.id} value={item.id}>
                                {item.description || item.name}
                              </MenuItem>
                            ))}
                          </TextField>
                        </TableCell>
                        <TableCell>
                          <TextField
                            {...cellField}
                            type="number"
                            value={row.amount}
                            disabled={readOnly}
                            onChange={(event) => update(row.key, { amount: event.target.value })}
                            slotProps={{ htmlInput: { min: 0, step: 0.01, 'aria-label': 'Amount' }, input: { startAdornment: <InputAdornment position="start">₹</InputAdornment> } }}
                          />
                        </TableCell>
                        <TableCell>
                          <TextField
                            {...cellField}
                            select
                            value={row.frequency}
                            disabled={readOnly}
                            onChange={(event) => update(row.key, { frequency: event.target.value as Row['frequency'], billing_months: null })}
                          >
                            {FREQUENCIES.map((item) => (
                              <MenuItem key={item.value} value={item.value}>
                                {item.label}
                              </MenuItem>
                            ))}
                          </TextField>
                        </TableCell>
                        <TableCell>
                          {row.frequency === 'MONTHLY' ? (
                            <Typography variant="body2" color="text.secondary">
                              Every month
                            </Typography>
                          ) : (
                            <TextField
                              {...cellField}
                              select
                              disabled={readOnly}
                              value={single ? row.billing_months?.[0] ?? '' : row.billing_months || []}
                              onChange={(event) => {
                                const value = event.target.value as unknown;
                                const months = single ? (value === '' ? null : [Number(value)]) : (value as number[]);
                                update(row.key, { billing_months: months && months.length ? months : null });
                              }}
                              slotProps={{
                                select: {
                                  multiple: !single,
                                  displayEmpty: true,
                                  renderValue: (value: unknown) => {
                                    const list = Array.isArray(value) ? value : value === '' ? [] : [value];
                                    return list.length ? list.map((month) => MONTHS[Number(month) - 1]).join(', ') : 'Default months';
                                  },
                                },
                              }}
                            >
                              {single && <MenuItem value="">Default (first month)</MenuItem>}
                              {MONTHS.map((month, index) => (
                                <MenuItem key={month} value={index + 1}>
                                  {month}
                                </MenuItem>
                              ))}
                            </TextField>
                          )}
                        </TableCell>
                        <TableCell>
                          <TextField
                            {...cellField}
                            type="number"
                            value={row.due_day}
                            disabled={readOnly}
                            onChange={(event) => update(row.key, { due_day: Math.min(28, Math.max(1, Number(event.target.value) || 1)) })}
                            slotProps={{ htmlInput: { min: 1, max: 28, 'aria-label': 'Due day of the month' } }}
                          />
                        </TableCell>
                        <TableCell>
                          <TextField {...cellField} select value={row.applies_to} disabled={readOnly} onChange={(event) => update(row.key, { applies_to: event.target.value as Row['applies_to'] })}>
                            {APPLIES_TO.map((item) => (
                              <MenuItem key={item.value} value={item.value}>
                                {item.label}
                              </MenuItem>
                            ))}
                          </TextField>
                        </TableCell>
                        <TableCell align="right">
                          {!readOnly && (
                            <Tooltip title="Remove">
                              <IconButton size="small" color="error" onClick={() => setRows((current) => current.filter((item) => item.key !== row.key))}>
                                <DeleteIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          )}
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </>
      )}
    </FormDialog>
  );
};

// ---------------------------------------------------------------------------
// List
// ---------------------------------------------------------------------------

const FeeStructuresTab: React.FC<Props> = ({ lookups, heads }) => {
  const { notify, notifyError, node } = useNotify();
  const [sessionId, setSessionId] = useState<number | null>(lookups.currentSessionId);
  const [structures, setStructures] = useState<FeeStructureSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [editor, setEditor] = useState<{ id: number | null; sessionYearId: number } | null>(null);
  const [copying, setCopying] = useState<FeeStructureSummary | null>(null);
  const [copyTo, setCopyTo] = useState<number | ''>('');
  const [copyBusy, setCopyBusy] = useState(false);
  const [copyError, setCopyError] = useState<string | null>(null);
  const [confirm, setConfirm] = useState<ConfirmRequest | null>(null);

  const load = useCallback(async () => {
    if (sessionId == null) return;
    setLoading(true);
    try {
      setStructures(await billingAPI.listStructures(sessionId));
    } catch (failure) {
      notifyError(failure);
    } finally {
      setLoading(false);
    }
  }, [sessionId, notifyError]);

  useEffect(() => {
    load();
  }, [load]);

  const order = { PUBLISHED: 0, DRAFT: 1, ARCHIVED: 2 };
  const sorted = [...structures].sort((a, b) => order[a.status] - order[b.status] || b.id - a.id);

  const copy = async () => {
    if (!copying || !copyTo) return;
    setCopyBusy(true);
    setCopyError(null);
    try {
      await billingAPI.copyStructure(copying.id, { session_year_id: copyTo });
      notify(`Copied into a new draft for ${lookups.sessionName(copyTo)}.`);
      setCopying(null);
      if (copyTo === sessionId) load();
      else setSessionId(copyTo);
    } catch (failure) {
      setCopyError(apiError(failure));
    } finally {
      setCopyBusy(false);
    }
  };

  return (
    <Panel
      title="Fee structures"
      subtitle="The published structure is the one students are billed from."
      actions={
        <>
          <TextField select size="small" label="Session" value={sessionId ?? ''} onChange={(event) => setSessionId(Number(event.target.value))} sx={{ minWidth: 130 }}>
            {lookups.sessionYears.map((year) => (
              <MenuItem key={year.id} value={year.id}>
                {year.name}
              </MenuItem>
            ))}
          </TextField>
          <Button variant="contained" startIcon={<AddIcon />} disabled={sessionId == null} onClick={() => sessionId != null && setEditor({ id: null, sessionYearId: sessionId })}>
            New structure
          </Button>
        </>
      }
    >
      {loading ? (
        <Loading />
      ) : sorted.length === 0 ? (
        <EmptyState title="No fee structure for this session" hint="Create one, or copy last year's from the previous session." icon={<ListAltIcon />} />
      ) : (
        <Box sx={{ display: 'grid', gap: 2, gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))' }}>
          {sorted.map((structure, index) => {
            const published = structure.status === 'PUBLISHED';
            const draft = structure.status === 'DRAFT';
            return (
              <Box
                key={structure.id}
                sx={{
                  position: 'relative',
                  overflow: 'hidden',
                  p: 2.25,
                  borderRadius: '18px',
                  border: '1px solid',
                  borderColor: published ? alpha('#16a34a', 0.35) : 'rgba(15,23,42,0.08)',
                  background: published ? 'linear-gradient(160deg, rgba(22,163,74,0.07), #fff 55%)' : '#fff',
                  animation: `fadeUp 0.45s ${ease} both`,
                  animationDelay: `${index * 50}ms`,
                  transition: `transform 0.35s ${ease}, box-shadow 0.35s ${ease}`,
                  opacity: structure.status === 'ARCHIVED' ? 0.75 : 1,
                  '&:hover': { transform: 'translateY(-4px)', boxShadow: brand.shadowLift, opacity: 1 },
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                  <Box sx={{ flexGrow: 1, minWidth: 0 }}>
                    <Typography sx={{ fontWeight: 700 }} noWrap title={structure.name}>
                      {structure.name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {published ? `Published ${formatDate(structure.published_at)}` : `Created ${formatDate(structure.created_at)}`}
                    </Typography>
                  </Box>
                  <StatusChip status={structure.status} />
                </Box>
                {structure.description && (
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    {structure.description}
                  </Typography>
                )}
                <Box sx={{ display: 'flex', gap: 0.5, mt: 2, flexWrap: 'wrap', alignItems: 'center' }}>
                  <Button size="small" variant={draft ? 'contained' : 'outlined'} startIcon={draft ? <EditIcon /> : <ViewIcon />} onClick={() => setEditor({ id: structure.id, sessionYearId: structure.session_year_id })}>
                    {draft ? 'Edit prices' : 'View prices'}
                  </Button>
                  {draft && (
                    <Button
                      size="small"
                      color="success"
                      startIcon={<PublishIcon />}
                      onClick={() =>
                        setConfirm({
                          title: 'Publish fee structure',
                          message: `Publish "${structure.name}"? Students are billed from it after the next plan build, and the structure published before it is archived.`,
                          confirmLabel: 'Publish',
                          onConfirm: async () => {
                            await billingAPI.publishStructure(structure.id);
                            notify('Published. Build plans on the Billing run tab to apply it.');
                            load();
                          },
                        })
                      }
                    >
                      Publish
                    </Button>
                  )}
                  <Box sx={{ flexGrow: 1 }} />
                  <Tooltip title="Copy into a new draft">
                    <IconButton
                      size="small"
                      onClick={() => {
                        setCopyTo(structure.session_year_id);
                        setCopyError(null);
                        setCopying(structure);
                      }}
                    >
                      <CopyIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                  {published && (
                    <Tooltip title="Archive">
                      <IconButton
                        size="small"
                        onClick={() =>
                          setConfirm({
                            title: 'Archive fee structure',
                            message: `Archive "${structure.name}"? The session then has no published structure until you publish another.`,
                            confirmLabel: 'Archive',
                            danger: true,
                            onConfirm: async () => {
                              await billingAPI.archiveStructure(structure.id);
                              notify('Archived.');
                              load();
                            },
                          })
                        }
                      >
                        <ArchiveIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  )}
                  {draft && (
                    <Tooltip title="Delete draft">
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() =>
                          setConfirm({
                            title: 'Delete draft',
                            message: `Delete the draft "${structure.name}"?`,
                            confirmLabel: 'Delete',
                            danger: true,
                            onConfirm: async () => {
                              await billingAPI.deleteStructure(structure.id);
                              notify('Draft deleted.');
                              load();
                            },
                          })
                        }
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  )}
                </Box>
              </Box>
            );
          })}
        </Box>
      )}

      <StructureEditor
        target={editor}
        lookups={lookups}
        heads={heads}
        onClose={() => setEditor(null)}
        onSaved={() => {
          notify('Draft saved.');
          load();
        }}
      />

      <FormDialog
        open={Boolean(copying)}
        title="Copy fee structure"
        subtitle={copying?.name}
        onClose={() => setCopying(null)}
        onSubmit={copy}
        submitLabel="Copy"
        busy={copyBusy}
        disabled={!copyTo}
        error={copyError}
        maxWidth="xs"
      >
        <Typography variant="body2" color="text.secondary">
          Every price is copied into a new draft that you can change before publishing.
        </Typography>
        <TextField select label="Copy to session" value={copyTo} onChange={(event) => setCopyTo(Number(event.target.value))}>
          {lookups.sessionYears.map((year) => (
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

export default FeeStructuresTab;
