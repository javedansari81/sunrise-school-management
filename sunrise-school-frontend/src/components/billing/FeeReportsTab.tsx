/** Fee reports: money collected between two dates, and what each class still owes. */
import React, { useCallback, useEffect, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  LinearProgress,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import {
  AccountBalanceWallet as WalletIcon,
  FactCheck as CheckIcon,
  Payments as PaymentsIcon,
  ReceiptLong as ReceiptIcon,
  Undo as UndoIcon,
  WarningAmber as WarningIcon,
} from '@mui/icons-material';
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip as ChartTooltip, XAxis, YAxis } from 'recharts';
import { billingAPI, CollectionReport, PendingByClass } from '../../services/billingService';
import { Lookups } from '../../hooks/useLookups';
import { apiError, EmptyState, formatDate, Loading, money, Panel, StatCard, StatGrid, todayISO, useNotify } from '../ui';
import { brand } from '../../theme';

interface Props {
  lookups: Lookups;
}

const firstOfMonth = () => `${todayISO().slice(0, 8)}01`;

/** A named amount with a bar showing its share of the total. */
const ShareRow: React.FC<{ label: string; amount: string; total: number; color: string }> = ({ label, amount, total, color }) => {
  const share = total > 0 ? Math.max(0, Math.min(100, (Number(amount) / total) * 100)) : 0;
  return (
    <Box sx={{ py: 1 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', gap: 2, mb: 0.5 }}>
        <Typography sx={{ fontSize: '0.875rem', fontWeight: 600 }}>{label}</Typography>
        <Typography sx={{ fontSize: '0.875rem', fontWeight: 700 }}>{money(amount)}</Typography>
      </Box>
      <LinearProgress variant="determinate" value={share} sx={{ backgroundColor: alpha(color, 0.12), '& .MuiLinearProgress-bar': { backgroundColor: color } }} />
    </Box>
  );
};

const FeeReportsTab: React.FC<Props> = ({ lookups }) => {
  const { notify, notifyError, node } = useNotify();
  const [dateFrom, setDateFrom] = useState(firstOfMonth());
  const [dateTo, setDateTo] = useState(todayISO());
  const [collection, setCollection] = useState<CollectionReport | null>(null);
  const [loadingCollection, setLoadingCollection] = useState(false);
  const [collectionError, setCollectionError] = useState<string | null>(null);

  const [sessionId, setSessionId] = useState<number | ''>(lookups.currentSessionId ?? '');
  const [pending, setPending] = useState<PendingByClass | null>(null);
  const [loadingPending, setLoadingPending] = useState(false);
  const [checking, setChecking] = useState(false);

  const loadCollection = useCallback(async () => {
    if (!dateFrom || !dateTo) return;
    setLoadingCollection(true);
    setCollectionError(null);
    try {
      setCollection(await billingAPI.collectionReport(dateFrom, dateTo));
    } catch (failure) {
      setCollectionError(apiError(failure));
    } finally {
      setLoadingCollection(false);
    }
  }, [dateFrom, dateTo]);

  const loadPending = useCallback(async () => {
    if (sessionId === '') return;
    setLoadingPending(true);
    try {
      setPending(await billingAPI.pendingByClass(sessionId));
    } catch (failure) {
      notifyError(failure);
    } finally {
      setLoadingPending(false);
    }
  }, [sessionId, notifyError]);

  useEffect(() => {
    loadCollection();
  }, [loadCollection]);
  useEffect(() => {
    loadPending();
  }, [loadPending]);

  const runCheck = async () => {
    setChecking(true);
    try {
      const result = await billingAPI.consistency();
      if (result.ok) notify(`All good: ${result.dues_checked} dues and ${result.payments_checked} payments add up.`);
      else notify(`${result.due_problems.length} dues and ${result.payment_problems.length} payments do not add up. Please report this.`, 'error');
    } catch (failure) {
      notifyError(failure);
    } finally {
      setChecking(false);
    }
  };

  const net = Number(collection?.net ?? 0);
  const chart = (collection?.by_day || []).map((day) => ({ day: formatDate(day.date).slice(0, 6), amount: Number(day.amount) }));

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      <Panel
        title="Collection"
        subtitle="Money received by payment date, with reversals taken off"
        actions={
          <>
            <TextField size="small" type="date" label="From" value={dateFrom} onChange={(event) => setDateFrom(event.target.value)} slotProps={{ inputLabel: { shrink: true }, htmlInput: { max: dateTo } }} />
            <TextField size="small" type="date" label="To" value={dateTo} onChange={(event) => setDateTo(event.target.value)} slotProps={{ inputLabel: { shrink: true }, htmlInput: { min: dateFrom } }} />
          </>
        }
      >
        {collectionError && <Alert severity="error" sx={{ mb: 2 }}>{collectionError}</Alert>}
        {loadingCollection && !collection ? (
          <Loading />
        ) : collection ? (
          <Box sx={{ opacity: loadingCollection ? 0.5 : 1, transition: 'opacity 0.2s ease' }}>
            <StatGrid min={180}>
              <StatCard label="Net collected" value={money(collection.net)} hint={`${collection.payments} payments`} icon={<WalletIcon />} tone="green" />
              <StatCard label="Received" value={money(collection.received)} icon={<PaymentsIcon />} tone="blue" delay={60} />
              <StatCard label="Reversed" value={money(collection.reversed)} icon={<UndoIcon />} tone={Number(collection.reversed) > 0 ? 'red' : 'slate'} delay={120} />
              <StatCard label="Advance credit" value={money(collection.not_allocated)} hint="Received but not yet used for a due" icon={<ReceiptIcon />} tone="violet" delay={180} />
            </StatGrid>

            {collection.payments === 0 && Number(collection.reversed) === 0 ? (
              <EmptyState title="Nothing collected in these dates" hint="Pick a wider date range." icon={<PaymentsIcon />} />
            ) : (
              <>
                <Typography sx={{ fontWeight: 700, mb: 1 }}>Per day</Typography>
                <Box sx={{ height: 260, mb: 3 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chart} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
                      <defs>
                        <linearGradient id="collectionBar" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor={brand.violet} />
                          <stop offset="100%" stopColor={brand.primary} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(15,23,42,0.07)" vertical={false} />
                      <XAxis dataKey="day" tickLine={false} axisLine={false} fontSize={12} />
                      <YAxis tickLine={false} axisLine={false} fontSize={12} width={64} tickFormatter={(value) => (value >= 1000 ? `${Math.round(value / 1000)}k` : value)} />
                      <ChartTooltip cursor={{ fill: 'rgba(37,99,235,0.06)' }} formatter={(value) => [money(Number(value)), 'Collected']} contentStyle={{ borderRadius: 12, border: 'none', boxShadow: '0 12px 30px rgba(15,23,42,0.18)' }} />
                      <Bar dataKey="amount" fill="url(#collectionBar)" radius={[8, 8, 0, 0]} maxBarSize={44} />
                    </BarChart>
                  </ResponsiveContainer>
                </Box>
                <Box sx={{ display: 'grid', gap: 4, gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' } }}>
                  <Box>
                    <Typography sx={{ fontWeight: 700, mb: 0.5 }}>By fee head</Typography>
                    {collection.by_head.map((head) => (
                      <ShareRow key={head.fee_head_id} label={head.name} amount={head.amount} total={net} color={brand.primary} />
                    ))}
                    {Number(collection.not_allocated) !== 0 && <ShareRow label="Advance credit" amount={collection.not_allocated} total={net} color={brand.violet} />}
                  </Box>
                  <Box>
                    <Typography sx={{ fontWeight: 700, mb: 0.5 }}>By payment method</Typography>
                    {collection.by_method.map((method) => (
                      <ShareRow key={String(method.payment_method_id)} label={method.method || 'Reversals'} amount={method.amount} total={net} color="#16a34a" />
                    ))}
                  </Box>
                </Box>
              </>
            )}
          </Box>
        ) : null}
      </Panel>

      <Panel
        title="Pending dues by class"
        subtitle={pending ? `As of ${formatDate(pending.as_of)}` : undefined}
        padded={false}
        actions={
          <TextField select size="small" label="Session" value={sessionId} onChange={(event) => setSessionId(Number(event.target.value))} sx={{ minWidth: 130 }}>
            {lookups.sessionYears.map((year) => (
              <MenuItem key={year.id} value={year.id}>
                {year.name}
              </MenuItem>
            ))}
          </TextField>
        }
      >
        {loadingPending && !pending ? (
          <Loading />
        ) : !pending || pending.classes.length === 0 ? (
          <EmptyState title="No pending dues" hint="Every due generated for this session is paid." icon={<CheckIcon />} />
        ) : (
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Class</TableCell>
                  <TableCell align="right">Students with dues</TableCell>
                  <TableCell align="right">Pending</TableCell>
                  <TableCell align="right">Of which overdue</TableCell>
                  <TableCell sx={{ width: '28%' }}>Share of pending</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {pending.classes.map((row) => (
                  <TableRow key={String(row.class_id)} hover>
                    <TableCell sx={{ fontWeight: 600 }}>{row.class_name}</TableCell>
                    <TableCell align="right">{row.students_with_dues}</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 700 }}>
                      {money(row.pending)}
                    </TableCell>
                    <TableCell align="right" sx={{ color: Number(row.overdue) > 0 ? 'error.main' : 'text.secondary', fontWeight: 600 }}>
                      {money(row.overdue)}
                    </TableCell>
                    <TableCell>
                      <LinearProgress variant="determinate" value={Number(pending.total_pending) > 0 ? (Number(row.pending) / Number(pending.total_pending)) * 100 : 0} />
                    </TableCell>
                  </TableRow>
                ))}
                <TableRow sx={{ '& td': { fontWeight: 800, borderBottom: 0, background: alpha(brand.primary, 0.05) } }}>
                  <TableCell>Total</TableCell>
                  <TableCell align="right">{pending.classes.reduce((total, row) => total + row.students_with_dues, 0)}</TableCell>
                  <TableCell align="right">{money(pending.total_pending)}</TableCell>
                  <TableCell align="right">{money(pending.total_overdue)}</TableCell>
                  <TableCell />
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Panel>

      <Panel>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
          <WarningIcon color="warning" />
          <Box sx={{ flexGrow: 1, minWidth: 220 }}>
            <Typography sx={{ fontWeight: 700 }}>Books check</Typography>
            <Typography variant="body2" color="text.secondary">
              Confirms that the paid amount on every due matches the payments recorded against it.
            </Typography>
          </Box>
          <Button variant="outlined" onClick={runCheck} disabled={checking} startIcon={<CheckIcon />}>
            {checking ? 'Checking…' : 'Run check'}
          </Button>
        </Box>
      </Panel>
      {node}
    </Box>
  );
};

export default FeeReportsTab;
