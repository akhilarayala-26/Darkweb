import { useEffect, useState } from 'react';
import { Card } from '../components/Card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Globe, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { motion } from 'framer-motion';

interface SourceData {
  source: string;
  total_entries: number;
  unique_titles: number;
  trend: string;
}

export function SourceSummary() {
  const [sources, setSources] = useState<SourceData[]>([]);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState<'entries' | 'titles'>('entries');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  useEffect(() => {
    fetchSources();
  }, []);
  const truncateText = (text: string, maxLength: number) => {
    return text.length > maxLength ? text.slice(0, maxLength) + "..." : text;
  };
  const fetchSources = async () => {
    try {
      const response = await fetch(
        "http://localhost:8000/analytics/source-summary"
      );
      const json = await response.json();
      if (json.sources) {
        setSources(json.sources);
      }
      console.log(json.sources)
    } catch (error) {
      console.error("Error fetching sources:", error);
    } finally {
      setLoading(false);
    }
  };


  const getSortedSources = () => {
    const sorted = [...sources].sort((a, b) => {
      const aValue = sortBy === 'entries' ? a.total_entries : a.unique_titles;
      const bValue = sortBy === 'entries' ? b.total_entries : b.unique_titles;
      return sortOrder === 'asc' ? aValue - bValue : bValue - aValue;
    });
    return sorted;
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="w-4 h-4 text-green-400" />;
      case 'down':
        return <TrendingDown className="w-4 h-4 text-red-400" />;
      default:
        return <Minus className="w-4 h-4 text-gray-400" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  const sortedSources = getSortedSources();
  const totalEntries = sources.reduce((sum, s) => sum + s.total_entries, 0);

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-xl font-semibold text-white flex items-center gap-2">
              <Globe className="w-6 h-6 text-blue-400" />
              Source Summary
            </h3>
            <p className="text-sm text-gray-400 mt-1">
              Contribution from each data source
            </p>
          </div>
          <div className="flex items-center gap-4">
            <select
              value={sortBy}
              onChange={(e) =>
                setSortBy(e.target.value as "entries" | "titles")
              }
              className="px-4 py-2 bg-gray-800 text-gray-300 rounded-lg border border-gray-700 focus:outline-none focus:border-blue-500"
            >
              <option value="entries">Sort by Entries</option>
              <option value="titles">Sort by Titles</option>
            </select>
            <button
              onClick={() => setSortOrder(sortOrder === "asc" ? "desc" : "asc")}
              className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg transition-colors border border-gray-700"
            >
              {sortOrder === "asc" ? "↑ Ascending" : "↓ Descending"}
            </button>
          </div>
        </div>

        {sortedSources.length > 0 ? (
          <ResponsiveContainer width="100%" height={600}>
            <BarChart
              data={sortedSources.slice(0, 15)} // only top 20
              layout="vertical"
              margin={{ top: 5, right: 30, left: 0, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis type="number" stroke="#9CA3AF" />
              <YAxis
                dataKey="source"
                type="category"
                stroke="#9CA3AF"
                width={300}
                tickFormatter={(text) => truncateText(text, 25)}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1F2937",
                  border: "1px solid #374151",
                  borderRadius: "8px",
                }}
                labelStyle={{ color: "#F3F4F6" }}
              />
              <Bar
                dataKey={
                  sortBy === "entries" ? "total_entries" : "unique_titles"
                }
                fill="#3B82F6"
                radius={[0, 8, 8, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex items-center justify-center h-[400px] text-gray-500">
            No source data available
          </div>
        )}
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {sortedSources.slice(0, 6).map((source, index) => (
          <motion.div
            key={source.source}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
          >
            <Card hover className="p-6">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1 overflow-hidden">
                  <h4
                    className="text-lg font-semibold text-white truncate block w-full"
                    title={source.source}
                  >
                    {source.source}
                  </h4>
                  <div className="flex items-center gap-2 mt-1">
                    {getTrendIcon(source.trend)}
                    <span className="text-xs text-gray-400 capitalize">
                      {source.trend}
                    </span>
                  </div>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-2xl font-bold text-blue-400">
                    {source.total_entries}
                  </p>
                  <p className="text-xs text-gray-500">Total Entries</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-cyan-400">
                    {source.unique_titles}
                  </p>
                  <p className="text-xs text-gray-500">Unique Titles</p>
                </div>
              </div>
              <div className="mt-4 pt-4 border-t border-gray-700">
                <div className="flex items-center justify-between text-xs text-gray-400">
                  <span>Share</span>
                  <span className="font-semibold text-white">
                    {((source.total_entries / totalEntries) * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="mt-2 w-full bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                    style={{
                      width: `${(source.total_entries / totalEntries) * 100}%`,
                    }}
                  />
                </div>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
