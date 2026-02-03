/**
 * TypeScript types for Session Progression feature
 * Matches backend schemas in sunrise-backend-fastapi/app/schemas/session_progression.py
 */

// Progression Action metadata
export interface ProgressionAction {
  id: number;
  name: string;
  description?: string;
  display_order: number;
  icon?: string;
  color_code?: string;
  is_positive: boolean;
  creates_new_session: boolean;
  is_active: boolean;
}

// Student preview item for progression
export interface StudentProgressionPreviewItem {
  student_id: number;
  admission_number: string;
  first_name: string;
  last_name: string;
  current_class_id: number;
  current_class_name: string;
  current_section?: string;
  current_roll_number?: string;
  suggested_action_id: number;
  suggested_action_name: string;
  target_class_id?: number;
  target_class_name?: string;
}

// Preview request
export interface StudentProgressionPreviewRequest {
  from_session_year_id: number;
  to_session_year_id: number;
  class_ids?: number[];
}

// Preview response
export interface StudentProgressionPreviewResponse {
  from_session_year_id: number;
  from_session_year_name: string;
  to_session_year_id: number;
  to_session_year_name: string;
  total_students: number;
  students: StudentProgressionPreviewItem[];
}

// Student item for bulk progression request
export interface StudentProgressionItem {
  student_id: number;
  progression_action_id: number;
  target_class_id?: number;
  target_section?: string;
  target_roll_number?: string;
  remarks?: string;
}

// Bulk progression request
export interface BulkProgressionRequest {
  from_session_year_id: number;
  to_session_year_id: number;
  students: StudentProgressionItem[];
}

// Result item for bulk progression
export interface BulkProgressionResultItem {
  student_id: number;
  success: boolean;
  admission_number?: string;
  student_name?: string;
  progression_action_name?: string;
  error_message?: string;
}

// Bulk progression response
export interface BulkProgressionResponse {
  batch_id: string;
  from_session_year_id: number;
  to_session_year_id: number;
  total_processed: number;
  successful_count: number;
  failed_count: number;
  results: BulkProgressionResultItem[];
  processed_at: string;
}

// Student progression history item
export interface StudentProgressionHistoryItem {
  id: number;
  session_year_id: number;
  session_year_name?: string;
  class_id: number;
  class_name?: string;
  section?: string;
  roll_number?: string;
  progression_action_id: number;
  progression_action_name?: string;
  from_session_year_id?: number;
  from_session_year_name?: string;
  from_class_id?: number;
  from_class_name?: string;
  progression_batch_id?: string;
  progressed_by: number;
  progressed_by_name?: string;
  progressed_at: string;
  remarks?: string;
}

// Student history response
export interface StudentProgressionHistoryResponse {
  student_id: number;
  total_records: number;
  history: StudentProgressionHistoryItem[];
}

// Rollback request
export interface RollbackRequest {
  batch_id: string;
  reason?: string;
}

// Rollback response
export interface RollbackResponse {
  batch_id: string;
  students_affected: number;
  success: boolean;
  message: string;
  rolled_back_at?: string;
}

// Progression report action stats
export interface ProgressionActionStats {
  action_id: number;
  action_name: string;
  action_icon?: string;
  action_color?: string;
  count: number;
}

// Progression report response
export interface ProgressionReportResponse {
  session_year_id: number;
  session_year_name?: string;
  total_students_progressed: number;
  by_action: ProgressionActionStats[];
  generated_at: string;
}

// Progression action IDs (from database)
// Only PROMOTED, RETAINED, DEMOTED are supported for session progression
export const PROGRESSION_ACTION_IDS = {
  PROMOTED: 1,
  RETAINED: 2,
  DEMOTED: 3,
} as const;

// Highest class ID (Class 8)
export const HIGHEST_CLASS_ID = 12;

