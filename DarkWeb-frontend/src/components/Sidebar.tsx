import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  TrendingUp,
  PieChart,
  FileText,
  Globe,
  Activity,
  Brain,
  Shield,
  Calendar,
} from "lucide-react";
import { motion } from 'framer-motion';

const navItems = [
  { path: "/", icon: LayoutDashboard, label: "Daily Domains" },
  { path: "/keywords", icon: TrendingUp, label: "Keyword Trends" },
  // { path: '/categories', icon: PieChart, label: 'Categories' },
  { path: "/titles", icon: FileText, label: "Grouped Titles" },
  { path: "/sources", icon: Globe, label: "Source Summary" },
  { path: "/trends", icon: Activity, label: "Time Trends" },
  // { path: "/daily-domains", icon: Calendar, label: "Daily Domains" },
  // { path: '/insights', icon: Brain, label: 'AI Insights' },
];

export function Sidebar() {
  return (
    <motion.aside
      initial={{ x: -300 }}
      animate={{ x: 0 }}
      transition={{ duration: 0.5, type: 'spring' }}
      className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col"
    >
      <div className="p-6 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">Dark Web</h1>
            <p className="text-xs text-gray-400">Analytics Dashboard</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item, index) => (
          <motion.div
            key={item.path}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
          >
            <NavLink
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${isActive
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/30'
                  : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                }`
              }
            >
              <item.icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </NavLink>
          </motion.div>
        ))}
      </nav>

      <div className="p-4 border-t border-gray-800">
        <div className="px-4 py-3 bg-gray-800 rounded-lg">
          <p className="text-xs text-gray-400">Version 1.0.0</p>
          <p className="text-xs text-gray-500 mt-1">Security Analytics Platform</p>
        </div>
      </div>
    </motion.aside>
  );
}
