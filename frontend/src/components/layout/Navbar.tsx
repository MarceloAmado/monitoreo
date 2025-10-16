/**
 * Navbar superior con información del usuario y logout
 */

import { useAuth } from '@/hooks/useAuth';

export const Navbar = () => {
  const { user, logout } = useAuth();

  const getRoleBadgeClass = (role: string) => {
    switch (role) {
      case 'super_admin':
        return 'badge-red';
      case 'service_admin':
        return 'badge-yellow';
      case 'technician':
        return 'badge-green';
      default:
        return 'badge-gray';
    }
  };

  const getRoleLabel = (role: string) => {
    switch (role) {
      case 'super_admin':
        return 'Super Admin';
      case 'service_admin':
        return 'Administrador';
      case 'technician':
        return 'Técnico';
      case 'guest':
        return 'Invitado';
      default:
        return role;
    }
  };

  return (
    <nav className="bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <h1 className="text-xl font-bold text-primary-600">
              IoT Monitoring
            </h1>
          </div>

          <div className="flex items-center space-x-4">
            {user && (
              <>
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-700">
                    {user.first_name} {user.last_name}
                  </p>
                  <p className="text-xs text-gray-500">{user.email}</p>
                </div>
                <span className={getRoleBadgeClass(user.role)}>
                  {getRoleLabel(user.role)}
                </span>
                <button
                  onClick={logout}
                  className="btn-secondary text-sm"
                >
                  Salir
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
