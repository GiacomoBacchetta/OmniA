import { Outlet, NavLink } from 'react-router-dom'
import { Archive, MessageSquare, Map, LogOut, Sparkles } from 'lucide-react'
import { useAuthStore } from '../store/authStore'

export default function Layout() {
  const logout = useAuthStore((state) => state.logout)

  const navLinks = [
    { to: '/archive', icon: Archive, label: 'Archive' },
    { to: '/agent', icon: MessageSquare, label: 'Agent' },
    { to: '/map', icon: Map, label: 'Map' },
  ]

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Top Navigation Bar */}
      <nav className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 shadow-lg">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <div className="flex items-center gap-2">
              <div className="bg-white/20 backdrop-blur-sm p-2 rounded-lg">
                <Sparkles className="text-white" size={24} />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">OmniA</h1>
                <p className="text-xs text-white/80">Your Personal Archive</p>
              </div>
            </div>

            {/* Navigation Links */}
            <div className="flex items-center gap-2">
              {navLinks.map((link) => (
                <NavLink
                  key={link.to}
                  to={link.to}
                  className={({ isActive }) =>
                    `flex items-center gap-2 px-5 py-2.5 rounded-lg transition-all duration-200 ${
                      isActive
                        ? 'bg-white text-blue-600 font-semibold shadow-md'
                        : 'text-white hover:bg-white/20 backdrop-blur-sm'
                    }`
                  }
                >
                  <link.icon size={20} />
                  <span className="font-medium">{link.label}</span>
                </NavLink>
              ))}
            </div>

            {/* Logout Button */}
            <button
              onClick={logout}
              className="flex items-center gap-2 px-5 py-2.5 rounded-lg text-white hover:bg-white/20 backdrop-blur-sm transition-all duration-200"
            >
              <LogOut size={20} />
              <span className="font-medium">Logout</span>
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        <Outlet />
      </div>
    </div>
  )
}
