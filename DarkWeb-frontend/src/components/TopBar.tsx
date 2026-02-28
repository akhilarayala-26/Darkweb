import { Calendar, Download, Settings, User } from "lucide-react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";

interface TopBarProps {
  title: string;
  showDateFilter?: boolean;
  onDateFilterChange?: (range: string) => void;
}

export function TopBar({ title, showDateFilter = true }: TopBarProps) {
  const navigate = useNavigate();

  return (
    <motion.div
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.4 }}
      className="bg-gray-900 border-b border-gray-800 px-8 py-4"
    >
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">{title}</h2>
          <p className="text-sm text-gray-400 mt-1">
            Monitor and analyze dark web data
          </p>
        </div>

        <div className="flex items-center gap-4">
          {showDateFilter && (
            <button className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg transition-colors border border-gray-700">
              <Calendar className="w-4 h-4" />
              <span className="text-sm">14 Days</span>
            </button>
          )}

          <button className="p-2 hover:bg-gray-800 text-gray-400 rounded-lg transition-colors">
            <Download className="w-5 h-5" />
          </button>

          <button
            onClick={() => navigate("/admin")}
            className="p-2 hover:bg-gray-800 text-gray-400 rounded-lg transition-colors"
          >
            <Settings className="w-5 h-5" />
          </button>

          <button
            onClick={() => navigate("/admin")}
            className="flex items-center gap-2 px-3 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg transition-colors border border-gray-700"
          >
            <User className="w-4 h-4" />
            <span className="text-sm">Admin</span>
          </button>
        </div>
      </div>
    </motion.div>
  );
}
