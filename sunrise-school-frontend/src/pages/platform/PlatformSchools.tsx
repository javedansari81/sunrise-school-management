/** Platform admin: every school on the service. Create, edit, suspend and reactivate. */
import React, { useCallback, useEffect, useState } from 'react';
import { Alert, Avatar, Box, Button, IconButton, InputAdornment, MenuItem, TextField, Tooltip, Typography } from '@mui/material';
import { alpha } from '@mui/material/styles';
import {
  Add as AddIcon,
  AdminPanelSettings as PlatformIcon,
  Apartment as SchoolsIcon,
  Block as SuspendIcon,
  CheckCircle as ActiveIcon,
  Edit as EditIcon,
  Groups as StudentsIcon,
  Logout as LogoutIcon,
  OpenInNew as OpenIcon,
  PlayCircle as ActivateIcon,
  Search as SearchIcon,
} from '@mui/icons-material';
import { Navigate, useNavigate } from 'react-router-dom';
import { platformAPI, platformAuth, School } from '../../services/platformService';
import {
  apiError,
  ConfirmDialog,
  ConfirmRequest,
  EmptyState,
  FieldRow,
  FormDialog,
  formatDate,
  heroButtonSx,
  Loading,
  PageHero,
  StatCard,
  StatGrid,
  StatusChip,
  useNotify,
} from '../../components/ui';
import { brand, ease } from '../../theme';

const BASE_DOMAIN = (process.env.REACT_APP_BASE_DOMAIN || '').trim().replace(/^\./, '');
const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
const CODE_RE = /^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$/;

/** Where a school's own site lives, when subdomains are set up. */
const schoolUrl = (code: string) => (BASE_DOMAIN ? `${window.location.protocol}//${code}.${BASE_DOMAIN}` : null);

const blankSchool = {
  code: '', name: '', short_name: '', phone: '', email: '', address: '', website: '', logo_url: '', academic_year_start_month: 4,
  admin_first_name: '', admin_last_name: '', admin_email: '', admin_password: '', copy_lists_from: '',
};

const PlatformSchools: React.FC = () => {
  const navigate = useNavigate();
  const { notify, notifyError, node } = useNotify();
  const admin = platformAuth.admin();

  const [schools, setSchools] = useState<School[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('');
  const [form, setForm] = useState<any | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [created, setCreated] = useState<any | null>(null);
  const [confirm, setConfirm] = useState<ConfirmRequest | null>(null);

  useEffect(() => {
    document.title = 'Schools · Platform admin';
  }, []);

  const load = useCallback(async () => {
    try {
      setSchools(await platformAPI.listSchools({ search: search.trim(), status }));
    } catch (failure) {
      notifyError(failure);
    } finally {
      setLoading(false);
    }
  }, [search, status, notifyError]);

  useEffect(() => {
    const timer = setTimeout(load, 250);
    return () => clearTimeout(timer);
  }, [load]);

  if (!platformAuth.isLoggedIn()) return <Navigate to="/platform/login" replace />;

  const set = (field: string) => (event: React.ChangeEvent<HTMLInputElement>) => setForm((current: any) => ({ ...current, [field]: event.target.value }));
  const isNew = form && !form.id;

  const openEdit = (school: School) => {
    setError(null);
    setForm({
      id: school.id, code: school.code, name: school.name, short_name: school.short_name || '', phone: school.phone || '', email: school.email || '',
      address: school.address || '', website: school.website || '', logo_url: school.logo_url || '', academic_year_start_month: school.academic_year_start_month,
    });
  };

  const valid =
    form &&
    CODE_RE.test(form.code) &&
    form.name.trim() &&
    (!isNew || (form.admin_first_name.trim() && form.admin_last_name.trim() && form.admin_email.trim() && form.admin_password.length >= 8));

  const save = async () => {
    setBusy(true);
    setError(null);
    const details = {
      code: form.code,
      name: form.name.trim(),
      short_name: form.short_name.trim() || null,
      phone: form.phone.trim() || null,
      email: form.email.trim() || null,
      address: form.address.trim() || null,
      website: form.website.trim() || null,
      logo_url: form.logo_url.trim() || null,
      academic_year_start_month: Number(form.academic_year_start_month),
    };
    try {
      if (isNew) {
        const result = await platformAPI.createSchool({
          ...details,
          admin: { first_name: form.admin_first_name.trim(), last_name: form.admin_last_name.trim(), email: form.admin_email.trim(), password: form.admin_password },
          ...(form.copy_lists_from ? { copy_lists_from: form.copy_lists_from } : {}),
        });
        setCreated(result);
      } else {
        await platformAPI.updateSchool(form.id, details);
        notify('School saved.');
      }
      setForm(null);
      load();
    } catch (failure) {
      setError(apiError(failure));
    } finally {
      setBusy(false);
    }
  };

  const logout = () => {
    platformAuth.logout();
    navigate('/platform/login', { replace: true });
  };

  const active = schools.filter((school) => school.status === 'ACTIVE').length;

  return (
    <Box sx={{ minHeight: '100vh', maxWidth: 1280, mx: 'auto', p: { xs: 1.5, sm: 3, md: 4 } }}>
      <PageHero
        icon={<PlatformIcon />}
        title="Schools"
        subtitle={`Platform admin${admin ? ` · ${admin.first_name} ${admin.last_name}` : ''}. Each school has its own address, data and logins.`}
        actions={
          <>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              sx={heroButtonSx}
              onClick={() => {
                setError(null);
                setForm({ ...blankSchool });
              }}
            >
              New school
            </Button>
            <Button variant="contained" startIcon={<LogoutIcon />} sx={heroButtonSx} onClick={logout}>
              Log out
            </Button>
          </>
        }
      />

      <StatGrid>
        <StatCard label="Schools" value={schools.length} hint={search || status ? 'matching the filter' : 'on the platform'} icon={<SchoolsIcon />} tone="blue" />
        <StatCard label="Active" value={active} icon={<ActiveIcon />} tone="green" delay={60} />
        <StatCard label="Suspended" value={schools.length - active} icon={<SuspendIcon />} tone={schools.length - active > 0 ? 'red' : 'slate'} delay={120} />
        <StatCard label="Students" value={schools.reduce((total, school) => total + school.students, 0).toLocaleString('en-IN')} hint="across these schools" icon={<StudentsIcon />} tone="violet" delay={180} />
      </StatGrid>

      <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mb: 3 }}>
        <TextField
          size="small"
          placeholder="Search by name or code"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          sx={{ flexGrow: 1, minWidth: 220, maxWidth: 420 }}
          slotProps={{ input: { startAdornment: <InputAdornment position="start"><SearchIcon fontSize="small" /></InputAdornment> } }}
        />
        <TextField select size="small" label="Status" value={status} onChange={(event) => setStatus(event.target.value)} sx={{ minWidth: 150 }} slotProps={{ select: { displayEmpty: true }, inputLabel: { shrink: true } }}>
          <MenuItem value="">All</MenuItem>
          <MenuItem value="ACTIVE">Active</MenuItem>
          <MenuItem value="SUSPENDED">Suspended</MenuItem>
        </TextField>
      </Box>

      {loading ? (
        <Loading />
      ) : schools.length === 0 ? (
        <EmptyState title="No schools found" hint={search || status ? 'Clear the filter to see every school.' : 'Create the first school to get started.'} icon={<SchoolsIcon />} />
      ) : (
        <Box sx={{ display: 'grid', gap: 2.5, gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))' }}>
          {schools.map((school, index) => {
            const suspended = school.status === 'SUSPENDED';
            const url = schoolUrl(school.code);
            return (
              <Box
                key={school.id}
                sx={{
                  position: 'relative',
                  overflow: 'hidden',
                  p: 2.5,
                  borderRadius: '22px',
                  background: 'rgba(255,255,255,0.92)',
                  backdropFilter: 'blur(12px)',
                  border: '1px solid',
                  borderColor: suspended ? alpha('#dc2626', 0.3) : 'rgba(15,23,42,0.07)',
                  boxShadow: brand.shadowSoft,
                  animation: `fadeUp 0.5s ${ease} both`,
                  animationDelay: `${Math.min(index, 10) * 50}ms`,
                  transition: `transform 0.35s ${ease}, box-shadow 0.35s ${ease}`,
                  '&:hover': { transform: 'translateY(-5px)', boxShadow: brand.shadowLift },
                  '&::before': { content: '""', position: 'absolute', inset: '0 0 auto 0', height: 4, background: suspended ? 'linear-gradient(90deg,#f87171,#dc2626)' : brand.gradient },
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                  <Avatar src={school.logo_url || undefined} variant="rounded" sx={{ width: 52, height: 52, borderRadius: '15px', fontWeight: 800, background: brand.gradient }}>
                    {(school.short_name || school.name)[0]?.toUpperCase()}
                  </Avatar>
                  <Box sx={{ minWidth: 0, flexGrow: 1 }}>
                    <Typography noWrap sx={{ fontWeight: 800 }} title={school.name}>
                      {school.name}
                    </Typography>
                    <Typography noWrap variant="caption" color="text.secondary" sx={{ fontFamily: 'monospace' }}>
                      {BASE_DOMAIN ? `${school.code}.${BASE_DOMAIN}` : school.code}
                    </Typography>
                  </Box>
                  <StatusChip status={school.status} />
                </Box>

                <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 1, my: 2 }}>
                  {[
                    ['Students', school.students],
                    ['Teachers', school.teachers],
                    ['Logins', school.users],
                  ].map(([label, value]) => (
                    <Box key={label} sx={{ p: 1, textAlign: 'center', borderRadius: '12px', background: alpha(brand.primary, 0.05) }}>
                      <Typography sx={{ fontWeight: 800, fontSize: '1.1rem' }}>{Number(value).toLocaleString('en-IN')}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {label}
                      </Typography>
                    </Box>
                  ))}
                </Box>

                <Typography variant="caption" color="text.secondary" component="div" noWrap>
                  {[school.phone, school.email].filter(Boolean).join(' · ') || 'No contact details'}
                </Typography>
                <Typography variant="caption" color="text.secondary" component="div">
                  Added {formatDate(school.created_at)} · year starts in {MONTHS[school.academic_year_start_month - 1]}
                </Typography>

                <Box sx={{ display: 'flex', gap: 0.5, mt: 1.5, alignItems: 'center' }}>
                  <Button size="small" variant="outlined" startIcon={<EditIcon />} onClick={() => openEdit(school)}>
                    Edit
                  </Button>
                  {suspended ? (
                    <Button
                      size="small"
                      color="success"
                      startIcon={<ActivateIcon />}
                      onClick={() =>
                        setConfirm({
                          title: 'Reactivate school',
                          message: `Let ${school.name} log in again?`,
                          confirmLabel: 'Reactivate',
                          onConfirm: async () => {
                            await platformAPI.activate(school.id);
                            notify(`${school.name} is active again.`);
                            load();
                          },
                        })
                      }
                    >
                      Reactivate
                    </Button>
                  ) : (
                    <Button
                      size="small"
                      color="error"
                      startIcon={<SuspendIcon />}
                      onClick={() =>
                        setConfirm({
                          title: 'Suspend school',
                          message: `Suspend ${school.name}? Nobody from this school can log in, and everyone logged in now is signed out at once. Its data is kept.`,
                          confirmLabel: 'Suspend',
                          danger: true,
                          onConfirm: async () => {
                            await platformAPI.suspend(school.id);
                            notify(`${school.name} is suspended.`, 'warning');
                            load();
                          },
                        })
                      }
                    >
                      Suspend
                    </Button>
                  )}
                  <Box sx={{ flexGrow: 1 }} />
                  {url && (
                    <Tooltip title="Open the school's site">
                      <IconButton size="small" component="a" href={url} target="_blank" rel="noopener noreferrer">
                        <OpenIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  )}
                </Box>
              </Box>
            );
          })}
        </Box>
      )}

      <FormDialog
        open={Boolean(form)}
        title={isNew ? 'New school' : 'Edit school'}
        subtitle={isNew ? 'Creates the school, its first admin login and its starting lists' : form?.name}
        onClose={() => setForm(null)}
        onSubmit={save}
        submitLabel={isNew ? 'Create school' : 'Save'}
        busy={busy}
        disabled={!valid}
        error={error}
        maxWidth="md"
      >
        {form && (
          <>
            <FieldRow>
              <TextField label="School name" value={form.name} onChange={set('name')} required autoFocus slotProps={{ htmlInput: { maxLength: 255 } }} />
              <TextField label="Short name" value={form.short_name} onChange={set('short_name')} helperText="Shown in the menu and on receipts" slotProps={{ htmlInput: { maxLength: 50 } }} />
            </FieldRow>
            <FieldRow>
              <TextField
                label="Code (web address)"
                value={form.code}
                onChange={(event) => setForm({ ...form, code: event.target.value.toLowerCase().replace(/[^a-z0-9-]/g, '') })}
                required
                error={form.code !== '' && !CODE_RE.test(form.code)}
                helperText={
                  !isNew
                    ? 'Changing the code changes the school’s address; old links stop working'
                    : `Small letters, digits and hyphens${BASE_DOMAIN ? `. Address: ${form.code || 'code'}.${BASE_DOMAIN}` : ''}`
                }
                slotProps={{ htmlInput: { maxLength: 63 } }}
              />
              <TextField select label="School year starts in" value={form.academic_year_start_month} onChange={set('academic_year_start_month')}>
                {MONTHS.map((month, index) => (
                  <MenuItem key={month} value={index + 1}>
                    {month}
                  </MenuItem>
                ))}
              </TextField>
            </FieldRow>
            <FieldRow>
              <TextField label="Phone" value={form.phone} onChange={set('phone')} slotProps={{ htmlInput: { maxLength: 20 } }} />
              <TextField label="Email" type="email" value={form.email} onChange={set('email')} />
            </FieldRow>
            <TextField label="Address" value={form.address} onChange={set('address')} multiline minRows={2} />
            <FieldRow>
              <TextField label="Website" value={form.website} onChange={set('website')} slotProps={{ htmlInput: { maxLength: 255 } }} />
              <TextField label="Logo image address" value={form.logo_url} onChange={set('logo_url')} helperText="A link to the logo (https://…)" />
            </FieldRow>

            {isNew && (
              <>
                <Typography sx={{ fontWeight: 700, mt: 1 }}>First admin of the school</Typography>
                <FieldRow>
                  <TextField label="First name" value={form.admin_first_name} onChange={set('admin_first_name')} required />
                  <TextField label="Last name" value={form.admin_last_name} onChange={set('admin_last_name')} required />
                </FieldRow>
                <FieldRow>
                  <TextField label="Login email" type="email" value={form.admin_email} onChange={set('admin_email')} required autoComplete="off" />
                  <TextField
                    label="Password"
                    type="text"
                    value={form.admin_password}
                    onChange={set('admin_password')}
                    required
                    autoComplete="off"
                    error={form.admin_password !== '' && form.admin_password.length < 8}
                    helperText="At least 8 characters. Pass it on to the admin; they can change it."
                    slotProps={{ htmlInput: { maxLength: 72 } }}
                  />
                </FieldRow>
                <TextField select label="Copy classes, session years and other lists from" value={form.copy_lists_from} onChange={set('copy_lists_from')} slotProps={{ select: { displayEmpty: true }, inputLabel: { shrink: true } }}>
                  <MenuItem value="">The standard template</MenuItem>
                  {schools.map((school) => (
                    <MenuItem key={school.id} value={school.code}>
                      {school.name}
                    </MenuItem>
                  ))}
                </TextField>
              </>
            )}
          </>
        )}
      </FormDialog>

      <FormDialog open={Boolean(created)} title="School created" onClose={() => setCreated(null)} maxWidth="xs">
        {created && (
          <>
            <Alert severity="success">
              <strong>{created.school.name}</strong> is ready.
            </Alert>
            <Typography variant="body2">
              Admin login: <strong>{created.admin.email}</strong>
              {schoolUrl(created.school.code) && (
                <>
                  <br />
                  Address: <strong>{schoolUrl(created.school.code)}</strong>
                </>
              )}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Its classes, session years, fee heads, vehicle types and other lists were copied{created.copied_from ? ` from ${created.copied_from}` : ''}. Next, the
              school’s admin logs in and sets prices in a fee structure.
            </Typography>
          </>
        )}
      </FormDialog>
      <ConfirmDialog request={confirm} onClose={() => setConfirm(null)} />
      {node}
    </Box>
  );
};

export default PlatformSchools;
