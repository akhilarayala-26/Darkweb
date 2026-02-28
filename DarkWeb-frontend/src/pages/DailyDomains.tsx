import { useEffect, useState } from "react";
import { Card } from "../components/Card";
import {
  Calendar,
  Globe,
  FileText,
  TrendingUp,
  ChevronDown,
  ChevronRight,
} from "lucide-react";
import { format, parseISO } from "date-fns";
import { motion, AnimatePresence } from "framer-motion";

interface DomainDetail {
  title: string;
  language: string;
  sentiment_score: number;
  category: string;
  keywords: string[];
  status_code: number;
  load_time_s: number;
  page_size_kb: number;
  onion_links_outbound: number;
  classification: string;
  first_seen: string;
  last_seen: string;
}

interface DomainData {
  [domain: string]: DomainDetail[];
}

interface DailyDomainsData {
  [date: string]: DomainData;
}

export function DailyDomains() {
  const [dailyData, setDailyData] = useState<DailyDomainsData>({});
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState<string>("");
  const [expandedDomains, setExpandedDomains] = useState<Set<string>>(
    new Set()
  );
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    fetchDailyDomains();
  }, []);

  const fetchDailyDomains = async () => {
    try {
      const response = await fetch(
        "http://localhost:8000/analytics/daily-domains"
      );

      if (!response.ok) {
        throw new Error("Failed to fetch daily domains");
      }

      const data = await response.json();
      const domainsData = data.daily_domains || {};

      setDailyData(domainsData);

      const dates = Object.keys(domainsData).sort((a, b) => b.localeCompare(a));
      if (dates.length > 0) {
        setSelectedDate(dates[0]);
      }
    } catch (error) {
      console.error("Error fetching daily domains:", error);
    } finally {
      setLoading(false);
    }
  };

  const toggleDomain = (domain: string) => {
    const newExpanded = new Set(expandedDomains);
    if (newExpanded.has(domain)) {
      newExpanded.delete(domain);
    } else {
      newExpanded.add(domain);
    }
    setExpandedDomains(newExpanded);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  const dates = Object.keys(dailyData).sort((a, b) => b.localeCompare(a));
  const currentData = selectedDate ? dailyData[selectedDate] : {};

  const filteredDomains = Object.entries(currentData).filter(([domain]) =>
    domain.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalDomains = filteredDomains.length;
  const totalPages = filteredDomains.reduce(
    (sum, [, details]) => sum + details.length,
    0
  );

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white">Daily Domains</h2>
          <p className="text-gray-400 mt-2">
            Explore unique domains discovered each day
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4 bg-gradient-to-br from-blue-500/10 to-blue-600/5 border-blue-500/20">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-blue-500/20 rounded-lg">
              <Calendar className="w-6 h-6 text-blue-400" />
            </div>
            <div>
              <p className="text-sm text-gray-400">Total Days</p>
              <p className="text-2xl font-bold text-white">{dates.length}</p>
            </div>
          </div>
        </Card>

        <Card className="p-4 bg-gradient-to-br from-green-500/10 to-green-600/5 border-green-500/20">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-green-500/20 rounded-lg">
              <Globe className="w-6 h-6 text-green-400" />
            </div>
            <div>
              <p className="text-sm text-gray-400">Domains 06-10-25</p>
              <p className="text-2xl font-bold text-white">{totalDomains}</p>
            </div>
          </div>
        </Card>

        <Card className="p-4 bg-gradient-to-br from-purple-500/10 to-purple-600/5 border-purple-500/20">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-purple-500/20 rounded-lg">
              <FileText className="w-6 h-6 text-purple-400" />
            </div>
            <div>
              <p className="text-sm text-gray-400">Pages 06-10-25</p>
              <p className="text-2xl font-bold text-white">576</p>
            </div>
          </div>
        </Card>
      </div>

      <Card className="p-6">
        <div className="space-y-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Select Date
              </label>
              <select
                value={selectedDate}
                onChange={(e) => {
                  setSelectedDate(e.target.value);
                  setExpandedDomains(new Set());
                }}
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
              >
                {dates.map((date) => (
                  <option key={date} value={date}>
                    {format(parseISO(date), "MMMM dd, yyyy")} (
                    {Object.keys(dailyData[date]).length} domains)
                  </option>
                ))}
              </select>
            </div>

            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Search Domains
              </label>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Filter by domain name..."
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>
        </div>
      </Card>

      <Card className="p-6">
        <div className="space-y-3">
          {filteredDomains.length === 0 ? (
            <div className="text-center py-12">
              <Globe className="w-12 h-12 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-500">No domains found</p>
            </div>
          ) : (
            filteredDomains.map(([domain, details]) => (
              <div
                key={domain}
                className="border border-gray-700 rounded-lg overflow-hidden"
              >
                <button
                  onClick={() => toggleDomain(domain)}
                  className="w-full px-4 py-3 bg-gray-800/50 hover:bg-gray-800 transition-colors flex items-center justify-between"
                >
                  <div className="flex items-center gap-3">
                    {expandedDomains.has(domain) ? (
                      <ChevronDown className="w-5 h-5 text-blue-400" />
                    ) : (
                      <ChevronRight className="w-5 h-5 text-gray-400" />
                    )}
                    <Globe className="w-5 h-5 text-green-400" />
                    <div className="text-left">
                      <p className="text-white font-medium break-all">
                        {domain}
                      </p>
                      <p className="text-sm text-gray-400">
                        {details.length} pages
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="px-3 py-1 bg-blue-500/10 text-blue-400 rounded-full text-sm font-semibold">
                      {details.length}
                    </span>
                  </div>
                </button>

                <AnimatePresence>
                  {expandedDomains.has(domain) && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.2 }}
                      className="overflow-hidden"
                    >
                      <div className="p-4 bg-gray-900/50 space-y-3">
                        {details.map((detail, idx) => (
                          <motion.div
                            key={idx}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: idx * 0.05 }}
                            className="p-4 bg-gray-800 rounded-lg border border-gray-700"
                          >
                            <div className="space-y-3">
                              <div>
                                <h4 className="text-white font-medium mb-2">
                                  {detail.title || "Untitled"}
                                </h4>
                                <div className="flex flex-wrap gap-2">
                                  {detail.category && (
                                    <span className="px-2 py-1 bg-purple-500/10 text-purple-400 rounded text-xs">
                                      {detail.category}
                                    </span>
                                  )}
                                  {detail.classification && (
                                    <span className="px-2 py-1 bg-orange-500/10 text-orange-400 rounded text-xs">
                                      {detail.classification}
                                    </span>
                                  )}
                                  {detail.language && (
                                    <span className="px-2 py-1 bg-blue-500/10 text-blue-400 rounded text-xs">
                                      {detail.language}
                                    </span>
                                  )}
                                  {detail.status_code && (
                                    <span
                                      className={`px-2 py-1 rounded text-xs ${
                                        detail.status_code === 200
                                          ? "bg-green-500/10 text-green-400"
                                          : "bg-red-500/10 text-red-400"
                                      }`}
                                    >
                                      {detail.status_code}
                                    </span>
                                  )}
                                </div>
                              </div>

                              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                                {detail.sentiment_score !== undefined &&
                                  detail.sentiment_score !== null && (
                                    <div>
                                      <p className="text-gray-400 text-xs">
                                        Sentiment
                                      </p>
                                      <p className="text-white font-medium">
                                        {detail.sentiment_score.toFixed(2)}
                                      </p>
                                    </div>
                                  )}
                                {detail.load_time_s !== undefined &&
                                  detail.load_time_s !== null && (
                                    <div>
                                      <p className="text-gray-400 text-xs">
                                        Load Time
                                      </p>
                                      <p className="text-white font-medium">
                                        {detail.load_time_s.toFixed(2)}s
                                      </p>
                                    </div>
                                  )}
                                {detail.page_size_kb !== undefined &&
                                  detail.page_size_kb !== null && (
                                    <div>
                                      <p className="text-gray-400 text-xs">
                                        Page Size
                                      </p>
                                      <p className="text-white font-medium">
                                        {detail.page_size_kb.toFixed(1)} KB
                                      </p>
                                    </div>
                                  )}
                                {detail.onion_links_outbound !== undefined &&
                                  detail.onion_links_outbound !== null && (
                                    <div>
                                      <p className="text-gray-400 text-xs">
                                        Outbound Links
                                      </p>
                                      <p className="text-white font-medium">
                                        {detail.onion_links_outbound}
                                      </p>
                                    </div>
                                  )}
                              </div>

                              {detail.keywords &&
                                detail.keywords.length > 0 && (
                                  <div>
                                    <p className="text-gray-400 text-xs mb-2">
                                      Keywords
                                    </p>
                                    <div className="flex flex-wrap gap-1">
                                      {detail.keywords
                                        .slice(0, 10)
                                        .map((keyword, kidx) => (
                                          <span
                                            key={kidx}
                                            className="px-2 py-1 bg-gray-700 text-gray-300 rounded text-xs"
                                          >
                                            {keyword}
                                          </span>
                                        ))}
                                    </div>
                                  </div>
                                )}

                              {(detail.first_seen || detail.last_seen) && (
                                <div className="flex gap-4 text-xs text-gray-400">
                                  {detail.first_seen && (
                                    <div>
                                      First seen:{" "}
                                      {format(
                                        parseISO(detail.first_seen),
                                        "MMM dd, yyyy"
                                      )}
                                    </div>
                                  )}
                                  {detail.last_seen && (
                                    <div>
                                      Last seen:{" "}
                                      {format(
                                        parseISO(detail.last_seen),
                                        "MMM dd, yyyy"
                                      )}
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>
                          </motion.div>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ))
          )}
        </div>
      </Card>
    </div>
  );
}
