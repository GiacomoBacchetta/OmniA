import { Outlet, NavLink } from 'react-router-dom'
import { Archive, MessageSquare, Map, LogOut } from 'lucide-react'
import { useAuthStore } from '../store/authStore'

export default function Layout() {
  const logout = useAuthStore((state) => state.logout)

  const navLinks = [
    { to: '/archive', icon: Archive, label: 'Archive' },
    { to: '/agent', icon: MessageSquare, label: 'Agent' },
    { to: '/map', icon: Map, label: 'Map' },
  ]

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-6">
          <h1 className="text-2xl font-bold text-primary-600">OmniA</h1>
          <p className="text-sm text-gray-500 mt-1">Your Personal Archive</p>
        </div>

        <nav className="flex-1 px-4 space-y-2">
          {navLinks.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-full transition-colors ${
                  isActive
                    ? 'bg-primary-50 text-primary-600 font-medium'
                    : 'text-gray-700 hover:bg-gray-100'
                }`
              }
            >
              <link.icon size={20} />
              {link.label}
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-gray-200">
          <button
            onClick={logout}
            className="flex items-center gap-3 px-4 py-3 w-full rounded-full text-gray-700 hover:bg-gray-100 transition-colors"
          >
            <LogOut size={20} />
            Logout
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        <Outlet />
      </div>
    </div>
  )
}
