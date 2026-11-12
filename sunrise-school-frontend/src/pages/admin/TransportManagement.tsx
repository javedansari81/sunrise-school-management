import React, { useCallback, useEffect, useState } from 'react';
import { Alert } from '@mui/material';
import {
  AirportShuttle as VehiclesIcon,
  DirectionsBus as BusIcon,
  Groups as RidersIcon,
  PriceChange as RatesIcon,
  Route as RoutesIcon,
} from '@mui/icons-material';
import AdminLayout from '../../components/Layout/AdminLayout';
import { apiError, Loading, PageHero, PillTabs, StatCard, StatGrid } from '../../components/ui';
import AssignmentsTab from '../../components/transit/AssignmentsTab';
import RoutesTab from '../../components/transit/RoutesTab';
import VehiclesTab from '../../components/transit/VehiclesTab';
import RatesTab from '../../components/transit/RatesTab';
import { Route, transitAPI, TransportType, Vehicle } from '../../services/transitService';
import { useLookups } from '../../hooks/useLookups';

const TABS = [
  { value: 'riders', label: 'Riders', icon: <RidersIcon fontSize="small" /> },
  { value: 'routes', label: 'Routes and stops', icon: <RoutesIcon fontSize="small" /> },
  { value: 'vehicles', label: 'Vehicles', icon: <VehiclesIcon fontSize="small" /> },
  { value: 'rates', label: 'Rates', icon: <RatesIcon fontSize="small" /> },
];

const TransportContent: React.FC = () => {
  const lookups = useLookups();
  const [tab, setTab] = useState('riders');
  const [types, setTypes] = useState<TransportType[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [routes, setRoutes] = useState<Route[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async () => {
    try {
      const [nextTypes, nextVehicles, nextRoutes] = await Promise.all([transitAPI.listTypes(), transitAPI.listVehicles(), transitAPI.listRoutes()]);
      setTypes(nextTypes);
      setVehicles(nextVehicles);
      setRoutes(nextRoutes);
      setError(null);
    } catch (failure) {
      setError(apiError(failure));
    } finally {
      setLoaded(true);
    }
  }, []);

  useEffect(() => {
    reload();
  }, [reload]);

  const activeRoutes = routes.filter((route) => route.is_active);

  return (
    <>
      <PageHero
        icon={<BusIcon />}
        title="Transport"
        subtitle="Routes, stops, vehicles and who rides what. Transport fees are billed and collected with every other fee on the Fees page."
      />
      {loaded && (
        <StatGrid min={170}>
          <StatCard label="Routes" value={activeRoutes.length} hint="in use" icon={<RoutesIcon />} tone="blue" />
          <StatCard label="Stops" value={activeRoutes.reduce((total, route) => total + route.stops.filter((stop) => stop.is_active).length, 0)} hint="on those routes" icon={<RidersIcon />} tone="violet" delay={60} />
          <StatCard label="Vehicles" value={vehicles.filter((vehicle) => vehicle.is_active).length} hint="in use" icon={<BusIcon />} tone="green" delay={120} />
          <StatCard label="Vehicle types" value={types.filter((type) => type.is_active).length} hint="with their own rates" icon={<VehiclesIcon />} tone="orange" delay={180} />
        </StatGrid>
      )}
      <PillTabs value={tab} onChange={setTab} tabs={TABS} />
      {(error || lookups.error) && <Alert severity="error" sx={{ mb: 2 }}>{error || lookups.error}</Alert>}
      {!lookups.ready || !loaded ? (
        <Loading />
      ) : (
        <div key={tab} className="fade-up">
          {tab === 'riders' && <AssignmentsTab lookups={lookups} types={types} vehicles={vehicles} routes={routes} />}
          {tab === 'routes' && <RoutesTab types={types} vehicles={vehicles} routes={routes} reload={reload} />}
          {tab === 'vehicles' && <VehiclesTab types={types} vehicles={vehicles} routes={routes} reload={reload} />}
          {tab === 'rates' && <RatesTab lookups={lookups} types={types} routes={routes} />}
        </div>
      )}
    </>
  );
};

const TransportManagement: React.FC = () => (
  <AdminLayout>
    <TransportContent />
  </AdminLayout>
);

export default TransportManagement;
