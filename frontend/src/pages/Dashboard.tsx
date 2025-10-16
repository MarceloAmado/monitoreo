/**
 * Página Dashboard - Lista de devices con su estado
 */

import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Layout } from '@/components/layout/Layout';
import deviceService from '@/services/deviceService';
import type { Device } from '@/types';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';

export const Dashboard = () => {
  const { data: devices, isLoading, error } = useQuery<Device[]>({
    queryKey: ['devices'],
    queryFn: () => deviceService.getDevices(),
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return 'badge-green';
      case 'inactive':
        return 'badge-gray';
      case 'maintenance':
        return 'badge-yellow';
      case 'error':
        return 'badge-red';
      default:
        return 'badge-gray';
    }
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      active: 'Activo',
      inactive: 'Inactivo',
      maintenance: 'Mantenimiento',
      error: 'Error',
    };
    return labels[status] || status;
  };

  const isOnline = (lastSeenAt: string | null) => {
    if (!lastSeenAt) return false;
    const lastSeen = new Date(lastSeenAt);
    const now = new Date();
    const diffMinutes = (now.getTime() - lastSeen.getTime()) / (1000 * 60);
    return diffMinutes < 10; // Online si visto hace menos de 10 minutos
  };

  if (isLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            <p className="mt-4 text-gray-600">Cargando dispositivos...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
          <p>Error al cargar dispositivos. Intenta nuevamente.</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">
          Monitoreo de dispositivos IoT en tiempo real
        </p>
      </div>

      {/* Estadísticas rápidas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="card">
          <p className="text-gray-600 text-sm">Total Dispositivos</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">
            {devices?.length || 0}
          </p>
        </div>
        <div className="card">
          <p className="text-gray-600 text-sm">En Línea</p>
          <p className="text-3xl font-bold text-green-600 mt-2">
            {devices?.filter(d => isOnline(d.last_seen_at)).length || 0}
          </p>
        </div>
        <div className="card">
          <p className="text-gray-600 text-sm">Fuera de Línea</p>
          <p className="text-3xl font-bold text-red-600 mt-2">
            {devices?.filter(d => !isOnline(d.last_seen_at)).length || 0}
          </p>
        </div>
        <div className="card">
          <p className="text-gray-600 text-sm">En Mantenimiento</p>
          <p className="text-3xl font-bold text-yellow-600 mt-2">
            {devices?.filter(d => d.status === 'maintenance').length || 0}
          </p>
        </div>
      </div>

      {/* Tabla de devices */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Dispositivos</h2>

        {devices && devices.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Dispositivo
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    EUI
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Estado
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Conexión
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Última Actividad
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {devices.map((device) => (
                  <tr key={device.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {device.name}
                        </div>
                        {device.firmware_version && (
                          <div className="text-sm text-gray-500">
                            v{device.firmware_version}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {device.device_eui}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={getStatusBadge(device.status)}>
                        {getStatusLabel(device.status)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {isOnline(device.last_seen_at) ? (
                        <span className="badge-green">En línea</span>
                      ) : (
                        <span className="badge-red">Fuera de línea</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {device.last_seen_at
                        ? formatDistanceToNow(new Date(device.last_seen_at), {
                            addSuffix: true,
                            locale: es,
                          })
                        : 'Nunca'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <Link
                        to={`/devices/${device.id}`}
                        className="text-primary-600 hover:text-primary-900 font-medium"
                      >
                        Ver detalles →
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-500">
              No hay dispositivos registrados.
            </p>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Dashboard;
