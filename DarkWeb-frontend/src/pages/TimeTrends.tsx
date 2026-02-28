import { useEffect, useState } from "react";
import { Card } from "../components/Card";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { Activity, Calendar, GitBranch, Globe } from "lucide-react";
import { format } from "date-fns";
import { motion } from "framer-motion";

interface TrendData {
  date: string;
  urls: number;
  keywords: number;
  sources: number;
  titles: number;
}

interface SiteEvolution {
  title: string;
  domains: Array<{
    domain: string;
    first_seen: string;
    last_seen: string;
  }>;
  total_domains: number;
  active_days: number;
}

export function TimeTrends() {
  const [trends, setTrends] = useState<TrendData[]>([]);
  const [siteEvolutions, setSiteEvolutions] = useState<SiteEvolution[]>([]);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState(14);

  useEffect(() => {
    fetchTrends();
    fetchSiteEvolution();
  }, [dateRange]);

const fetchTrends = async () => {
  try {
    const response = await fetch(
      `http://localhost:8000/analytics/time-trends?days=${dateRange}`
    );

    if (!response.ok) {
      throw new Error("Failed to fetch time trends");
    }

    const data = await response.json();
    console.log("Time trends response:", data);

    // --- FIX ---
    // Access the array inside the 'trends' property
    if (data && Array.isArray(data.trends)) {
      // --- FIX ---
      // Map over data.trends
      const formattedData = data.trends.map((m: any) => ({
        // --- FIX ---
        // Your log shows the date is already formatted as "Oct 18".
        // Using new Date("Oct 18") would be invalid.
        // Use the value directly.
        date: m.date,
        urls: m.urls || 0,
        keywords: m.keywords || 0,
        sources: m.sources || 0,
        titles: m.titles || 0,
      }));
      setTrends(formattedData);
    } else {
      console.warn("No 'trends' array found in API response.");
      setTrends([]); // Clear data on empty response
    }
  } catch (error) {
    console.error("Error fetching trends:", error);
  } finally {
    setLoading(false);
  }
};

const fetchSiteEvolution = async () => {
  try {
    const response = await fetch(
      "http://localhost:8000/analytics/site-evolution"
    );

    if (!response.ok) {
      throw new Error("Failed to fetch site evolution");
    }

    const data = await response.json();
    console.log("Site evolution response:", data); // Keep this for debugging

    // --- FIX ---
    // Access the array inside the 'site_evolutions' property
    if (data && Array.isArray(data.site_evolutions)) {
      // --- FIX ---
      // Map over data.site_evolutions
      const evolutions: SiteEvolution[] = data.site_evolutions.map(
        (item: any) => ({
          title: item.title,
          domains: item.domains || [],
          total_domains: item.total_domains || 0,
          active_days: item.active_days || 0,
        })
      );

      setSiteEvolutions(evolutions.slice(0, 10));
    } else {
      console.warn("No 'site_evolutions' array found in API response.");
      setSiteEvolutions([]); // Clear data on empty response
    }
  } catch (error) {
    console.error("Error fetching site evolution:", error);
  }
  // Note: No 'finally' block here, as this fetch is separate.
  // Consider adding a separate 'evolutionLoading' state.
};

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  const totalUrls = trends.reduce((sum, t) => sum + t.urls, 0);
  const avgUrls =
    trends.length > 0 ? (totalUrls / trends.length).toFixed(0) : 0;
  const maxUrls =
    trends.length > 0 ? Math.max(...trends.map((t) => t.urls)) : 0;
  const minUrls =
    trends.length > 0 ? Math.min(...trends.map((t) => t.urls)) : 0;

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-xl font-semibold text-white flex items-center gap-2">
              <Activity className="w-6 h-6 text-blue-400" />
              Time-based Trends
            </h3>
            <p className="text-sm text-gray-400 mt-1">
              Growth and activity over time
            </p>
          </div>
          <div className="flex items-center gap-4">
            <select
              value={dateRange}
              onChange={(e) => setDateRange(Number(e.target.value))}
              className="px-4 py-2 bg-gray-800 text-gray-300 rounded-lg border border-gray-700 focus:outline-none focus:border-blue-500"
            >
              <option value={7}>Last 7 Days</option>
              <option value={14}>Last 14 Days</option>
              <option value={30}>Last 30 Days</option>
              <option value={90}>Last 90 Days</option>
            </select>
          </div>
        </div>

        {trends.length > 0 ? (
          <ResponsiveContainer width="100%" height={400}>
            <LineChart
              data={trends}
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1F2937",
                  border: "1px solid #374151",
                  borderRadius: "8px",
                }}
                labelStyle={{ color: "#F3F4F6" }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="urls"
                stroke="#3B82F6"
                strokeWidth={2}
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
                name="URLs"
              />
              <Line
                type="monotone"
                dataKey="keywords"
                stroke="#8B5CF6"
                strokeWidth={2}
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
                name="Keywords"
              />
              <Line
                type="monotone"
                dataKey="sources"
                stroke="#10B981"
                strokeWidth={2}
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
                name="Sources"
              />
              <Line
                type="monotone"
                dataKey="titles"
                stroke="#F59E0B"
                strokeWidth={2}
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
                name="Grouped Titles"
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex items-center justify-center h-[400px] text-gray-500">
            No trend data available for selected period
          </div>
        )}
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-3 h-3 rounded-full bg-blue-500"></div>
            <h4 className="text-sm font-medium text-gray-400">Total URLs</h4>
          </div>
          <p className="text-3xl font-bold text-white">{totalUrls}</p>
          <p className="text-sm text-gray-500 mt-1">Over {dateRange} days</p>
        </Card>

        <Card className="p-6">
          <div className="flex items-center gap-3 mb-2">
            <Calendar className="w-4 h-4 text-gray-400" />
            <h4 className="text-sm font-medium text-gray-400">Daily Average</h4>
          </div>
          <p className="text-3xl font-bold text-white">{avgUrls}</p>
          <p className="text-sm text-gray-500 mt-1">URLs per day</p>
        </Card>

        <Card className="p-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            <h4 className="text-sm font-medium text-gray-400">Peak Day</h4>
          </div>
          <p className="text-3xl font-bold text-white">{maxUrls}</p>
          <p className="text-sm text-gray-500 mt-1">Maximum URLs</p>
        </Card>

        <Card className="p-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            <h4 className="text-sm font-medium text-gray-400">Lowest Day</h4>
          </div>
          <p className="text-3xl font-bold text-white">{minUrls}</p>
          <p className="text-sm text-gray-500 mt-1">Minimum URLs</p>
        </Card>
      </div>

      <Card className="p-6">
        <h3 className="text-lg font-semibold text-white mb-4">
          Activity Summary
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="text-sm font-medium text-gray-400 mb-3">
              Recent Activity
            </h4>
            <div className="space-y-2">
              {trends
                .slice(-5)
                .reverse()
                .map((trend, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 bg-gray-800 rounded-lg"
                  >
                    <span className="text-sm text-gray-300">{trend.date}</span>
                    <div className="flex items-center gap-4">
                      <span className="text-sm text-blue-400 font-semibold">
                        {trend.urls} URLs
                      </span>
                      <span className="text-sm text-purple-400 font-semibold">
                        {trend.keywords} Keywords
                      </span>
                    </div>
                  </div>
                ))}
            </div>
          </div>

          <div>
            <h4 className="text-sm font-medium text-gray-400 mb-3">
              Growth Metrics
            </h4>
            <div className="space-y-4">
              <div className="p-4 bg-gray-800 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-300">
                    URL Collection Rate
                  </span>
                  <span className="text-sm text-blue-400 font-semibold">
                    {avgUrls}/day
                  </span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full"
                    style={{
                      width: `${Math.min(
                        (Number(avgUrls) / maxUrls) * 100,
                        100
                      )}%`,
                    }}
                  />
                </div>
              </div>

              <div className="p-4 bg-gray-800 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-300">
                    Peak Performance
                  </span>
                  <span className="text-sm text-green-400 font-semibold">
                    {maxUrls} URLs
                  </span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-green-500 h-2 rounded-full"
                    style={{ width: "100%" }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </Card>

      <Card className="p-6">
        <div className="flex items-center gap-3 mb-6">
          <GitBranch className="w-6 h-6 text-cyan-400" />
          <div>
            <h3 className="text-xl font-semibold text-white">
              Site Evolution Analysis
            </h3>
            <p className="text-sm text-gray-400 mt-1">
              Tracking how titles migrate across different domains
            </p>
          </div>
        </div>

        {siteEvolutions.length > 0 ? (
          <div className="space-y-4">
            {siteEvolutions.map((evolution, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
                className="bg-gray-800 rounded-lg border border-gray-700 p-5"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h4 className="text-white font-semibold mb-2">
                      {evolution.title}
                    </h4>
                    <div className="flex items-center gap-4 text-sm text-gray-400">
                      <span className="flex items-center gap-1">
                        <Globe className="w-4 h-4" />
                        {evolution.total_domains} domains
                      </span>
                      <span>•</span>
                      <span className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        {evolution.active_days} active days
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 px-3 py-1 bg-cyan-500/10 rounded-lg border border-cyan-500/30">
                    <GitBranch className="w-4 h-4 text-cyan-400" />
                    <span className="text-sm font-semibold text-cyan-400">
                      {evolution.total_domains} migrations
                    </span>
                  </div>
                </div>

                <div className="space-y-2">
                  {evolution.domains.map((domain, domainIndex) => (
                    <div
                      key={domainIndex}
                      className="flex items-center gap-3 p-3 bg-gray-900 rounded-lg"
                    >
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-gradient-to-br from-cyan-500 to-blue-500 rounded-lg flex items-center justify-center text-white text-sm font-bold">
                          {domainIndex + 1}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-gray-300 font-mono truncate">
                            {domain.domain}
                          </p>
                          <p className="text-xs text-gray-500 mt-1">
                            {format(
                              new Date(domain.first_seen),
                              "MMM dd, yyyy"
                            )}{" "}
                            →{" "}
                            {format(new Date(domain.last_seen), "MMM dd, yyyy")}
                          </p>
                        </div>
                      </div>
                      {domainIndex < evolution.domains.length - 1 && (
                        <div className="text-gray-600">→</div>
                      )}
                    </div>
                  ))}
                </div>
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <GitBranch className="w-12 h-12 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-500">No site evolution data available</p>
            <p className="text-sm text-gray-600 mt-2">
              Titles appearing on multiple domains will be tracked here
            </p>
          </div>
        )}
      </Card>
    </div>
  );
}
