import { useState } from 'react';
import { Calendar } from 'lucide-react';

interface DateRangePickerProps {
    onRangeChange: (start: string | null, end: string | null) => void;
}

export function DateRangePicker({ onRangeChange }: DateRangePickerProps) {
    const [preset, setPreset] = useState('all');
    const [customStart, setCustomStart] = useState('');
    const [customEnd, setCustomEnd] = useState('');

    const handlePreset = (p: string) => {
        setPreset(p);
        if (p === 'custom') return;
        if (p === 'all') {
            onRangeChange(null, null);
            return;
        }
        const end = new Date();
        const start = new Date();
        start.setDate(end.getDate() - parseInt(p));
        onRangeChange(
            start.toISOString().split('T')[0],
            end.toISOString().split('T')[0]
        );
    };

    const applyCustom = () => {
        if (customStart && customEnd) {
            onRangeChange(customStart, customEnd);
        }
    };

    return (
        <div className="flex items-center gap-3 flex-wrap">
            <Calendar className="w-4 h-4 text-gray-400" />
            {['all'].map((p) => (
                <button
                    key={p}
                    onClick={() => handlePreset(p)}
                    className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${preset === p
                        ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/30'
                        : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white border border-gray-700'
                        }`}
                >
                    {p === 'all' ? 'All Time' : `${p}d`}
                </button>
            ))}
            <button
                onClick={() => handlePreset('custom')}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${preset === 'custom'
                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/30'
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white border border-gray-700'
                    }`}
            >
                Custom
            </button>
            {preset === 'custom' && (
                <div className="flex items-center gap-2">
                    <input
                        type="date"
                        value={customStart}
                        onChange={(e) => setCustomStart(e.target.value)}
                        className="px-3 py-1.5 bg-gray-800 border border-gray-700 rounded-lg text-white text-sm focus:outline-none focus:border-blue-500"
                    />
                    <span className="text-gray-500">→</span>
                    <input
                        type="date"
                        value={customEnd}
                        onChange={(e) => setCustomEnd(e.target.value)}
                        className="px-3 py-1.5 bg-gray-800 border border-gray-700 rounded-lg text-white text-sm focus:outline-none focus:border-blue-500"
                    />
                    <button
                        onClick={applyCustom}
                        className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors"
                    >
                        Apply
                    </button>
                </div>
            )}
        </div>
    );
}
