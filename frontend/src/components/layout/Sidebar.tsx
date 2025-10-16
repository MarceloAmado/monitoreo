/**
 * Sidebar con navegación principal
 */

import { Link, useLocation } from 'react-router-dom';

export const Sidebar = () => {
  const location = useLocation();

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: '📊' },
    { path: '/devices', label: 'Dispositivos', icon: '📡' },
    { path: '/alerts', label: 'Alertas', icon: '🔔' },
    { path: '/settings', label: 'Configuración', icon: '⚙️' },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <aside className="w-64 bg-white shadow-md min-h-screen">
      <nav className="mt-5 px-2">
        <div className="space-y-1">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`
                group flex items-center px-4 py-3 text-sm font-medium rounded-md transition-colors
                ${
                  isActive(item.path)
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }
              `}
            >
              <span className="mr-3 text-xl">{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </div>
      </nav>
    </aside>
  );
};

export default Sidebar;
