/** The school admin's Settings screen (/api/v1/school-settings): profile, settings and the school's own lists. */
import api from './api';

export interface SchoolProfile {
  code: string;
  name: string;
  short_name: string | null;
  address: string | null;
  phone: string | null;
  email: string | null;
  website: string | null;
  logo_url: string | null;
  currency: string;
  timezone: string;
  academic_year_start_month: number;
}

export type SettingType = 'bool' | 'int' | 'decimal' | 'text' | 'choice';

export interface SettingValue {
  key: string;
  label: string;
  group: string;
  type: SettingType;
  /** Used while no value is stored. */
  default: string | null;
  help: string;
  choices: string[];
  min: number | null;
  max: number | null;
  /** Null: the default applies. */
  value: string | null;
}

export type ListFieldType = 'text' | 'int' | 'decimal' | 'date' | 'bool' | 'ref';

export interface ListField {
  name: string;
  label: string;
  type: ListFieldType;
  required: boolean;
  max_length: number | null;
  help: string;
  /** For a ref field: the list it points at. */
  ref: string | null;
}

export interface ListKind {
  kind: string;
  label: string;
  group: string;
  hint: string;
  fields: ListField[];
}

export type ListRow = { id: number; is_active: boolean } & Record<string, any>;

export const SHOP_SETTING = 'module.shop.enabled';

export const schoolSettingsAPI = {
  getProfile: (): Promise<SchoolProfile> => api.get('/school-settings/profile').then((r) => r.data),
  updateProfile: (body: Partial<SchoolProfile>): Promise<SchoolProfile> => api.patch('/school-settings/profile', body).then((r) => r.data),

  listValues: (): Promise<SettingValue[]> => api.get('/school-settings/values').then((r) => r.data),
  /** Null resets the setting to its default. */
  setValue: (key: string, value: string | boolean | null): Promise<SettingValue> =>
    api.put(`/school-settings/values/${encodeURIComponent(key)}`, { value }).then((r) => r.data),

  listKinds: (): Promise<ListKind[]> => api.get('/school-settings/lists').then((r) => r.data),
  listRows: (kind: string): Promise<ListRow[]> => api.get(`/school-settings/lists/${kind}`).then((r) => r.data),
  createRow: (kind: string, body: Record<string, any>): Promise<ListRow> => api.post(`/school-settings/lists/${kind}`, body).then((r) => r.data),
  updateRow: (kind: string, id: number, body: Record<string, any>): Promise<ListRow> =>
    api.patch(`/school-settings/lists/${kind}/${id}`, body).then((r) => r.data),
};
