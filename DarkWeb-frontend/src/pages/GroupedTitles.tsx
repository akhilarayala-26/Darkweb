import { useEffect, useState } from "react";
import { Card } from "../components/Card";
import {
  Search,
  ChevronDown,
  ChevronUp,
  FileText,
  Download,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface TitleData {
  title: string;
  total_appearances: number;
  unique_days: number;
  first_seen: string;
  last_seen: string;
  avg_sentiment?: number;
}

export function GroupedTitles() {
  const [titles, setTitles] = useState<TitleData[]>([]);
  const [filteredTitles, setFilteredTitles] = useState<TitleData[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [sortOption, setSortOption] = useState("unique_days");
  const [loading, setLoading] = useState(true);
  const [expandedTitle, setExpandedTitle] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTitles();
  }, []);

  useEffect(() => {
    let filtered = titles;

    if (searchTerm.trim().length > 0) {
      filtered = titles.filter((t) =>
        t.title.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    const sorted = [...filtered].sort((a, b) => {
      if (sortOption === "title") return a.title.localeCompare(b.title);
      if (sortOption === "first_seen" || sortOption === "last_seen")
        return (
          new Date(b[sortOption]).getTime() - new Date(a[sortOption]).getTime()
        );
      return (b as any)[sortOption] - (a as any)[sortOption];
    });

    setFilteredTitles(sorted);
  }, [searchTerm, titles, sortOption]);

  const fetchTitles = async () => {
    try {
      setLoading(true);
      setError(null);

      // ✅ Updated endpoint
      const res = await fetch(
        "http://localhost:8000/analytics/repeated-domains"
      );
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const result = await res.json();
      const data = Array.isArray(result) ? result : result.data;

      if (!Array.isArray(data)) throw new Error("Invalid response format");

      setTitles(data);
      setFilteredTitles(data);
    } catch (err: any) {
      console.error("Error fetching repeated titles:", err);
      setError("Failed to load repeated titles. Please try again later.");
      setTitles([]);
      setFilteredTitles([]);
    } finally {
      setLoading(false);
    }
  };

  const exportToCSV = () => {
    if (!filteredTitles || filteredTitles.length === 0) return;

    const headers = [
      "Title",
      "Total Appearances",
      "Unique Days",
      "First Seen",
      "Last Seen",
      "Avg Sentiment",
    ];
    const rows = filteredTitles.map((t) => [
      t.title,
      t.total_appearances.toString(),
      t.unique_days.toString(),
      new Date(t.first_seen).toLocaleDateString(),
      new Date(t.last_seen).toLocaleDateString(),
      t.avg_sentiment?.toFixed(2) ?? "N/A",
    ]);

    const csv = [
      headers.join(","),
      ...rows.map((row) => row.map((cell) => `"${cell}"`).join(",")),
    ].join("\n");

    const blob = new Blob([csv], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "repeated_titles.csv";
    a.click();
    window.URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64 text-red-400">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-4">
          <div>
            <h3 className="text-xl font-semibold text-white flex items-center gap-2">
              <FileText className="w-6 h-6 text-blue-400" />
              Repeated Titles
            </h3>
            <p className="text-sm text-gray-400 mt-1">
              Titles appearing across multiple days
            </p>
          </div>

          <div className="flex gap-3">
            <select
              value={sortOption}
              onChange={(e) => setSortOption(e.target.value)}
              className="bg-gray-800 text-white px-3 py-2 rounded-lg border border-gray-700 focus:outline-none focus:border-blue-500"
            >
              <option value="unique_days">Unique Days</option>
              <option value="total_appearances">Total Appearances</option>
              <option value="avg_sentiment">Average Sentiment</option>
              <option value="first_seen">First Seen</option>
              <option value="last_seen">Last Seen</option>
              <option value="title">Title (A–Z)</option>
            </select>

            <button
              onClick={exportToCSV}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
            >
              <Download className="w-4 h-4" />
              <span className="text-sm">Export CSV</span>
            </button>
          </div>
        </div>

        <div className="relative mb-6">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search titles..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-3 bg-gray-800 text-white rounded-lg border border-gray-700 focus:outline-none focus:border-blue-500"
          />
        </div>

        <div className="space-y-3">
          {filteredTitles && filteredTitles.length > 0 ? (
            filteredTitles.map((title, index) => (
              <motion.div
                key={title.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.02 }}
              >
                <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
                  <button
                    onClick={() =>
                      setExpandedTitle(
                        expandedTitle === title.title ? null : title.title
                      )
                    }
                    className="w-full p-4 flex items-center justify-between hover:bg-gray-750 transition-colors"
                  >
                    <div className="flex-1 text-left">
                      <h4 className="text-white font-medium">{title.title}</h4>
                      <div className="flex items-center gap-4 mt-2 text-sm text-gray-400">
                        <span>{title.unique_days} unique days</span>
                        <span>•</span>
                        <span>
                          First seen:{" "}
                          {new Date(title.first_seen).toLocaleDateString()}
                        </span>
                        <span>•</span>
                        <span>
                          Last seen:{" "}
                          {new Date(title.last_seen).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                    {expandedTitle === title.title ? (
                      <ChevronUp className="w-5 h-5 text-gray-400" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-gray-400" />
                    )}
                  </button>

                  <AnimatePresence>
                    {expandedTitle === title.title && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.3 }}
                        className="border-t border-gray-700"
                      >
                        <div className="p-4 bg-gray-850">
                          <p className="text-sm text-gray-300">
                            Total appearances: {title.total_appearances}
                          </p>
                          {typeof title.avg_sentiment === "number" && (
                            <p className="text-sm text-gray-400 mt-1">
                              Avg sentiment: {title.avg_sentiment.toFixed(2)}
                            </p>
                          )}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </motion.div>
            ))
          ) : (
            <div className="flex items-center justify-center h-64 text-gray-500">
              No repeated titles found
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}
