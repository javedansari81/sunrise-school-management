/** Shows a School Shop page only when the school turned the shop on in Settings. */
import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { Button } from '@mui/material';
import { Storefront as StorefrontIcon } from '@mui/icons-material';
import AdminLayout from './Layout/AdminLayout';
import { EmptyState, Loading, Panel } from './ui';
import { useSchool } from '../contexts/SchoolContext';

const ShopRoute: React.FC<{ children: React.ReactElement }> = ({ children }) => {
  const { school, ready } = useSchool();
  if (school.features.shop) return children;

  return (
    <AdminLayout>
      {!ready ? (
        <Loading />
      ) : (
        <Panel>
          <EmptyState
            icon={<StorefrontIcon />}
            title="The School Shop is turned off"
            hint="Turn it on under Settings, Modules and settings, to sell uniforms and books and track stock."
            action={
              <Button component={RouterLink} to="/admin/settings" variant="contained">
                Open Settings
              </Button>
            }
          />
        </Panel>
      )}
    </AdminLayout>
  );
};

export default ShopRoute;
