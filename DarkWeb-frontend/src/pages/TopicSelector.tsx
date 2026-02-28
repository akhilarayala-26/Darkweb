import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../components/Card';
import { Shield, Pill, CreditCard, Crosshair, ArrowRight, Database, Calendar, Globe } from 'lucide-react';
import { motion } from 'framer-motion';
import { API_BASE_URL } from '../config';

interface TopicInfo {
    id: string;
    label: string;
    icon: string;
    color: string;
    total_records: number;
    total_pipeline_runs: number;
    first_date: string | null;
    last_date: string | null;
}

const ICON_MAP: Record<string, any> = {
    pill: Pill,
    'credit-card': CreditCard,
    crosshair: Crosshair,
};

export function TopicSelector() {
    const [topics, setTopics] = useState<TopicInfo[]>([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        fetchTopics();
    }, []);

    const fetchTopics = async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/dashboard/topics`);
            const data = await res.json();
            setTopics(data.topics || []);
        } catch (e) {
            console.error('Error fetching topics:', e);
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
        <div className="min-h-full flex flex-col items-center justify-center p-8">
            <motion.div
                initial={{ opacity: 0, y: -30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                className="text-center mb-12"
            >
                <div className="flex items-center justify-center gap-4 mb-6">
                    <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-500/30">
                        <Shield className="w-9 h-9 text-white" />
                    </div>
                </div>
                <h1 className="text-4xl font-bold text-white mb-3">
                    Dark Web Intelligence
                </h1>
                <p className="text-gray-400 text-lg max-w-xl mx-auto">
                    Select a threat category to view comprehensive analysis, visualizations, and intelligence reports
                </p>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 w-full max-w-5xl">
                {topics.map((topic, index) => {
                    const IconComponent = ICON_MAP[topic.icon] || Globe;
                    return (
                        <motion.div
                            key={topic.id}
                            initial={{ opacity: 0, y: 40 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5, delay: index * 0.15 }}
                        >
                            <div
                                onClick={() => navigate(`/topic/${topic.id}`)}
                                className="group cursor-pointer"
                            >
                                <Card hover className="p-8 relative overflow-hidden">
                                    {/* Gradient accent bar */}
                                    <div
                                        className="absolute top-0 left-0 right-0 h-1 opacity-80"
                                        style={{ background: `linear-gradient(90deg, ${topic.color}, ${topic.color}88)` }}
                                    />

                                    {/* Icon */}
                                    <div
                                        className="w-14 h-14 rounded-xl flex items-center justify-center mb-6"
                                        style={{ backgroundColor: `${topic.color}20` }}
                                    >
                                        <IconComponent className="w-7 h-7" style={{ color: topic.color }} />
                                    </div>

                                    {/* Title */}
                                    <h3 className="text-2xl font-bold text-white mb-2 group-hover:text-blue-400 transition-colors">
                                        {topic.label}
                                    </h3>

                                    {/* Stats */}
                                    <div className="space-y-3 mt-6">
                                        <div className="flex items-center gap-3 text-sm">
                                            <Database className="w-4 h-4 text-gray-500" />
                                            <span className="text-gray-400">Records:</span>
                                            <span className="text-white font-semibold ml-auto">
                                                {topic.total_records.toLocaleString()}
                                            </span>
                                        </div>
                                        <div className="flex items-center gap-3 text-sm">
                                            <Calendar className="w-4 h-4 text-gray-500" />
                                            <span className="text-gray-400">Pipeline Runs:</span>
                                            <span className="text-white font-semibold ml-auto">
                                                {topic.total_pipeline_runs}
                                            </span>
                                        </div>
                                        {topic.last_date && (
                                            <div className="flex items-center gap-3 text-sm">
                                                <Globe className="w-4 h-4 text-gray-500" />
                                                <span className="text-gray-400">Latest Data:</span>
                                                <span className="text-white font-semibold ml-auto">
                                                    {topic.last_date}
                                                </span>
                                            </div>
                                        )}
                                    </div>

                                    {/* CTA */}
                                    <div className="mt-8 flex items-center gap-2 text-sm font-medium group-hover:gap-3 transition-all"
                                        style={{ color: topic.color }}
                                    >
                                        <span>View Analysis</span>
                                        <ArrowRight className="w-4 h-4" />
                                    </div>
                                </Card>
                            </div>
                        </motion.div>
                    );
                })}
            </div>
        </div>
    );
}
