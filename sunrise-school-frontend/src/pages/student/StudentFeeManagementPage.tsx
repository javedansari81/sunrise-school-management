import React from 'react';
import StudentLayout from '../../components/Layout/StudentLayout';
import StudentFeeManagement from '../../components/student/StudentFeeManagement';

const StudentFeeManagementPage: React.FC = () => {
  return (
    <StudentLayout>
      <StudentFeeManagement />
    </StudentLayout>
  );
};

export default StudentFeeManagementPage;

