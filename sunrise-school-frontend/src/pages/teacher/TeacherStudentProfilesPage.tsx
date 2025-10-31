import React from 'react';
import TeacherLayout from '../../components/Layout/TeacherLayout';
import TeacherStudentProfiles from '../../components/teacher/TeacherStudentProfiles';

const TeacherStudentProfilesPage: React.FC = () => {
  return (
    <TeacherLayout>
      <TeacherStudentProfiles />
    </TeacherLayout>
  );
};

export default TeacherStudentProfilesPage;

