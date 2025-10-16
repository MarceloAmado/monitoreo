/**
 * Servicio para manejo de devices.
 */

import api from './api';
import type { Device, DeviceSchema } from '@/types';

export const deviceService = {
  /**
   * Obtener lista de devices
   */
  async getDevices(): Promise<Device[]> {
    const response = await api.get<Device[]>('/devices');
    return response.data;
  },

  /**
   * Obtener un device por ID
   */
  async getDevice(deviceId: number): Promise<Device> {
    const response = await api.get<Device>(`/devices/${deviceId}`);
    return response.data;
  },

  /**
   * Obtener schema de un device (para gráficos dinámicos)
   */
  async getDeviceSchema(deviceId: number): Promise<DeviceSchema> {
    const response = await api.get<DeviceSchema>(`/devices/${deviceId}/schema`);
    return response.data;
  },

  /**
   * Crear nuevo device (solo admins)
   */
  async createDevice(device: Partial<Device>): Promise<Device> {
    const response = await api.post<Device>('/devices', device);
    return response.data;
  },

  /**
   * Actualizar device
   */
  async updateDevice(deviceId: number, updates: Partial<Device>): Promise<Device> {
    const response = await api.patch<Device>(`/devices/${deviceId}`, updates);
    return response.data;
  },

  /**
   * Eliminar device
   */
  async deleteDevice(deviceId: number): Promise<void> {
    await api.delete(`/devices/${deviceId}`);
  },
};

export default deviceService;
