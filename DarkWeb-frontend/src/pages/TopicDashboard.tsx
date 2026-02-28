import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card } from '../components/Card';
import { DateRangePicker } from '../components/DateRangePicker';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
    ResponsiveContainer, LineChart, Line, Legend, PieChart, Pie, Cell,
} from 'recharts';
import {
    ArrowLeft, Globe, FileText, TrendingUp, Shield, Key,
    Mail, Bitcoin, ChevronDown, ChevronRight, GitBranch,
    Activity, Search, Copy, Layers,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { API_BASE_URL } from '../config';

const SENTIMENT_COLORS = { positive: '#10B981', neutral: '#6B7280', negative: '#EF4444' };

const TOPIC_META: Record<string, { label: string; color: string }> = {
    drugs: { label: 'Drugs & Forums', color: '#8B5CF6' },
    credit_card: { label: 'Credit Card', color: '#F59E0B' },
    weapons: { label: 'Weapons', color: '#EF4444' },
};

export function TopicDashboard() {
    const { topicId } = useParams<{ topicId: string }>();
    const navigate = useNavigate();
    const [dateRange, setDateRange] = useState<{ start: string | null; end: string | null }>({ start: null, end: null });
    const [loading, setLoading] = useState(true);

    // Data states
    const [overview, setOverview] = useState<any>({});
    const [keywords, setKeywords] = useState<any[]>([]);
    const [sentiment, setSentiment] = useState<any>({});
    const [trends, setTrends] = useState<any[]>([]);
    const [groups, setGroups] = useState<any>({ groups: [], total: 0 });
    const [mirrors, setMirrors] = useState<any>({ clusters: [], summary: {} });
    const [actors, setActors] = useState<any>({});
    const [evolution, setEvolution] = useState<any>({ evolution_groups: [], available_dates: [], total_urls: 0 });

    // UI states
    const [expandedGroup, setExpandedGroup] = useState<string | null>(null);
    const [groupSearch, setGroupSearch] = useState('');
    const [expandedEvoGroup, setExpandedEvoGroup] = useState<string | null>(null);
    const [evoShowMore, setEvoShowMore] = useState<Record<string, boolean>>({});
    const [mirrorShowAll, setMirrorShowAll] = useState<Record<number, boolean>>({});
    const [activeTab, setActiveTab] = useState('overview');

    const meta = TOPIC_META[topicId || ''] || { label: topicId, color: '#3B82F6' };

    useEffect(() => {
        if (!topicId) return;

        const buildUrl = (path: string, extra?: Record<string, any>) => {
            const params = new URLSearchParams();
            if (dateRange.start) params.set('start', dateRange.start);
            if (dateRange.end) params.set('end', dateRange.end);
            if (extra) Object.entries(extra).forEach(([k, v]) => params.set(k, String(v)));
            const qs = params.toString();
            return `${API_BASE_URL}/dashboard/topic/${topicId}/${path}${qs ? `?${qs}` : ''}`;
        };

        console.log('[Dashboard] Fetching with dateRange:', dateRange.start, dateRange.end);

        setLoading(true);
        Promise.all([
            fetch(buildUrl('overview')).then(r => r.json()),
            fetch(buildUrl('keywords', { limit: 25 })).then(r => r.json()),
            fetch(buildUrl('sentiment')).then(r => r.json()),
            fetch(buildUrl('trends')).then(r => r.json()),
            fetch(buildUrl('groups')).then(r => r.json()),
            fetch(buildUrl('mirrors')).then(r => r.json()),
            fetch(buildUrl('actors')).then(r => r.json()),
            fetch(buildUrl('evolution')).then(r => r.json()),
        ]).then(([ov, kw, se, tr, gr, mi, ac, ev]) => {
            setOverview(ov.summary || {});
            setKeywords(kw.keywords || []);
            setSentiment(se);
            setTrends(tr.trends || []);
            setGroups(gr);
            setMirrors(mi);
            setActors(ac);
            setEvolution(ev || { evolution_groups: [], available_dates: [], total_urls: 0 });
        }).catch(e => console.error('Error loading dashboard:', e))
            .finally(() => setLoading(false));
    }, [topicId, dateRange.start, dateRange.end]);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="flex flex-col items-center gap-4">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
                    <p className="text-gray-400">Loading {meta.label} analysis...</p>
                </div>
            </div>
        );
    }

    const filteredGroups = groups.groups?.filter((g: any) =>
        g.title.toLowerCase().includes(groupSearch.toLowerCase())
    ) || [];

    const sentimentPieData = sentiment.distribution ? [
        { name: 'Positive', value: sentiment.distribution.positive, color: SENTIMENT_COLORS.positive },
        { name: 'Neutral', value: sentiment.distribution.neutral, color: SENTIMENT_COLORS.neutral },
        { name: 'Negative', value: sentiment.distribution.negative, color: SENTIMENT_COLORS.negative },
    ] : [];

    const tabs = [
        { id: 'overview', label: 'Overview', icon: Activity },
        { id: 'groups', label: 'Grouped Titles', icon: FileText },
        { id: 'mirrors', label: 'Mirrors', icon: Layers },
        { id: 'actors', label: 'Actor Intel', icon: Key },
        { id: 'evolution', label: 'Evolution', icon: GitBranch },
    ];

    return (
        <div className="space-y-6 p-6">
            {/* Header */}
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                    <button
                        onClick={() => navigate('/')}
                        className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
                    >
                        <ArrowLeft className="w-5 h-5 text-gray-400" />
                    </button>
                    <div>
                        <h2 className="text-3xl font-bold text-white flex items-center gap-3">
                            <div className="w-3 h-8 rounded-full" style={{ backgroundColor: meta.color }} />
                            {meta.label} Analysis
                        </h2>
                        <p className="text-gray-400 mt-1">
                            {overview.data_start && overview.data_end
                                ? `Data from ${overview.data_start} to ${overview.data_end} · ${overview.total_days} days`
                                : 'Comprehensive threat analysis'}
                        </p>
                    </div>
                </div>
                <DateRangePicker onRangeChange={(s, e) => setDateRange({ start: s, end: e })} />
            </div>

            {/* Tab Navigation */}
            <div className="flex items-center gap-2 border-b border-gray-800 pb-1 overflow-x-auto">
                {tabs.map(tab => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`flex items-center gap-2 px-4 py-2.5 rounded-t-lg text-sm font-medium transition-all whitespace-nowrap ${activeTab === tab.id
                            ? 'bg-gray-800 text-white border-b-2 border-blue-500'
                            : 'text-gray-500 hover:text-gray-300 hover:bg-gray-800/50'
                            }`}
                    >
                        <tab.icon className="w-4 h-4" />
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* OVERVIEW TAB */}
            {activeTab === 'overview' && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
                    {/* Metric Cards */}
                    <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
                        {[
                            { label: 'Total Records', value: overview.total_records?.toLocaleString() || '0', color: '#3B82F6' },
                            { label: 'Unique Domains', value: overview.unique_domains?.toLocaleString() || '0', color: '#10B981' },
                            { label: 'Title Groups', value: overview.total_groups?.toLocaleString() || '0', color: '#8B5CF6' },
                            { label: 'Mirror Clusters', value: overview.mirror_clusters?.toLocaleString() || '0', color: '#F59E0B' },
                            { label: 'Avg Sentiment', value: overview.avg_sentiment?.toFixed(3) || '0', color: overview.avg_sentiment > 0 ? '#10B981' : '#EF4444' },
                        ].map((m, i) => (
                            <motion.div key={i} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}>
                                <Card className="p-5">
                                    <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">{m.label}</p>
                                    <p className="text-3xl font-bold mt-2" style={{ color: m.color }}>{m.value}</p>
                                </Card>
                            </motion.div>
                        ))}
                    </div>

                    {/* Keywords Chart */}
                    <Card className="p-6">
                        <h3 className="text-lg font-semibold text-white mb-1 flex items-center gap-2">
                            <TrendingUp className="w-5 h-5 text-blue-400" />
                            Top Keywords
                        </h3>
                        <p className="text-sm text-gray-500 mb-4">Most frequently occurring keywords</p>
                        {keywords.length > 0 ? (
                            <ResponsiveContainer width="100%" height={400}>
                                <BarChart data={keywords.slice(0, 20)} margin={{ top: 10, right: 30, left: 0, bottom: 80 }}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
                                    <XAxis dataKey="keyword" stroke="#6B7280" angle={-45} textAnchor="end" height={100} interval={0} tick={{ fontSize: 12 }} />
                                    <YAxis stroke="#6B7280" />
                                    <Tooltip contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151', borderRadius: '8px' }} />
                                    <Bar dataKey="count" fill="#3B82F6" radius={[6, 6, 0, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        ) : <p className="text-gray-500 text-center py-12">No keyword data available</p>}
                    </Card>

                    {/* Sentiment + Trends Row */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Sentiment Pie */}
                        <Card className="p-6">
                            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                                <Shield className="w-5 h-5 text-green-400" />
                                Sentiment Distribution
                            </h3>
                            {sentimentPieData.length > 0 ? (
                                <div className="flex items-center gap-8">
                                    <ResponsiveContainer width="60%" height={250}>
                                        <PieChart>
                                            <Pie data={sentimentPieData} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={3} dataKey="value">
                                                {sentimentPieData.map((entry, i) => (
                                                    <Cell key={i} fill={entry.color} />
                                                ))}
                                            </Pie>
                                            <Tooltip contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151', borderRadius: '8px' }} />
                                        </PieChart>
                                    </ResponsiveContainer>
                                    <div className="space-y-3">
                                        {sentimentPieData.map((s, i) => (
                                            <div key={i} className="flex items-center gap-3">
                                                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: s.color }} />
                                                <span className="text-sm text-gray-400">{s.name}</span>
                                                <span className="text-sm font-bold text-white ml-auto">{s.value}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            ) : <p className="text-gray-500 text-center py-12">No sentiment data</p>}
                        </Card>

                        {/* Sentiment Timeline */}
                        <Card className="p-6">
                            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                                <Activity className="w-5 h-5 text-purple-400" />
                                Sentiment Over Time
                            </h3>
                            {sentiment.timeline?.length > 0 ? (
                                <ResponsiveContainer width="100%" height={250}>
                                    <LineChart data={sentiment.timeline}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
                                        <XAxis dataKey="date" stroke="#6B7280" tick={{ fontSize: 11 }} />
                                        <YAxis stroke="#6B7280" />
                                        <Tooltip contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151', borderRadius: '8px' }} />
                                        <Line type="monotone" dataKey="avg_sentiment" stroke="#8B5CF6" strokeWidth={2} dot={{ r: 4 }} name="Avg Sentiment" />
                                    </LineChart>
                                </ResponsiveContainer>
                            ) : <p className="text-gray-500 text-center py-12">No timeline data</p>}
                        </Card>
                    </div>

                    {/* Activity Trends */}
                    <Card className="p-6">
                        <h3 className="text-lg font-semibold text-white mb-1 flex items-center gap-2">
                            <Activity className="w-5 h-5 text-blue-400" />
                            Activity Trends
                        </h3>
                        <p className="text-sm text-gray-500 mb-4">URLs, keywords, sources, and titles over time</p>
                        {trends.length > 0 ? (
                            <ResponsiveContainer width="100%" height={350}>
                                <LineChart data={trends} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
                                    <XAxis dataKey="date" stroke="#6B7280" tick={{ fontSize: 11 }} />
                                    <YAxis stroke="#6B7280" />
                                    <Tooltip contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151', borderRadius: '8px' }} />
                                    <Legend />
                                    <Line type="monotone" dataKey="urls" stroke="#3B82F6" strokeWidth={2} dot={{ r: 3 }} name="URLs" />
                                    <Line type="monotone" dataKey="keywords" stroke="#8B5CF6" strokeWidth={2} dot={{ r: 3 }} name="Keywords" />
                                    <Line type="monotone" dataKey="sources" stroke="#10B981" strokeWidth={2} dot={{ r: 3 }} name="Sources" />
                                    <Line type="monotone" dataKey="titles" stroke="#F59E0B" strokeWidth={2} dot={{ r: 3 }} name="Titles" />
                                </LineChart>
                            </ResponsiveContainer>
                        ) : <p className="text-gray-500 text-center py-12">No trend data available</p>}
                    </Card>
                </motion.div>
            )}

            {/* GROUPS TAB */}
            {activeTab === 'groups' && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
                    <Card className="p-6">
                        <div className="flex items-center justify-between mb-4">
                            <div>
                                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                                    <FileText className="w-5 h-5 text-blue-400" />
                                    Grouped Titles ({groups.total || 0})
                                </h3>
                                <p className="text-sm text-gray-500 mt-1">Sites sharing the same title across multiple .onion domains</p>
                            </div>
                        </div>
                        <div className="relative mb-4">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                            <input
                                type="text" placeholder="Search titles..." value={groupSearch}
                                onChange={(e) => setGroupSearch(e.target.value)}
                                className="w-full pl-10 pr-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                            />
                        </div>
                        <div className="space-y-2 max-h-[600px] overflow-y-auto">
                            {filteredGroups.length === 0 ? (
                                <p className="text-gray-500 text-center py-8">No groups found</p>
                            ) : filteredGroups.map((g: any, i: number) => (
                                <motion.div key={i} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.02 }}>
                                    <div className="border border-gray-700 rounded-lg overflow-hidden">
                                        <button
                                            onClick={() => setExpandedGroup(expandedGroup === g.title ? null : g.title)}
                                            className="w-full px-4 py-3 bg-gray-800/50 hover:bg-gray-800 transition-colors flex items-center justify-between"
                                        >
                                            <div className="flex items-center gap-3 text-left flex-1 min-w-0">
                                                {expandedGroup === g.title ? <ChevronDown className="w-4 h-4 text-blue-400 flex-shrink-0" /> : <ChevronRight className="w-4 h-4 text-gray-500 flex-shrink-0" />}
                                                <span className="text-white font-medium truncate">{g.title}</span>
                                            </div>
                                            <div className="flex items-center gap-3 flex-shrink-0 ml-4">
                                                <span className="px-2.5 py-1 bg-blue-500/10 text-blue-400 rounded-full text-xs font-semibold">{g.url_count} URLs</span>
                                                <span className="px-2.5 py-1 bg-green-500/10 text-green-400 rounded-full text-xs font-semibold">{g.domain_count} domains</span>
                                            </div>
                                        </button>
                                        <AnimatePresence>
                                            {expandedGroup === g.title && (
                                                <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.2 }} className="overflow-hidden">
                                                    <div className="p-4 bg-gray-900/50 space-y-3">
                                                        {/* Content summary */}
                                                        {g.summary && (
                                                            <div className="p-3 bg-gray-800/80 rounded-lg border border-gray-700/50 space-y-2">
                                                                <p className="text-xs text-gray-400 uppercase tracking-wider font-semibold">Content Summary</p>
                                                                {g.summary.top_keywords?.length > 0 && (
                                                                    <div className="flex flex-wrap gap-1.5">
                                                                        <span className="text-xs text-gray-500 mr-1">Keywords:</span>
                                                                        {g.summary.top_keywords.map((kw: string, ki: number) => (
                                                                            <span key={ki} className="px-2 py-0.5 bg-blue-500/10 text-blue-400 rounded text-xs">{kw}</span>
                                                                        ))}
                                                                    </div>
                                                                )}
                                                                <div className="flex flex-wrap items-center gap-3 text-xs">
                                                                    <span className="text-gray-500">Sentiment:</span>
                                                                    <span className="text-green-400">▲ {g.summary.sentiment?.positive || 0} positive</span>
                                                                    <span className="text-gray-400">● {g.summary.sentiment?.neutral || 0} neutral</span>
                                                                    <span className="text-red-400">▼ {g.summary.sentiment?.negative || 0} negative</span>
                                                                    <span className="text-gray-500">(avg: {g.summary.sentiment?.avg?.toFixed(2) || '0.00'})</span>
                                                                </div>
                                                                {g.summary.languages?.length > 0 && (
                                                                    <div className="flex items-center gap-2 text-xs">
                                                                        <span className="text-gray-500">Languages:</span>
                                                                        {g.summary.languages.map((l: any, li: number) => (
                                                                            <span key={li} className="px-2 py-0.5 bg-purple-500/10 text-purple-400 rounded">{l.lang} ({l.count})</span>
                                                                        ))}
                                                                    </div>
                                                                )}
                                                            </div>
                                                        )}
                                                        {/* URLs */}
                                                        <div className="space-y-2 max-h-60 overflow-y-auto">
                                                            {g.urls.map((url: string, j: number) => (
                                                                <div key={j} className="flex items-center gap-2 p-2 bg-gray-800 rounded text-sm">
                                                                    <Globe className="w-3.5 h-3.5 text-green-400 flex-shrink-0" />
                                                                    <span className="text-gray-300 font-mono text-xs break-all">{url}</span>
                                                                    <button onClick={() => navigator.clipboard.writeText(url)} className="ml-auto flex-shrink-0 p-1 hover:bg-gray-700 rounded" title="Copy URL">
                                                                        <Copy className="w-3.5 h-3.5 text-gray-500" />
                                                                    </button>
                                                                </div>
                                                            ))}
                                                        </div>
                                                    </div>
                                                </motion.div>
                                            )}
                                        </AnimatePresence>
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    </Card>
                </motion.div>
            )}

            {/* MIRRORS TAB */}
            {activeTab === 'mirrors' && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
                    {/* Mirror Summary */}
                    {mirrors.summary && Object.keys(mirrors.summary).length > 0 && (
                        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                            {[
                                { label: 'Total Clusters', value: mirrors.summary.total_mirror_clusters, color: '#3B82F6' },
                                { label: 'Mirrored Domains', value: mirrors.summary.total_mirrored_domains, color: '#8B5CF6' },
                                { label: 'Exact Matches', value: mirrors.summary.exact_matches, color: '#10B981' },
                                { label: 'Near Matches', value: mirrors.summary.near_matches, color: '#F59E0B' },
                            ].map((m, i) => (
                                <Card key={i} className="p-4">
                                    <p className="text-xs text-gray-400 uppercase tracking-wider">{m.label}</p>
                                    <p className="text-2xl font-bold mt-1" style={{ color: m.color }}>{m.value ?? 0}</p>
                                </Card>
                            ))}
                        </div>
                    )}
                    {/* Mirror Clusters */}
                    <div className="space-y-4">
                        {mirrors.clusters?.length === 0 ? (
                            <Card className="p-12">
                                <div className="text-center">
                                    <Layers className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                                    <p className="text-gray-500">No mirror clusters detected</p>
                                    <p className="text-sm text-gray-600 mt-2">Mirror detection runs as part of the pipeline</p>
                                </div>
                            </Card>
                        ) : mirrors.clusters?.map((c: any, i: number) => (
                            <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}>
                                <Card className="p-6">
                                    <div className="flex items-start justify-between mb-3">
                                        <div className="flex-1 min-w-0">
                                            <h4 className="text-white font-semibold truncate">{c.title}</h4>
                                            <div className="flex items-center gap-3 mt-1">
                                                <span className={`px-2 py-0.5 rounded text-xs font-semibold ${c.mirror_type === 'exact' ? 'bg-green-500/20 text-green-400' : c.mirror_type === 'near' ? 'bg-yellow-500/20 text-yellow-400' : 'bg-blue-500/20 text-blue-400'}`}>
                                                    {c.mirror_type}
                                                </span>
                                                <span className="text-sm text-gray-400">Confidence: {(c.confidence * 100).toFixed(0)}%</span>
                                            </div>
                                        </div>
                                        <span className="px-3 py-1 bg-purple-500/10 text-purple-400 rounded-lg text-sm font-semibold">{c.num_mirrors} mirrors</span>
                                    </div>
                                    <div className="space-y-1.5">
                                        {(mirrorShowAll[i] ? c.domains : c.domains?.slice(0, 5))?.map((d: string, j: number) => (
                                            <div key={j} className="flex items-center gap-2 px-3 py-1.5 bg-gray-800 rounded text-xs font-mono text-gray-300">
                                                <Globe className="w-3 h-3 text-green-400 flex-shrink-0" />
                                                <span className="truncate">{d}</span>
                                            </div>
                                        ))}
                                        {c.domains?.length > 5 && (
                                            <button
                                                onClick={() => setMirrorShowAll(prev => ({ ...prev, [i]: !prev[i] }))}
                                                className="w-full py-1.5 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg text-xs font-medium text-cyan-400 transition-colors mt-1"
                                            >
                                                {mirrorShowAll[i] ? 'Show Less' : `Show All ${c.domains.length} Domains`}
                                            </button>
                                        )}
                                    </div>
                                </Card>
                            </motion.div>
                        ))}
                    </div>
                </motion.div>
            )}

            {/* ACTORS TAB */}
            {activeTab === 'actors' && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
                    {/* Totals */}
                    <div className="grid grid-cols-3 gap-4">
                        <Card className="p-4">
                            <div className="flex items-center gap-3">
                                <Bitcoin className="w-6 h-6 text-orange-400" />
                                <div>
                                    <p className="text-xs text-gray-400">BTC Wallets</p>
                                    <p className="text-2xl font-bold text-orange-400">{actors.totals?.btc_wallets || 0}</p>
                                </div>
                            </div>
                        </Card>
                        <Card className="p-4">
                            <div className="flex items-center gap-3">
                                <Key className="w-6 h-6 text-cyan-400" />
                                <div>
                                    <p className="text-xs text-gray-400">PGP Keys</p>
                                    <p className="text-2xl font-bold text-cyan-400">{actors.totals?.pgp_keys || 0}</p>
                                </div>
                            </div>
                        </Card>
                        <Card className="p-4">
                            <div className="flex items-center gap-3">
                                <Mail className="w-6 h-6 text-blue-400" />
                                <div>
                                    <p className="text-xs text-gray-400">Emails</p>
                                    <p className="text-2xl font-bold text-blue-400">{actors.totals?.emails || 0}</p>
                                </div>
                            </div>
                        </Card>
                    </div>

                    {/* BTC Wallets Table */}
                    {actors.btc_wallets?.length > 0 && (
                        <Card className="p-6">
                            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                                <Bitcoin className="w-5 h-5 text-orange-400" />
                                Bitcoin Wallets
                            </h3>
                            <div className="overflow-x-auto">
                                <table className="w-full">
                                    <thead>
                                        <tr className="border-b border-gray-700">
                                            <th className="text-left text-xs text-gray-400 uppercase py-2 px-3">Address</th>
                                            <th className="text-right text-xs text-gray-400 uppercase py-2 px-3">Occurrences</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {actors.btc_wallets.slice(0, 20).map((w: any, i: number) => (
                                            <tr key={i} className="border-b border-gray-800 hover:bg-gray-800/50">
                                                <td className="py-2.5 px-3 text-sm font-mono text-gray-300">{w.address}</td>
                                                <td className="py-2.5 px-3 text-right text-sm font-semibold text-orange-400">{w.count}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </Card>
                    )}

                    {/* Emails Table */}
                    {actors.emails?.length > 0 && (
                        <Card className="p-6">
                            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                                <Mail className="w-5 h-5 text-blue-400" />
                                Email Addresses
                            </h3>
                            <div className="overflow-x-auto">
                                <table className="w-full">
                                    <thead>
                                        <tr className="border-b border-gray-700">
                                            <th className="text-left text-xs text-gray-400 uppercase py-2 px-3">Email</th>
                                            <th className="text-right text-xs text-gray-400 uppercase py-2 px-3">Occurrences</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {actors.emails.slice(0, 20).map((e: any, i: number) => (
                                            <tr key={i} className="border-b border-gray-800 hover:bg-gray-800/50">
                                                <td className="py-2.5 px-3 text-sm font-mono text-gray-300">{e.email}</td>
                                                <td className="py-2.5 px-3 text-right text-sm font-semibold text-blue-400">{e.count}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </Card>
                    )}

                    {/* PGP Keys */}
                    {actors.pgp_keys?.length > 0 && (
                        <Card className="p-6">
                            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                                <Key className="w-5 h-5 text-cyan-400" />
                                PGP Keys ({actors.pgp_keys.length})
                            </h3>
                            <div className="space-y-2">
                                {actors.pgp_keys.slice(0, 10).map((k: any, i: number) => (
                                    <div key={i} className="p-3 bg-gray-800 rounded-lg border border-gray-700">
                                        <p className="text-xs font-mono text-gray-400 break-all">{k.key_preview}...</p>
                                    </div>
                                ))}
                            </div>
                        </Card>
                    )}

                    {!actors.btc_wallets?.length && !actors.emails?.length && !actors.pgp_keys?.length && (
                        <Card className="p-12">
                            <div className="text-center">
                                <Key className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                                <p className="text-gray-500">No actor intelligence found</p>
                            </div>
                        </Card>
                    )}
                </motion.div>
            )}

            {/* EVOLUTION TAB */}
            {activeTab === 'evolution' && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
                    {/* Summary */}
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                        <Card className="p-4">
                            <p className="text-xs text-gray-400 uppercase tracking-wider">Total Titles</p>
                            <p className="text-2xl font-bold text-cyan-400 mt-1">{evolution.total_titles || 0}</p>
                        </Card>
                        <Card className="p-4">
                            <p className="text-xs text-gray-400 uppercase tracking-wider">Total URLs</p>
                            <p className="text-2xl font-bold text-purple-400 mt-1">{evolution.total_urls || 0}</p>
                        </Card>
                        <Card className="p-4">
                            <p className="text-xs text-gray-400 uppercase tracking-wider">Dates in Range</p>
                            <p className="text-2xl font-bold text-blue-400 mt-1">{evolution.available_dates?.length || 0}</p>
                        </Card>
                        <Card className="p-4">
                            <p className="text-xs text-gray-400 uppercase tracking-wider">Date Range</p>
                            <p className="text-sm font-semibold text-white mt-1">
                                {evolution.available_dates?.length > 0
                                    ? `${evolution.available_dates[0]} → ${evolution.available_dates[evolution.available_dates.length - 1]}`
                                    : 'N/A'}
                            </p>
                        </Card>
                    </div>

                    <Card className="p-6">
                        <div className="flex items-center gap-3 mb-6">
                            <GitBranch className="w-6 h-6 text-cyan-400" />
                            <div>
                                <h3 className="text-lg font-semibold text-white">URL Evolution by Title</h3>
                                <p className="text-sm text-gray-500">For each title, links are grouped by their date-span pattern</p>
                            </div>
                        </div>
                        {!evolution.title_groups?.length ? (
                            <div className="text-center py-12">
                                <GitBranch className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                                <p className="text-gray-500">No evolution data available</p>
                            </div>
                        ) : (
                            <div className="space-y-3">
                                {evolution.title_groups.map((titleGrp: any, ti: number) => {
                                    const isTitleExpanded = expandedEvoGroup === titleGrp.title;
                                    return (
                                        <motion.div key={ti} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: ti * 0.03 }}>
                                            <div className="border border-gray-700 rounded-lg overflow-hidden">
                                                <button
                                                    onClick={() => setExpandedEvoGroup(isTitleExpanded ? null : titleGrp.title)}
                                                    className="w-full px-5 py-4 bg-gray-800/60 hover:bg-gray-800 transition-colors flex items-center justify-between"
                                                >
                                                    <div className="flex items-center gap-3 flex-1 min-w-0">
                                                        {isTitleExpanded ? <ChevronDown className="w-5 h-5 text-cyan-400 flex-shrink-0" /> : <ChevronRight className="w-5 h-5 text-gray-500 flex-shrink-0" />}
                                                        <div className="text-left min-w-0">
                                                            <p className="text-white font-semibold truncate">{titleGrp.title}</p>
                                                            <p className="text-xs text-gray-500 mt-0.5">{titleGrp.total_spans} date span{titleGrp.total_spans > 1 ? 's' : ''}</p>
                                                        </div>
                                                    </div>
                                                    <span className="px-3 py-1 bg-cyan-500/10 text-cyan-400 rounded-full text-sm font-bold flex-shrink-0 ml-4">
                                                        {titleGrp.total_urls} URLs
                                                    </span>
                                                </button>
                                                <AnimatePresence>
                                                    {isTitleExpanded && (
                                                        <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.2 }} className="overflow-hidden">
                                                            <div className="p-4 bg-gray-900/40 space-y-2">
                                                                {titleGrp.date_spans.map((span: any, si: number) => {
                                                                    const spanKey = `${titleGrp.title}__${span.label}`;
                                                                    const isSpanOpen = evoShowMore[`exp_${spanKey}`] || false;
                                                                    const showAll = evoShowMore[`all_${spanKey}`] || false;
                                                                    const visibleLinks = showAll ? span.links : span.links?.slice(0, 5);
                                                                    const hasMore = span.links?.length > 5;
                                                                    return (
                                                                        <div key={si} className="border border-gray-700/60 rounded-lg overflow-hidden">
                                                                            <button
                                                                                onClick={() => setEvoShowMore(prev => ({ ...prev, [`exp_${spanKey}`]: !isSpanOpen }))}
                                                                                className="w-full px-4 py-3 bg-gray-800/40 hover:bg-gray-800/70 transition-colors flex items-center justify-between"
                                                                            >
                                                                                <div className="flex items-center gap-2 flex-1 min-w-0">
                                                                                    {isSpanOpen ? <ChevronDown className="w-3.5 h-3.5 text-purple-400 flex-shrink-0" /> : <ChevronRight className="w-3.5 h-3.5 text-gray-600 flex-shrink-0" />}
                                                                                    <span className="text-sm text-gray-300 truncate">{span.label}</span>
                                                                                </div>
                                                                                <div className="flex items-center gap-2 flex-shrink-0 ml-3">
                                                                                    <span className="px-2.5 py-1 bg-blue-500/10 text-blue-400 rounded-full text-xs font-semibold">{span.count} links</span>
                                                                                    <span className={`px-2 py-0.5 rounded text-xs font-semibold ${span.span_type === 'full_range' ? 'bg-cyan-500/20 text-cyan-400' :
                                                                                        span.span_type === 'partial' ? 'bg-purple-500/20 text-purple-400' :
                                                                                            'bg-gray-600/30 text-gray-400'
                                                                                        }`}>
                                                                                        {span.span_type === 'full_range' ? 'All Days' : span.span_type === 'partial' ? 'Partial' : 'Single Day'}
                                                                                    </span>
                                                                                </div>
                                                                            </button>
                                                                            <AnimatePresence>
                                                                                {isSpanOpen && (
                                                                                    <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.15 }} className="overflow-hidden">
                                                                                        <div className="p-3 bg-gray-900/60 space-y-1.5">
                                                                                            <div className="max-h-[400px] overflow-y-auto space-y-1.5 pr-1">
                                                                                                {visibleLinks?.map((link: any, li: number) => (
                                                                                                    <div key={li} className="flex items-center gap-2 p-2.5 bg-gray-800 rounded-lg border border-gray-700/50">
                                                                                                        <div className="w-6 h-6 bg-gradient-to-br from-cyan-500 to-blue-600 rounded flex items-center justify-center text-white text-xs font-bold flex-shrink-0">{li + 1}</div>
                                                                                                        <div className="flex-1 min-w-0">
                                                                                                            <div className="flex items-center gap-2">
                                                                                                                <Globe className="w-3 h-3 text-green-400 flex-shrink-0" />
                                                                                                                <p className="text-xs text-gray-300 font-mono truncate">{link.domain}</p>
                                                                                                            </div>
                                                                                                            <p className="text-xs text-gray-500 font-mono truncate mt-0.5 pl-5">{link.url}</p>

                                                                                                        </div>
                                                                                                        <button onClick={() => navigator.clipboard.writeText(link.url)} className="flex-shrink-0 p-1 hover:bg-gray-700 rounded" title="Copy">
                                                                                                            <Copy className="w-3 h-3 text-gray-600" />
                                                                                                        </button>
                                                                                                    </div>
                                                                                                ))}
                                                                                            </div>
                                                                                            {hasMore && (
                                                                                                <button
                                                                                                    onClick={() => setEvoShowMore(prev => ({ ...prev, [`all_${spanKey}`]: !showAll }))}
                                                                                                    className="w-full mt-1 py-1.5 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg text-xs font-medium text-cyan-400 transition-colors"
                                                                                                >
                                                                                                    {showAll ? 'Show Less' : `Show All ${span.links.length} Links`}
                                                                                                </button>
                                                                                            )}
                                                                                        </div>
                                                                                    </motion.div>
                                                                                )}
                                                                            </AnimatePresence>
                                                                        </div>
                                                                    );
                                                                })}
                                                            </div>
                                                        </motion.div>
                                                    )}
                                                </AnimatePresence>
                                            </div>
                                        </motion.div>
                                    );
                                })}
                            </div>
                        )}
                    </Card>
                </motion.div>
            )}
        </div>
    );
}
