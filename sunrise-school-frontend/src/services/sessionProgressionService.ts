/**
 * Session Progression Service
 * Provides API calls for session progression management
 * Allows SUPER_ADMIN to promote, retain, demote, or graduate students between sessions
 */

import api from './api';
import {
  StudentProgressionPreviewRequest,
  StudentProgressionPreviewResponse,
  BulkProgressionRequest,
  BulkProgressionResponse,
  StudentProgressionHistoryResponse,
  RollbackRequest,
  RollbackResponse,
  ProgressionReportResponse,
} from '../types/sessionProgression';

/**
 * Session Progression API service
 */
export const sessionProgressionAPI = {
  /**
   * Preview eligible students for progression from one session to another
   * Shows suggested actions based on current class (PROMOTED for most, GRADUATED for Class 8)
   */
  previewEligibleStudents: async (
    request: StudentProgressionPreviewRequest
  ): Promise<StudentProgressionPreviewResponse> => {
    const response = await api.post('/session-progression/preview', request);
    return response.data;
  },

  /**
   * Bulk progress students from one session to another
   * Requires SUPER_ADMIN role
   */
  bulkProgressStudents: async (
    request: BulkProgressionRequest
  ): Promise<BulkProgressionResponse> => {
    const response = await api.post('/session-progression/bulk-progress', request);
    return response.data;
  },

  /**
   * Get progression history for a specific student
   * Shows all sessions the student has been part of with their progression actions
   */
  getStudentHistory: async (
    studentId: number
  ): Promise<StudentProgressionHistoryResponse> => {
    const response = await api.get(`/session-progression/history/${studentId}`);
    return response.data;
  },

  /**
   * Rollback a progression batch
   * Reverts all student progressions in the specified batch
   * Requires SUPER_ADMIN role
   */
  rollbackBatch: async (
    request: RollbackRequest
  ): Promise<RollbackResponse> => {
    const response = await api.post('/session-progression/rollback', request);
    return response.data;
  },

  /**
   * Get progression report for a session year
   * Shows summary statistics of student progression actions
   */
  getProgressionReport: async (
    sessionYearId: number,
    classIds?: number[]
  ): Promise<ProgressionReportResponse> => {
    const queryParams = new URLSearchParams();
    queryParams.append('session_year_id', String(sessionYearId));
    if (classIds && classIds.length > 0) {
      classIds.forEach(id => queryParams.append('class_ids', String(id)));
    }
    const response = await api.get(`/session-progression/report?${queryParams.toString()}`);
    return response.data;
  },
};

export default sessionProgressionAPI;

