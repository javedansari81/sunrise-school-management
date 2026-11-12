import React, { useCallback, useEffect, useState } from 'react';
import { Alert } from '@mui/material';
import {
  Assessment as ReportsIcon,
  AttachMoney as MoneyIcon,
  Category as HeadsIcon,
  ListAlt as StructuresIcon,
  LocalOffer as ConcessionsIcon,
  PlayCircle as RunIcon,
  PointOfSale as DeskIcon,
} from '@mui/icons-material';
import AdminLayout from '../../components/Layout/AdminLayout';
import { apiError, Loading, PageHero, PillTabs } from '../../components/ui';
import FeeDeskTab from '../../components/billing/FeeDeskTab';
import FeeHeadsTab from '../../components/billing/FeeHeadsTab';
import FeeStructuresTab from '../../components/billing/FeeStructuresTab';
import ConcessionsTab from '../../components/billing/ConcessionsTab';
import BillingRunTab from '../../components/billing/BillingRunTab';
import FeeReportsTab from '../../components/billing/FeeReportsTab';
import { billingAPI, FeeHead } from '../../services/billingService';
import { useLookups } from '../../hooks/useLookups';

const TABS = [
  { value: 'desk', label: 'Collect', icon: <DeskIcon fontSize="small" /> },
  { value: 'structures', label: 'Fee structures', icon: <StructuresIcon fontSize="small" /> },
  { value: 'heads', label: 'Fee heads', icon: <HeadsIcon fontSize="small" /> },
  { value: 'concessions', label: 'Concessions', icon: <ConcessionsIcon fontSize="small" /> },
  { value: 'run', label: 'Billing run', icon: <RunIcon fontSize="small" /> },
  { value: 'reports', label: 'Reports', icon: <ReportsIcon fontSize="small" /> },
];

const FeesContent: React.FC = () => {
  const lookups = useLookups();
  const [tab, setTab] = useState('desk');
  const [heads, setHeads] = useState<FeeHead[]>([]);
  const [headsError, setHeadsError] = useState<string | null>(null);

  const loadHeads = useCallback(async () => {
    try {
      setHeads(await billingAPI.listHeads(true));
      setHeadsError(null);
    } catch (failure) {
      setHeadsError(apiError(failure));
    }
  }, []);

  useEffect(() => {
    loadHeads();
  }, [loadHeads]);

  return (
    <>
      <PageHero
        icon={<MoneyIcon />}
        title="Fees"
        subtitle="Tuition, transport, admission, exam and one-off charges: billed, collected and receipted in one place."
      />
      <PillTabs value={tab} onChange={setTab} tabs={TABS} />
      {lookups.error && <Alert severity="error" sx={{ mb: 2 }}>{lookups.error}</Alert>}
      {headsError && <Alert severity="error" sx={{ mb: 2 }}>{headsError}</Alert>}
      {!lookups.ready ? (
        <Loading label="Loading the school's lists…" />
      ) : (
        <div key={tab} className="fade-up">
          {tab === 'desk' && <FeeDeskTab lookups={lookups} heads={heads} />}
          {tab === 'structures' && <FeeStructuresTab lookups={lookups} heads={heads} />}
          {tab === 'heads' && <FeeHeadsTab heads={heads} reload={loadHeads} />}
          {tab === 'concessions' && <ConcessionsTab heads={heads} />}
          {tab === 'run' && <BillingRunTab lookups={lookups} />}
          {tab === 'reports' && <FeeReportsTab lookups={lookups} />}
        </div>
      )}
    </>
  );
};

const FeesManagement: React.FC = () => (
  <AdminLayout>
    <FeesContent />
  </AdminLayout>
);

export default FeesManagement;
