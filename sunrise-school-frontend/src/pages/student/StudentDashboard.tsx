import React from 'react';
import StudentLayout from '../../components/Layout/StudentLayout';
import StudentDashboardOverview from '../../components/student/StudentDashboardOverview';

const StudentDashboard: React.FC = () => {
  return (
    <StudentLayout>
      <StudentDashboardOverview />
    </StudentLayout>
  );
};

export default StudentDashboard;
