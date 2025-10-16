/**
 * Página de detalle de un device con gráfico de temperatura
 */

import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Layout } from '@/components/layout/Layout';
import deviceService from '@/services/deviceService';
import readingService from '@/services/readingService';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

export const DeviceDetail = () => {
  const { id } = useParams<{ id: string }>();
  const deviceId = parseInt(id || '0');

  const { data: device, isLoading: deviceLoading } = useQuery({
    queryKey: ['device', deviceId],
    queryFn: () => deviceService.getDevice(deviceId),
  });

  const { data: readings, isLoading: readingsLoading } = useQuery({
    queryKey: ['readings', deviceId, '24h'],
    queryFn: () => readingService.getDeviceReadings(deviceId, '24h'),
  });

  if (deviceLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      </Layout>
    );
  }

  if (!device) {
    return (
      <Layout>
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
          <p>Dispositivo no encontrado</p>
        </div>
      </Layout>
    );
  }

  // Preparar datos para el gráfico
  const chartData = readings?.map((r) => ({
    timestamp: format(new Date(r.timestamp), 'HH:mm', { locale: es }),
    temp_c: r.data_payload.temp_c || null,
    humidity_pct: r.data_payload.humidity_pct || null,
  })) || [];

  return (
    <Layout>
      <div className="mb-6">
        <Link to="/dashboard" className="text-primary-600 hover:text-primary-800 text-sm">
          ← Volver al Dashboard
        </Link>
        <h1 className="text-3xl font-bold text-gray-900 mt-2">{device.name}</h1>
        <p className="text-gray-600">{device.device_eui}</p>
      </div>

      {/* Información del device */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="card">
          <p className="text-gray-600 text-sm">Estado</p>
          <p className="text-xl font-semibold mt-2">{device.status}</p>
        </div>
        <div className="card">
          <p className="text-gray-600 text-sm">Firmware</p>
          <p className="text-xl font-semibold mt-2">
            {device.firmware_version || 'N/A'}
          </p>
        </div>
        <div className="card">
          <p className="text-gray-600 text-sm">Última Actividad</p>
          <p className="text-xl font-semibold mt-2">
            {device.last_seen_at
              ? format(new Date(device.last_seen_at), 'dd/MM/yyyy HH:mm')
              : 'Nunca'}
          </p>
        </div>
      </div>

      {/* Gráfico */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">
          Temperatura y Humedad (Últimas 24 horas)
        </h2>

        {readingsLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Legend />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="temp_c"
                stroke="#ff6b6b"
                name="Temperatura (°C)"
                dot={false}
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="humidity_pct"
                stroke="#4ecdc4"
                name="Humedad (%)"
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="text-center py-12 text-gray-500">
            No hay datos disponibles para las últimas 24 horas
          </div>
        )}
      </div>

      {/* Tabla de readings recientes */}
      <div className="card mt-6">
        <h2 className="text-xl font-semibold mb-4">Lecturas Recientes</h2>
        {readings && readings.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Timestamp
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Temperatura
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Humedad
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Calidad
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {readings.slice(0, 10).map((reading) => (
                  <tr key={reading.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {format(new Date(reading.timestamp), 'dd/MM/yyyy HH:mm:ss')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {reading.data_payload.temp_c?.toFixed(1) || '-'} °C
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {reading.data_payload.humidity_pct?.toFixed(1) || '-'} %
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={
                          (reading.quality_score || 0) > 0.7
                            ? 'badge-green'
                            : 'badge-yellow'
                        }
                      >
                        {((reading.quality_score || 0) * 100).toFixed(0)}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-center py-8 text-gray-500">
            No hay lecturas disponibles
          </p>
        )}
      </div>
    </Layout>
  );
};

export default DeviceDetail;
