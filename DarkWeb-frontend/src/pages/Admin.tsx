import { useState } from "react";
import { Card } from "../components/Card";
import {
  Settings,
  Play,
  CheckCircle,
  XCircle,
  Loader,
  Database,
  Activity,
} from "lucide-react";
import { motion } from "framer-motion";

interface ScriptLog {
  timestamp: string;
  status: "success" | "error" | "running";
  message: string;
}

export function Admin() {
  const [isRunning, setIsRunning] = useState(false);
  const [logs, setLogs] = useState<ScriptLog[]>([]);
  const [lastRun, setLastRun] = useState<string | null>(null);

  const runPipeline = async () => {
    setIsRunning(true);
    const timestamp = new Date().toISOString();

    setLogs((prev) => [
      ...prev,
      {
        timestamp,
        status: "running",
        message: "Starting data scraping pipeline...",
      },
    ]);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/pipeline/run-scripts",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        throw new Error(`Pipeline failed with status: ${response.status}`);
      }

      const data = await response.json();

      setLogs((prev) => [
        ...prev,
        {
          timestamp: new Date().toISOString(),
          status: "success",
          message: `Pipeline completed successfully: ${JSON.stringify(data)}`,
        },
      ]);

      setLastRun(new Date().toLocaleString());
    } catch (error) {
      setLogs((prev) => [
        ...prev,
        {
          timestamp: new Date().toISOString(),
          status: "error",
          message: `Pipeline failed: ${
            error instanceof Error ? error.message : "Unknown error"
          }`,
        },
      ]);
    } finally {
      setIsRunning(false);
    }
  };

  const clearLogs = () => {
    setLogs([]);
  };

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white flex items-center gap-3">
            <Settings className="w-8 h-8" />
            Admin Panel
          </h2>
          <p className="text-gray-400 mt-2">
            Manage data scraping and system operations
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4 bg-gradient-to-br from-blue-500/10 to-blue-600/5 border-blue-500/20">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-blue-500/20 rounded-lg">
              <Database className="w-6 h-6 text-blue-400" />
            </div>
            <div>
              <p className="text-sm text-gray-400">System Status</p>
              <p className="text-xl font-bold text-white">
                {isRunning ? "Running" : "Idle"}
              </p>
            </div>
          </div>
        </Card>

        <Card className="p-4 bg-gradient-to-br from-green-500/10 to-green-600/5 border-green-500/20">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-green-500/20 rounded-lg">
              <Activity className="w-6 h-6 text-green-400" />
            </div>
            <div>
              <p className="text-sm text-gray-400">Last Run</p>
              <p className="text-sm font-medium text-white">
                {lastRun || "06-10-2025"}
              </p>
            </div>
          </div>
        </Card>

        <Card className="p-4 bg-gradient-to-br from-purple-500/10 to-purple-600/5 border-purple-500/20">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-purple-500/20 rounded-lg">
              <CheckCircle className="w-6 h-6 text-purple-400" />
            </div>
            <div>
              <p className="text-sm text-gray-400">Total Runs</p>
              <p className="text-xl font-bold text-white">
                {/* {logs.filter((log) => log.status === "success").length} */}
                14
              </p>
            </div>
          </div>
        </Card>
      </div>

      <Card className="p-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-semibold text-white flex items-center gap-2">
                <Play className="w-5 h-5 text-blue-400" />
                Data Scraping Pipeline
              </h3>
              <p className="text-sm text-gray-400 mt-1">
                Execute the data collection scripts to gather today's dark web
                data
              </p>
            </div>
          </div>

          <div className="border-t border-gray-700 pt-4">
            <button
              onClick={runPipeline}
              disabled={isRunning}
              className={`
                flex items-center gap-3 px-6 py-3 rounded-lg font-semibold text-white
                transition-all transform hover:scale-105
                ${
                  isRunning
                    ? "bg-gray-600 cursor-not-allowed"
                    : "bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 shadow-lg shadow-blue-500/30"
                }
              `}
            >
              {isRunning ? (
                <>
                  <Loader className="w-5 h-5 animate-spin" />
                  Running Pipeline...
                </>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  Run Data Scraping Pipeline
                </>
              )}
            </button>

            <div className="mt-4 text-sm text-gray-400">
              <p className="font-semibold mb-2">What this does:</p>
              <ul className="list-disc list-inside space-y-1 ml-2">
                <li>Executes the data collection scripts</li>
                <li>Scrapes today's dark web data</li>
                <li>Processes and stores results in the database</li>
                <li>Updates analytics dashboards with fresh data</li>
              </ul>
            </div>
          </div>
        </div>
      </Card>

      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold text-white">Execution Logs</h3>
          {logs.length > 0 && (
            <button
              onClick={clearLogs}
              className="px-4 py-2 text-sm bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
            >
              Clear Logs
            </button>
          )}
        </div>

        <div className="space-y-2 max-h-96 overflow-y-auto">
          {logs.length === 0 ? (
            <div className="text-center py-12">
              <Activity className="w-12 h-12 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-500">No logs yet</p>
              <p className="text-sm text-gray-600 mt-2">
                Run the pipeline to see execution logs
              </p>
            </div>
          ) : (
            logs.map((log, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
                className={`
                  p-4 rounded-lg border
                  ${
                    log.status === "success"
                      ? "bg-green-500/5 border-green-500/20"
                      : log.status === "error"
                      ? "bg-red-500/5 border-red-500/20"
                      : "bg-blue-500/5 border-blue-500/20"
                  }
                `}
              >
                <div className="flex items-start gap-3">
                  {log.status === "success" && (
                    <CheckCircle className="w-5 h-5 text-green-400 mt-0.5" />
                  )}
                  {log.status === "error" && (
                    <XCircle className="w-5 h-5 text-red-400 mt-0.5" />
                  )}
                  {log.status === "running" && (
                    <Loader className="w-5 h-5 text-blue-400 mt-0.5 animate-spin" />
                  )}
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs text-gray-400">
                        {new Date(log.timestamp).toLocaleString()}
                      </span>
                      <span
                        className={`
                        px-2 py-0.5 rounded text-xs font-semibold
                        ${
                          log.status === "success"
                            ? "bg-green-500/20 text-green-400"
                            : log.status === "error"
                            ? "bg-red-500/20 text-red-400"
                            : "bg-blue-500/20 text-blue-400"
                        }
                      `}
                      >
                        {log.status.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-sm text-white break-all">
                      {log.message}
                    </p>
                  </div>
                </div>
              </motion.div>
            ))
          )}
        </div>
      </Card>
    </div>
  );
}
