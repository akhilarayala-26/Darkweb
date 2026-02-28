import { useEffect, useState } from 'react';
import { Card } from '../components/Card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Search, TrendingUp } from 'lucide-react';
import { motion } from 'framer-motion';

interface KeywordData {
  keyword: string;
  count: number;
  category: string | null;
}

export function KeywordTrends() {
  const [keywords, setKeywords] = useState<KeywordData[]>([]);
  const [filteredKeywords, setFilteredKeywords] = useState<KeywordData[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [limit, setLimit] = useState(20);

  useEffect(() => {
    fetchKeywords();
  }, [limit]);

  useEffect(() => {
    if (searchTerm) {
      const filtered = keywords.filter(k =>
        k.keyword.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredKeywords(filtered);
    } else {
      setFilteredKeywords(keywords);
    }
  }, [searchTerm, keywords]);

  const fetchKeywords = async () => {
    try {
      const res = await fetch(
        `http://127.0.0.1:8000/analytics/keywords?limit=${limit}`
      );
      const json = await res.json();
      if (json.keywords) {
        setKeywords(json.keywords);
        setFilteredKeywords(json.keywords);
      }
    } catch (error) {
      console.error("Error fetching keywords:", error);
    } finally {
      setLoading(false);
    }
  };


  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-xl font-semibold text-white flex items-center gap-2">
              <TrendingUp className="w-6 h-6 text-blue-400" />
              Keyword Frequency Analysis
            </h3>
            <p className="text-sm text-gray-400 mt-1">Most frequently occurring keywords across all sources</p>
          </div>
          <div className="flex items-center gap-4">
            <select
              value={limit}
              onChange={(e) => setLimit(Number(e.target.value))}
              className="px-4 py-2 bg-gray-800 text-gray-300 rounded-lg border border-gray-700 focus:outline-none focus:border-blue-500"
            >
              <option value={10}>Top 10</option>
              <option value={20}>Top 20</option>
              <option value={50}>Top 50</option>
              <option value={100}>Top 100</option>
            </select>
          </div>
        </div>

        <div className="relative mb-6">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search keywords..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-3 bg-gray-800 text-white rounded-lg border border-gray-700 focus:outline-none focus:border-blue-500"
          />
        </div>

        {filteredKeywords.length > 0 ? (
          <ResponsiveContainer width="100%" height={500}>
            <BarChart data={filteredKeywords} margin={{ top: 20, right: 30, left: 20, bottom: 80 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis
                dataKey="keyword"
                stroke="#9CA3AF"
                angle={-45}
                textAnchor="end"
                height={100}
                interval={0}
              />
              <YAxis stroke="#9CA3AF" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1F2937',
                  border: '1px solid #374151',
                  borderRadius: '8px'
                }}
                labelStyle={{ color: '#F3F4F6' }}
              />
              <Bar dataKey="count" fill="#3B82F6" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex items-center justify-center h-[500px] text-gray-500">
            No keywords found
          </div>
        )}
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredKeywords.slice(0, 9).map((keyword, index) => (
          <motion.div
            key={keyword.keyword}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
          >
            <Card hover className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <h4 className="text-lg font-semibold text-white truncate">{keyword.keyword}</h4>
                  {keyword.category && (
                    <span className="inline-block px-2 py-1 text-xs bg-gray-700 text-gray-300 rounded mt-1">
                      {keyword.category}
                    </span>
                  )}
                </div>
                <div className="text-right ml-4">
                  <p className="text-3xl font-bold text-blue-400">{keyword.count}</p>
                  <p className="text-xs text-gray-500">occurrences</p>
                </div>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
