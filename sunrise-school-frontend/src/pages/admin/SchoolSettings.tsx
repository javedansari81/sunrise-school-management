/**
 * Settings for this school: its profile, modules and settings, and the lists
 * it keeps for itself (classes, session years, departments ...). Every change
 * applies to this school only.
 */
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Alert,
  Avatar,
  Box,
  Button,
  Chip,
  FormControlLabel,
  IconButton,
  List,
  ListItemButton,
  ListItemText,
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
import {
  Add as AddIcon,
  Business as ProfileIcon,
  Edit as EditIcon,
  ListAlt as ListsIcon,
  RestartAlt as ResetIcon,
  Settings as SettingsIcon,
  Tune as TuneIcon,
} from '@mui/icons-material';
import AdminLayout from '../../components/Layout/AdminLayout';
import { apiError, EmptyState, FieldRow, FormDialog, Loading, PageHero, Panel, PillTabs, StatusChip, useNotify } from '../../components/ui';
import { useSchool } from '../../contexts/SchoolContext';
import { configurationService } from '../../services/configurationService';
import {
  ListField,
  ListKind,
  ListRow,
  SchoolProfile,
  schoolSettingsAPI,
  SettingValue,
  SHOP_SETTING,
} from '../../services/schoolSettingsService';

const TABS = [
  { value: 'profile', label: 'School profile', icon: <ProfileIcon fontSize="small" /> },
  { value: 'settings', label: 'Modules and settings', icon: <TuneIcon fontSize="small" /> },
  { value: 'lists', label: 'Lists', icon: <ListsIcon fontSize="small" /> },
];

type Notify = ReturnType<typeof useNotify>['notify'];

// ---------------------------------------------------------------- profile

const PROFILE_FIELDS: { name: keyof SchoolProfile; label: string; max: number; wide?: boolean; help?: string }[] = [
  { name: 'name', label: 'School name', max: 255, wide: true },
  { name: 'short_name', label: 'Short name', max: 50, help: 'Shown where space is tight, e.g. the menu' },
  { name: 'phone', label: 'Phone', max: 20 },
  { name: 'email', label: 'Email', max: 255 },
  { name: 'website', label: 'Website', max: 255 },
  { name: 'address', label: 'Address', max: 1000, wide: true },
  { name: 'logo_url', label: 'Logo URL', max: 1000, wide: true, help: 'Link to the school logo image. Used on the website, the portals and receipts.' },
];

const ProfileTab: React.FC<{ notify: Notify; onSaved: () => Promise<void> }> = ({ notify, onSaved }) => {
  const [profile, setProfile] = useState<SchoolProfile | null>(null);
  const [form, setForm] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fill = (data: SchoolProfile) => {
    setProfile(data);
    setForm(Object.fromEntries(PROFILE_FIELDS.map((field) => [field.name, (data[field.name] as string | null) || ''])));
  };

  useEffect(() => {
    schoolSettingsAPI.getProfile().then(fill).catch((failure) => setError(apiError(failure)));
  }, []);

  const changed = profile !== null && PROFILE_FIELDS.some((field) => (form[field.name] || '') !== ((profile[field.name] as string | null) || ''));

  const save = async () => {
    if (!profile) return;
    setBusy(true);
    setError(null);
    try {
      const body: Record<string, string | null> = {};
      PROFILE_FIELDS.forEach((field) => {
        if ((form[field.name] || '') !== ((profile[field.name] as string | null) || '')) body[field.name] = form[field.name].trim() || null;
      });
      fill(await schoolSettingsAPI.updateProfile(body));
      await onSaved();
      notify('School profile saved.');
    } catch (failure) {
      setError(apiError(failure));
    } finally {
      setBusy(false);
    }
  };

  if (!profile) return error ? <Alert severity="error">{error}</Alert> : <Loading />;

  return (
    <Box sx={{ display: 'grid', gap: 3, gridTemplateColumns: { xs: '1fr', lg: 'minmax(0, 1.7fr) minmax(0, 1fr)' }, alignItems: 'start' }}>
      <Panel
        title="School profile"
        subtitle="Shown on the website, in the portals and on receipts"
        actions={
          <Button variant="contained" onClick={save} disabled={!changed || busy || !form.name?.trim()}>
            Save changes
          </Button>
        }
      >
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {error && <Alert severity="error">{error}</Alert>}
          <TextField label="School name" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} required slotProps={{ htmlInput: { maxLength: 255 } }} />
          <FieldRow>
            {PROFILE_FIELDS.filter((field) => !field.wide).map((field) => (
              <TextField
                key={field.name}
                label={field.label}
                value={form[field.name]}
                helperText={field.help}
                type={field.name === 'email' ? 'email' : 'text'}
                onChange={(event) => setForm({ ...form, [field.name]: event.target.value })}
                slotProps={{ htmlInput: { maxLength: field.max } }}
              />
            ))}
          </FieldRow>
          <TextField label="Address" value={form.address} onChange={(event) => setForm({ ...form, address: event.target.value })} multiline minRows={2} slotProps={{ htmlInput: { maxLength: 1000 } }} />
          <TextField label="Logo URL" value={form.logo_url} helperText={PROFILE_FIELDS.find((field) => field.name === 'logo_url')?.help} onChange={(event) => setForm({ ...form, logo_url: event.target.value })} slotProps={{ htmlInput: { maxLength: 1000 } }} />
        </Box>
      </Panel>

      <Panel title="Set by the platform" subtitle="Ask the platform admin to change these">
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <Avatar src={form.logo_url || undefined} sx={{ width: 56, height: 56, bgcolor: 'primary.main', fontWeight: 800 }}>
            {(form.name || '?').charAt(0)}
          </Avatar>
          <Box sx={{ minWidth: 0 }}>
            <Typography sx={{ fontWeight: 700 }} noWrap>
              {form.name}
            </Typography>
            <Typography variant="body2" color="text.secondary" noWrap>
              {form.short_name || '—'}
            </Typography>
          </Box>
        </Box>
        {[
          ['School code', profile.code],
          ['Currency', profile.currency],
          ['Time zone', profile.timezone],
          ['Academic year starts', new Date(2000, profile.academic_year_start_month - 1, 1).toLocaleString('en-IN', { month: 'long' })],
        ].map(([label, value]) => (
          <Box key={label} sx={{ display: 'flex', justifyContent: 'space-between', gap: 2, py: 0.75, borderTop: '1px solid rgba(15,23,42,0.06)' }}>
            <Typography variant="body2" color="text.secondary">
              {label}
            </Typography>
            <Typography variant="body2" sx={{ fontWeight: 600, fontFamily: label === 'School code' ? 'monospace' : undefined }}>
              {value}
            </Typography>
          </Box>
        ))}
      </Panel>
    </Box>
  );
};

// ---------------------------------------------------------------- settings

const shown = (setting: SettingValue): string => {
  const value = setting.value ?? setting.default;
  if (setting.type === 'bool') return value === 'true' ? 'On' : 'Off';
  return value ?? '—';
};

const SettingsTab: React.FC<{ notify: Notify; onShopChanged: () => Promise<void> }> = ({ notify, onShopChanged }) => {
  const [values, setValues] = useState<SettingValue[] | null>(null);
  const [editing, setEditing] = useState<{ setting: SettingValue; value: string } | null>(null);
  const [busyKey, setBusyKey] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dialogError, setDialogError] = useState<string | null>(null);

  useEffect(() => {
    schoolSettingsAPI.listValues().then(setValues).catch((failure) => setError(apiError(failure)));
  }, []);

  const store = async (setting: SettingValue, value: string | boolean | null): Promise<boolean> => {
    setBusyKey(setting.key);
    setError(null);
    setDialogError(null);
    try {
      const saved = await schoolSettingsAPI.setValue(setting.key, value);
      setValues((current) => (current || []).map((item) => (item.key === saved.key ? saved : item)));
      if (setting.key === SHOP_SETTING) await onShopChanged();
      notify(value === null ? `${setting.label} reset to the default.` : `${setting.label} saved.`);
      return true;
    } catch (failure) {
      (editing ? setDialogError : setError)(apiError(failure));
      return false;
    } finally {
      setBusyKey(null);
    }
  };

  const groups = useMemo(() => {
    const result: Record<string, SettingValue[]> = {};
    (values || []).forEach((setting) => {
      (result[setting.group] = result[setting.group] || []).push(setting);
    });
    return Object.entries(result);
  }, [values]);

  if (!values) return error ? <Alert severity="error">{error}</Alert> : <Loading />;

  return (
    <Box sx={{ display: 'grid', gap: 3, gridTemplateColumns: { xs: '1fr', lg: 'repeat(2, minmax(0, 1fr))' }, alignItems: 'start' }}>
      {error && (
        <Alert severity="error" sx={{ gridColumn: '1 / -1' }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      {groups.map(([group, settings]) => (
        <Panel key={group} title={group} padded={false}>
          {settings.map((setting) => (
            <Box key={setting.key} sx={{ display: 'flex', alignItems: 'center', gap: 2, px: 2.5, py: 1.75, borderTop: '1px solid rgba(15,23,42,0.06)', '&:first-of-type': { borderTop: 'none' } }}>
              <Box sx={{ flexGrow: 1, minWidth: 0 }}>
                <Typography sx={{ fontWeight: 600, fontSize: '0.92rem' }}>
                  {setting.label}
                  {setting.value === null && setting.type !== 'bool' && <Chip label="default" size="small" sx={{ ml: 1, height: 20, fontSize: '0.7rem' }} />}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {setting.help}
                </Typography>
              </Box>
              {setting.type === 'bool' ? (
                <Switch
                  checked={(setting.value ?? setting.default) === 'true'}
                  disabled={busyKey === setting.key}
                  onChange={(event) => store(setting, event.target.checked)}
                  inputProps={{ 'aria-label': setting.label }}
                />
              ) : (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, flexShrink: 0 }}>
                  <Typography sx={{ fontWeight: 700, fontSize: '0.9rem', maxWidth: 160, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{shown(setting)}</Typography>
                  <Tooltip title="Change">
                    <IconButton size="small" color="primary" onClick={() => { setDialogError(null); setEditing({ setting, value: setting.value ?? setting.default ?? '' }); }}>
                      <EditIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                  {setting.value !== null && (
                    <Tooltip title="Reset to default">
                      <IconButton size="small" disabled={busyKey === setting.key} onClick={() => store(setting, null)}>
                        <ResetIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  )}
                </Box>
              )}
            </Box>
          ))}
        </Panel>
      ))}

      <FormDialog
        open={Boolean(editing)}
        title={editing?.setting.label || ''}
        subtitle={editing?.setting.help}
        onClose={() => setEditing(null)}
        onSubmit={async () => editing && (await store(editing.setting, editing.value)) && setEditing(null)}
        busy={Boolean(busyKey)}
        error={dialogError}
        maxWidth="xs"
      >
        {editing &&
          (editing.setting.type === 'choice' ? (
            <TextField select label={editing.setting.label} value={editing.value} onChange={(event) => setEditing({ ...editing, value: event.target.value })}>
              {editing.setting.choices.map((choice) => (
                <MenuItem key={choice} value={choice}>
                  {choice.charAt(0) + choice.slice(1).toLowerCase()}
                </MenuItem>
              ))}
            </TextField>
          ) : (
            <TextField
              autoFocus
              label={editing.setting.label}
              value={editing.value}
              type={editing.setting.type === 'text' ? 'text' : 'number'}
              onChange={(event) => setEditing({ ...editing, value: event.target.value })}
              helperText={editing.setting.default !== null ? `Default: ${editing.setting.default}. Leave empty for the default.` : 'Leave empty for the default.'}
              slotProps={{ htmlInput: { min: editing.setting.min ?? undefined, max: editing.setting.max ?? undefined, step: editing.setting.type === 'decimal' ? '0.01' : 1 } }}
            />
          ))}
      </FormDialog>
    </Box>
  );
};

// ---------------------------------------------------------------- lists

const display = (field: ListField, value: any, refs: Record<string, ListRow[]>): React.ReactNode => {
  if (value === null || value === undefined || value === '') return '—';
  if (field.type === 'bool') return value ? 'Yes' : 'No';
  if (field.type === 'ref') return (refs[field.ref || ''] || []).find((row) => row.id === value)?.name || value;
  return String(value);
};

const ListsTab: React.FC<{ notify: Notify; shopEnabled: boolean }> = ({ notify, shopEnabled }) => {
  const [kinds, setKinds] = useState<ListKind[] | null>(null);
  const [kind, setKind] = useState<string>('classes');
  const [rows, setRows] = useState<ListRow[] | null>(null);
  const [refs, setRefs] = useState<Record<string, ListRow[]>>({});
  const [form, setForm] = useState<Record<string, any> | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    schoolSettingsAPI
      .listKinds()
      .then((data) => {
        setKinds(data);
        setKind((current) => (data.some((item) => item.kind === current) ? current : data[0]?.kind));
      })
      .catch((failure) => setError(apiError(failure)));
  }, [shopEnabled]);

  const spec = kinds?.find((item) => item.kind === kind);

  const load = useCallback(async () => {
    if (!spec) return;
    setRows(null);
    try {
      setRows(await schoolSettingsAPI.listRows(spec.kind));
      const refKinds = spec.fields.filter((field) => field.type === 'ref' && field.ref).map((field) => field.ref as string);
      const loaded = await Promise.all(refKinds.map((ref) => schoolSettingsAPI.listRows(ref)));
      setRefs(Object.fromEntries(refKinds.map((ref, index) => [ref, loaded[index]])));
      setError(null);
    } catch (failure) {
      setError(apiError(failure));
      setRows([]);
    }
  }, [spec]);

  useEffect(() => {
    load();
  }, [load]);

  const open = (row?: ListRow) => {
    if (!spec) return;
    setFormError(null);
    const empty = Object.fromEntries(spec.fields.map((field) => [field.name, field.type === 'bool' ? false : '']));
    setForm(row ? { ...empty, ...Object.fromEntries(Object.entries(row).map(([key, value]) => [key, value ?? ''])) } : { ...empty, id: null, is_active: true });
  };

  const save = async () => {
    if (!spec || !form) return;
    setBusy(true);
    setFormError(null);
    try {
      const body: Record<string, any> = { is_active: form.is_active };
      spec.fields.forEach((field) => {
        const value = form[field.name];
        body[field.name] = field.type === 'bool' ? Boolean(value) : value === '' ? null : value;
      });
      if (form.id) await schoolSettingsAPI.updateRow(spec.kind, form.id, body);
      else await schoolSettingsAPI.createRow(spec.kind, body);
      configurationService.clearConfiguration(); // other screens load the new list next time
      await load();
      notify(`${spec.label}: saved.`);
      setForm(null);
    } catch (failure) {
      setFormError(apiError(failure));
    } finally {
      setBusy(false);
    }
  };

  if (!kinds) return error ? <Alert severity="error">{error}</Alert> : <Loading />;

  const groups = kinds.reduce<Record<string, ListKind[]>>((result, item) => {
    (result[item.group] = result[item.group] || []).push(item);
    return result;
  }, {});
  const missingRequired = spec?.fields.some((field) => field.required && (form?.[field.name] === '' || form?.[field.name] === null || form?.[field.name] === undefined));

  return (
    <Box sx={{ display: 'grid', gap: 3, gridTemplateColumns: { xs: '1fr', md: '240px minmax(0, 1fr)' }, alignItems: 'start' }}>
      <Panel padded={false}>
        <List dense disablePadding sx={{ py: 1 }}>
          {Object.entries(groups).map(([group, items]) => (
            <React.Fragment key={group}>
              <ListSubheader disableSticky sx={{ background: 'transparent', lineHeight: '32px', fontWeight: 700, fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: 0.6 }}>
                {group}
              </ListSubheader>
              {items.map((item) => (
                <ListItemButton key={item.kind} selected={item.kind === kind} onClick={() => setKind(item.kind)} sx={{ mx: 1, borderRadius: '10px' }}>
                  <ListItemText primary={item.label} slotProps={{ primary: { sx: { fontWeight: item.kind === kind ? 700 : 500, fontSize: '0.9rem' } } }} />
                </ListItemButton>
              ))}
            </React.Fragment>
          ))}
        </List>
      </Panel>

      {spec && (
        <Panel
          title={spec.label}
          subtitle={spec.hint}
          padded={false}
          actions={
            <Button variant="contained" startIcon={<AddIcon />} onClick={() => open()}>
              Add
            </Button>
          }
        >
          {error && <Alert severity="error" sx={{ m: 2 }}>{error}</Alert>}
          {rows === null ? (
            <Loading />
          ) : rows.length === 0 ? (
            <EmptyState title={`No ${spec.label.toLowerCase()} yet`} hint="Add the first one." icon={<ListsIcon />} />
          ) : (
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    {spec.fields.map((field) => (
                      <TableCell key={field.name} align={field.type === 'int' || field.type === 'decimal' ? 'right' : 'left'}>
                        {field.label}
                      </TableCell>
                    ))}
                    <TableCell>Status</TableCell>
                    <TableCell align="right">Edit</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {rows.map((row) => (
                    <TableRow key={row.id} hover sx={{ opacity: row.is_active ? 1 : 0.6 }}>
                      {spec.fields.map((field, index) => (
                        <TableCell key={field.name} align={field.type === 'int' || field.type === 'decimal' ? 'right' : 'left'} sx={index === 0 ? { fontWeight: 600 } : undefined}>
                          {field.name === 'is_current' && row.is_current ? <Chip label="Current" color="primary" size="small" /> : display(field, row[field.name], refs)}
                        </TableCell>
                      ))}
                      <TableCell>
                        <StatusChip status={row.is_active ? 'ACTIVE' : 'INACTIVE'} label={row.is_active ? 'In use' : 'Not in use'} />
                      </TableCell>
                      <TableCell align="right">
                        <Tooltip title="Edit">
                          <IconButton size="small" color="primary" onClick={() => open(row)}>
                            <EditIcon fontSize="small" />
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
      )}

      <FormDialog
        open={Boolean(form)}
        title={`${form?.id ? 'Edit' : 'Add'}: ${spec?.label || ''}`}
        subtitle="Rows are never deleted, because records point at them. Turn off “In use” to stop offering one."
        onClose={() => setForm(null)}
        onSubmit={save}
        busy={busy}
        disabled={missingRequired}
        error={formError}
      >
        {form && spec && (
          <>
            {spec.fields.map((field, index) =>
              field.type === 'bool' ? (
                <FormControlLabel key={field.name} control={<Switch checked={Boolean(form[field.name])} onChange={(event) => setForm({ ...form, [field.name]: event.target.checked })} />} label={field.label} />
              ) : field.type === 'ref' ? (
                <TextField key={field.name} select label={field.label} value={form[field.name]} required={field.required} helperText={field.help || undefined} onChange={(event) => setForm({ ...form, [field.name]: Number(event.target.value) })}>
                  {(refs[field.ref || ''] || [])
                    .filter((option) => option.is_active || option.id === form[field.name])
                    .map((option) => (
                      <MenuItem key={option.id} value={option.id}>
                        {option.name}
                      </MenuItem>
                    ))}
                </TextField>
              ) : (
                <TextField
                  key={field.name}
                  autoFocus={index === 0}
                  label={field.label}
                  value={form[field.name]}
                  required={field.required}
                  helperText={field.help || undefined}
                  type={field.type === 'date' ? 'date' : field.type === 'int' || field.type === 'decimal' ? 'number' : 'text'}
                  onChange={(event) => setForm({ ...form, [field.name]: event.target.value })}
                  slotProps={{
                    inputLabel: field.type === 'date' ? { shrink: true } : undefined,
                    htmlInput: { maxLength: field.max_length ?? undefined, min: field.type === 'decimal' ? 0 : undefined, step: field.type === 'decimal' ? '0.01' : undefined },
                  }}
                />
              )
            )}
            <FormControlLabel control={<Switch checked={Boolean(form.is_active)} onChange={(event) => setForm({ ...form, is_active: event.target.checked })} />} label="In use" />
          </>
        )}
      </FormDialog>
    </Box>
  );
};

// ---------------------------------------------------------------- page

const SettingsContent: React.FC = () => {
  const { school, refresh } = useSchool();
  const { notify, node } = useNotify();
  const [tab, setTab] = useState('profile');

  return (
    <>
      <PageHero icon={<SettingsIcon />} title="Settings" subtitle={`How ${school.shortName} runs: its profile, the modules it uses, fee rules and its own lists. Changes apply to this school only.`} />
      <PillTabs value={tab} onChange={setTab} tabs={TABS} />
      <div key={tab} className="fade-up">
        {tab === 'profile' && <ProfileTab notify={notify} onSaved={refresh} />}
        {tab === 'settings' && <SettingsTab notify={notify} onShopChanged={refresh} />}
        {tab === 'lists' && <ListsTab notify={notify} shopEnabled={school.features.shop} />}
      </div>
      {node}
    </>
  );
};

const SchoolSettings: React.FC = () => (
  <AdminLayout>
    <SettingsContent />
  </AdminLayout>
);

export default SchoolSettings;
