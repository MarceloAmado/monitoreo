// Tipos base del sistema

export interface User {
  id: number;
  email: string;
  role: 'super_admin' | 'service_admin' | 'technician' | 'guest';
  first_name: string;
  last_name: string;
  is_active: boolean;
  allowed_location_ids: number[] | null;
  created_at: string;
  last_login_at: string | null;
}

export interface Device {
  id: number;
  asset_id: number | null;
  device_eui: string;
  name: string;
  status: 'active' | 'inactive' | 'maintenance' | 'error';
  firmware_version: string | null;
  last_seen_at: string | null;
  config: Record<string, any> | null;
  extra_data: Record<string, any> | null;
  created_at: string;
}

export interface SensorReading {
  id: number;
  device_id: number;
  data_payload: Record<string, any>;
  quality_score: number | null;
  processed: boolean;
  timestamp: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface DeviceVariable {
  key: string;
  label: string;
  unit: string;
  type: string;
  color?: string;
}

export interface DeviceSchema {
  device_id: number;
  variables: DeviceVariable[];
}

export interface Alert {
  id: number;
  device_id: number;
  triggered_at: string;
  message: string;
  value_observed: number | null;
}
