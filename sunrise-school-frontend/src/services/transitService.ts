/** Transport operations module (/api/v1/transit): types, vehicles, routes, stops, rates, assignments. */
import api from './api';

export type RateBasis = 'PER_STOP' | 'DISTANCE_SLAB' | 'FLAT';
export const RATE_BASES: { value: RateBasis; label: string; hint: string }[] = [
  { value: 'FLAT', label: 'Flat per vehicle type', hint: 'One monthly amount for everyone on this vehicle type' },
  { value: 'DISTANCE_SLAB', label: 'Distance slab', hint: 'By how far the student lives, in km' },
  { value: 'PER_STOP', label: 'Per stop', hint: 'A fixed amount for one stop' },
];

export interface TransportType {
  id: number;
  name: string;
  description: string | null;
  capacity: number | null;
  sort_order: number;
  is_active: boolean;
}
export interface Vehicle {
  id: number;
  transport_type_id: number;
  registration_number: string;
  capacity: number | null;
  driver_name: string | null;
  driver_phone: string | null;
  remarks: string | null;
  is_active: boolean;
}
export interface Stop {
  id: number;
  route_id: number;
  name: string;
  sequence: number;
  distance_km: string | null;
  pickup_time: string | null;
  drop_time: string | null;
  is_active: boolean;
}
export interface Route {
  id: number;
  name: string;
  description: string | null;
  vehicle_id: number | null;
  is_active: boolean;
  stops: Stop[];
}
export interface Rate {
  id: number;
  session_year_id: number;
  basis: RateBasis;
  transport_type_id: number | null;
  route_stop_id: number | null;
  distance_from_km: string | null;
  distance_to_km: string | null;
  monthly_amount: string;
  description: string | null;
  is_active: boolean;
}
export interface Pause {
  id: number;
  from_period: string;
  to_period: string;
  reason: string | null;
  is_active: boolean;
}
export interface Assignment {
  id: number;
  student_id: number;
  session_year_id: number;
  transport_type_id: number;
  route_id: number | null;
  route_stop_id: number | null;
  distance_km: string | null;
  pickup_location: string | null;
  drop_location: string | null;
  start_date: string;
  end_date: string | null;
  monthly_amount: string;
  amount_overridden: boolean;
  is_active: boolean;
  end_reason: string | null;
  remarks: string | null;
  pauses: Pause[];
  student_name: string | null;
  admission_number: string | null;
}
export interface AssignmentResult {
  assignment: Assignment;
  warnings: string[];
}
export interface Rider {
  assignment_id: number;
  student_name: string;
  admission_number: string;
  class_name: string | null;
  paused: boolean;
}
export interface RouteRoster {
  route_id: number;
  route_name: string;
  vehicle: Vehicle | null;
  seats: number | null;
  on_date: string;
  riding: number;
  paused: number;
  over_capacity: boolean;
  stops: { stop: Stop | null; riders: Rider[] }[];
}

const data = <T>(promise: Promise<{ data: T }>): Promise<T> => promise.then((response) => response.data);
const clean = (params: Record<string, any>) =>
  Object.fromEntries(Object.entries(params).filter(([, value]) => value !== undefined && value !== null && value !== ''));

export const transitAPI = {
  listTypes: (includeInactive = true) =>
    data<TransportType[]>(api.get('/transit/transport-types', { params: { include_inactive: includeInactive } })),
  createType: (body: Record<string, any>) => data<TransportType>(api.post('/transit/transport-types', clean(body))),
  updateType: (id: number, body: Record<string, any>) =>
    data<TransportType>(api.patch(`/transit/transport-types/${id}`, body)),
  deleteType: (id: number) => api.delete(`/transit/transport-types/${id}`),

  listVehicles: (includeInactive = true) =>
    data<Vehicle[]>(api.get('/transit/vehicles', { params: { include_inactive: includeInactive } })),
  createVehicle: (body: Record<string, any>) => data<Vehicle>(api.post('/transit/vehicles', clean(body))),
  updateVehicle: (id: number, body: Record<string, any>) => data<Vehicle>(api.patch(`/transit/vehicles/${id}`, body)),
  deleteVehicle: (id: number) => api.delete(`/transit/vehicles/${id}`),

  listRoutes: (includeInactive = true) =>
    data<Route[]>(api.get('/transit/routes', { params: { include_inactive: includeInactive } })),
  createRoute: (body: Record<string, any>) => data<Route>(api.post('/transit/routes', clean(body))),
  updateRoute: (id: number, body: Record<string, any>) => data<Route>(api.patch(`/transit/routes/${id}`, body)),
  deleteRoute: (id: number) => api.delete(`/transit/routes/${id}`),
  addStop: (routeId: number, body: Record<string, any>) =>
    data<Stop>(api.post(`/transit/routes/${routeId}/stops`, clean(body))),
  updateStop: (stopId: number, body: Record<string, any>) => data<Stop>(api.patch(`/transit/stops/${stopId}`, body)),
  deleteStop: (stopId: number) => api.delete(`/transit/stops/${stopId}`),
  reorderStops: (routeId: number, stopIds: number[]) =>
    data<Route>(api.put(`/transit/routes/${routeId}/stops/order`, { stop_ids: stopIds })),
  routeRoster: (routeId: number, onDate?: string) =>
    data<RouteRoster>(api.get(`/transit/routes/${routeId}/roster`, { params: clean({ on_date: onDate }) })),

  listRates: (sessionYearId: number) =>
    data<Rate[]>(api.get('/transit/rates', { params: { session_year_id: sessionYearId, include_inactive: true } })),
  createRate: (body: Record<string, any>) => data<Rate>(api.post('/transit/rates', clean(body))),
  updateRate: (id: number, body: Record<string, any>) => data<Rate>(api.patch(`/transit/rates/${id}`, body)),
  deleteRate: (id: number) => api.delete(`/transit/rates/${id}`),
  copyRates: (fromSessionYearId: number, toSessionYearId: number) =>
    data<{ copied: number }>(
      api.post('/transit/rates/copy', { from_session_year_id: fromSessionYearId, to_session_year_id: toSessionYearId })
    ),
  quote: (body: Record<string, any>) =>
    data<{ monthly_amount: string | null; basis: string | null }>(api.post('/transit/rates/quote', clean(body))),

  listAssignments: (params: Record<string, any>) =>
    data<Assignment[]>(api.get('/transit/assignments', { params: clean(params) })),
  assign: (body: Record<string, any>) =>
    data<AssignmentResult>(api.post('/transit/assignments', clean(body), { timeout: 30000 })),
  change: (id: number, body: Record<string, any>) =>
    // Not cleaned: a null here clears the field, a missing one keeps it
    data<AssignmentResult>(api.post(`/transit/assignments/${id}/change`, body, { timeout: 30000 })),
  discontinue: (id: number, body: { end_date: string; reason?: string }) =>
    data<AssignmentResult>(api.post(`/transit/assignments/${id}/discontinue`, clean(body))),
  cancel: (id: number, reason: string) =>
    data<AssignmentResult>(api.post(`/transit/assignments/${id}/cancel`, { reason })),
  pause: (id: number, body: { from_period: string; to_period: string; reason?: string }) =>
    data<AssignmentResult>(api.post(`/transit/assignments/${id}/pauses`, clean(body))),
  removePause: (pauseId: number) => data<AssignmentResult>(api.delete(`/transit/pauses/${pauseId}`)),
};
