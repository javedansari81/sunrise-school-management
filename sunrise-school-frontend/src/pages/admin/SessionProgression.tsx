import React from 'react';
import AdminLayout from '../../components/Layout/AdminLayout';
import SessionProgressionSystem from '../../components/admin/SessionProgressionSystem';
import ServiceConfigurationLoader from '../../components/common/ServiceConfigurationLoader';

/**
 * SessionProgression Page - SUPER_ADMIN Only Feature
 *
 * Purpose: Manage student academic progression at the end of each session year
 * - Promote students to the next class level
 * - Retain students to repeat their current class
 * - Demote students to a lower class if necessary
 */
const SessionProgression: React.FC = () => {
  return (
    <AdminLayout>
      <ServiceConfigurationLoader service="session-progression">
        <SessionProgressionSystem />
      </ServiceConfigurationLoader>
    </AdminLayout>
  );
};

export default SessionProgression;

