"use client";
import { useState } from "react";
import { FileText, Link, Loader2, AlertCircle, CheckCircle, Copy, Maximize2, Minimize2, Sparkles, Zap, ArrowRight, Download, Share2 } from "lucide-react";

const UserInput = () => {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isExpanded, setIsExpanded] = useState(false);
  const [copied, setCopied] = useState(false);
  const [revised, setRevised] = useState<string | null>(null);
  const [revising, setRevising] = useState(false);

  // Store the last analyzed URL and result for revision
  const [lastUrl, setLastUrl] = useState<string | null>(null);
  const [lastContent, setLastContent] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    setRevised(null);
    setLastContent(null);
    
    try {
      const res = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Something went wrong");
      }

      const data = await res.json();
      setResult(data.analysis);  // Store analysis part
      setLastContent(data.content);  // Store content part
    } catch (err: Error | unknown) {
      setError(err instanceof Error ? err.message : "Error occurred");
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async () => {
    if (result) {
      try {
        await navigator.clipboard.writeText(result);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      } catch (err) {
        console.error('Failed to copy text: ', err);
      }
    }
  };

  const toggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  const handleRevise = async () => {
    if (!lastContent || !result) return;
    setRevising(true);
    setRevised(null);
    try {
      const res = await fetch("http://localhost:8000/revise", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          content: lastContent,
          suggestions: result  // This is now the analysis object
        }),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Revision failed");
      }
      const data = await res.json();
      setRevised(data.revised);
    } catch (err) {
      console.error('Revision error:', err);
      setRevised("Revision failed.");
    } finally {
      setRevising(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl animate-pulse delay-500"></div>
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-4 mb-6">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl blur opacity-75"></div>
              <div className="relative p-4 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl shadow-2xl">
                <Sparkles className="w-10 h-10 text-white" />
              </div>
            </div>
            <div>
              <h1 className="text-6xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-2">
                AI Doc Analyzer
              </h1>
              <div className="flex items-center justify-center gap-2 text-purple-300">
                <Zap className="w-4 h-4" />
                <span className="text-sm font-medium">Powered by Advanced AI</span>
              </div>
            </div>
          </div>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto leading-relaxed">
            Transform your documentation with AI-driven insights, analysis, and automated improvements
          </p>
        </div>

        {/* Input Section */}
        <div className="relative mb-8">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-purple-500/20 rounded-3xl blur-xl"></div>
          <div className="relative bg-white/10 backdrop-blur-xl rounded-3xl border border-white/20 shadow-2xl overflow-hidden">
            <div className="p-8">
              <div className="space-y-6">
                <div className="relative">
                  <label htmlFor="url" className="block text-sm font-semibold text-gray-200 mb-3">
                    Documentation URL
                  </label>
                  <div className="relative group">
                    <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-2xl blur opacity-25 group-focus-within:opacity-50 transition-opacity duration-300"></div>
                    <div className="relative flex items-center">
                      <Link className="absolute left-4 z-10 text-gray-400 w-5 h-5" />
                      <input
                        id="url"
                        type="url"
                        placeholder="https://docs.example.com/api/reference"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        required
                        className="w-full pl-12 pr-4 py-4 bg-white/10 backdrop-blur-sm border-2 border-white/20 rounded-2xl focus:outline-none focus:border-purple-400 focus:ring-4 focus:ring-purple-400/30 transition-all duration-300 text-white placeholder-gray-400"
                      />
                    </div>
                  </div>
                </div>
                
                <button
                  onClick={handleSubmit}
                  disabled={loading || !url.trim()}
                  className="w-full group relative overflow-hidden"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl blur opacity-75 group-hover:opacity-100 transition-opacity duration-300"></div>
                  <div className="relative bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-2xl px-6 py-4 font-semibold hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-4 focus:ring-purple-400/50 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-2xl">
                    {loading ? (
                      <div className="flex items-center justify-center gap-3">
                        <Loader2 className="w-5 h-5 animate-spin" />
                        <span>Analyzing Documentation...</span>
                        <div className="flex gap-1">
                          <div className="w-2 h-2 bg-white/60 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-white/60 rounded-full animate-bounce delay-100"></div>
                          <div className="w-2 h-2 bg-white/60 rounded-full animate-bounce delay-200"></div>
                        </div>
                      </div>
                    ) : (
                      <div className="flex items-center justify-center gap-3">
                        <Sparkles className="w-5 h-5" />
                        <span>Analyze Documentation</span>
                        <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform duration-300" />
                      </div>
                    )}
                  </div>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Error Section */}
        {error && (
          <div className="mb-8 animate-slide-up">
            <div className="relative">
              <div className="absolute inset-0 bg-red-500/20 rounded-2xl blur-xl"></div>
              <div className="relative bg-red-500/10 backdrop-blur-xl border border-red-500/30 rounded-2xl p-6">
                <div className="flex items-center gap-4">
                  <div className="p-2 bg-red-500/20 rounded-xl">
                    <AlertCircle className="w-6 h-6 text-red-400" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-red-300 mb-1">Analysis Failed</h3>
                    <p className="text-red-200">{error}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Results Section */}
        {result && (
          <div className="animate-slide-up">
            <div className="relative mb-8">
              <div className="absolute inset-0 bg-gradient-to-r from-green-500/20 to-emerald-500/20 rounded-3xl blur-xl"></div>
              <div className="relative bg-white/10 backdrop-blur-xl rounded-3xl border border-white/20 shadow-2xl overflow-hidden">
                {/* Results Header */}
                <div className="bg-gradient-to-r from-green-500/20 to-emerald-500/20 px-8 py-6 border-b border-white/10">
                  <div className="flex items-center justify-between flex-wrap gap-4">
                    <div className="flex items-center gap-4">
                      <div className="p-2 bg-green-500/20 rounded-xl">
                        <CheckCircle className="w-6 h-6 text-green-400" />
                      </div>
                      <div>
                        <h2 className="text-xl font-semibold text-white">
                          Analysis Complete
                        </h2>
                        <p className="text-green-300 text-sm">Ready for review and revision</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <button
                        onClick={handleCopy}
                        className="flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl hover:bg-white/20 transition-all duration-200 text-sm text-white group"
                      >
                        <Copy className="w-4 h-4 group-hover:scale-110 transition-transform duration-200" />
                        {copied ? "Copied!" : "Copy"}
                      </button>
                      <button
                        onClick={toggleExpand}
                        className="flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl hover:bg-white/20 transition-all duration-200 text-sm text-white group"
                      >
                        {isExpanded ? (
                          <>
                            <Minimize2 className="w-4 h-4 group-hover:scale-110 transition-transform duration-200" />
                            Collapse
                          </>
                        ) : (
                          <>
                            <Maximize2 className="w-4 h-4 group-hover:scale-110 transition-transform duration-200" />
                            Expand
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                </div>

                {/* Results Content */}
                <div className="p-8">
                  <div 
                    className={`bg-black/20 backdrop-blur-sm rounded-2xl border border-white/10 transition-all duration-300 ${
                      isExpanded ? 'p-8' : 'p-6'
                    }`}
                  >
                    <div 
                      className={`overflow-auto transition-all duration-300 ${
                        isExpanded 
                          ? 'max-h-screen' 
                          : 'max-h-96'
                      }`}
                      style={{ 
                        scrollbarWidth: 'thin', 
                        scrollbarColor: '#6366f1 transparent',
                      }}
                    >
                      <div className="prose prose-invert prose-sm max-w-none">
                        <pre className="whitespace-pre-wrap text-gray-200 leading-relaxed font-mono text-sm bg-transparent border-none p-0 m-0">
                          {result}
                        </pre>
                      </div>
                    </div>
                    
                    {!isExpanded && result.length > 1000 && (
                      <div className="mt-6 pt-4 border-t border-white/10 text-center">
                        <button
                          onClick={toggleExpand}
                          className="text-purple-400 hover:text-purple-300 font-medium flex items-center gap-2 mx-auto transition-colors duration-200 group"
                        >
                          <Maximize2 className="w-4 h-4 group-hover:scale-110 transition-transform duration-200" />
                          Show full analysis ({Math.ceil(result.length / 1000)}k+ characters)
                        </button>
                      </div>
                    )}
                  </div>
                </div>

                {/* Results Footer */}
                <div className="bg-black/20 px-8 py-4 border-t border-white/10">
                  <div className="flex items-center justify-between text-sm text-gray-300 flex-wrap gap-2">
                    <span className="truncate max-w-md flex items-center gap-2">
                      <Link className="w-4 h-4" />
                      {url}
                    </span>
                    <div className="flex items-center gap-6">
                      <span className="flex items-center gap-1">
                        <FileText className="w-4 h-4" />
                        {result.length.toLocaleString()} chars
                      </span>
                      <span>{result.split('\n').length} lines</span>
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex justify-between px-8 py-6 bg-gradient-to-r from-purple-500/10 to-blue-500/10 border-t border-white/10">
                  <div className="flex gap-3">
                    <button className="flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl hover:bg-white/20 transition-all duration-200 text-sm text-white">
                      <Download className="w-4 h-4" />
                      Export
                    </button>
                    <button className="flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl hover:bg-white/20 transition-all duration-200 text-sm text-white">
                      <Share2 className="w-4 h-4" />
                      Share
                    </button>
                  </div>
                  <button
                    onClick={handleRevise}
                    disabled={revising}
                    className="flex items-center gap-2 px-6 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-xl hover:from-purple-700 hover:to-blue-700 transition-all duration-200 text-sm disabled:opacity-50 shadow-lg hover:shadow-xl group"
                  >
                    {revising ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Revising...
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-4 h-4 group-hover:scale-110 transition-transform duration-200" />
                        Revise Main Doc
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Revised Article Section */}
        {revised && (
          <div className="animate-slide-up">
            <div className="relative mb-8">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-indigo-500/20 rounded-3xl blur-xl"></div>
              <div className="relative bg-white/10 backdrop-blur-xl rounded-3xl border border-white/20 shadow-2xl overflow-hidden">
                <div className="bg-gradient-to-r from-blue-500/20 to-indigo-500/20 px-8 py-6 border-b border-white/10">
                  <div className="flex items-center gap-4">
                    <div className="p-2 bg-blue-500/20 rounded-xl">
                      <CheckCircle className="w-6 h-6 text-blue-400" />
                    </div>
                    <div>
                      <h2 className="text-xl font-semibold text-white">
                        Revised Documentation
                      </h2>
                      <p className="text-blue-300 text-sm">AI-enhanced and optimized</p>
                    </div>
                  </div>
                </div>
                <div className="p-8">
                  <div className="bg-black/20 backdrop-blur-sm rounded-2xl border border-white/10 p-6">
                    <div className="prose prose-invert prose-sm max-w-none">
                      <pre className="whitespace-pre-wrap text-gray-200 leading-relaxed font-mono text-sm bg-transparent border-none p-0 m-0">
                        {revised}
                      </pre>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="animate-slide-up">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-purple-500/20 to-blue-500/20 rounded-3xl blur-xl"></div>
              <div className="relative bg-white/10 backdrop-blur-xl rounded-3xl border border-white/20 shadow-2xl p-12 text-center">
                <div className="flex flex-col items-center gap-8">
                  <div className="relative">
                    <div className="w-24 h-24 border-4 border-purple-500/30 rounded-full"></div>
                    <div className="w-24 h-24 border-4 border-purple-500 border-t-transparent rounded-full animate-spin absolute top-0 left-0"></div>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <Sparkles className="w-8 h-8 text-purple-400 animate-pulse" />
                    </div>
                  </div>
                  <div>
                    <h3 className="text-2xl font-semibold text-white mb-3">
                      Analyzing Documentation
                    </h3>
                    <p className="text-gray-300 max-w-md leading-relaxed">
                      Our AI is processing your documentation with advanced language models. This may take a few moments.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && !result && !error && (
          <div className="animate-slide-up">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-gray-500/10 to-gray-600/10 rounded-3xl blur-xl"></div>
              <div className="relative bg-white/5 backdrop-blur-xl rounded-3xl border border-white/10 shadow-2xl p-12 text-center">
                <div className="flex flex-col items-center gap-6">
                  <div className="relative">
                    <div className="absolute inset-0 bg-gradient-to-r from-gray-500 to-gray-600 rounded-2xl blur opacity-30"></div>
                    <div className="relative p-6 bg-gradient-to-r from-gray-600/20 to-gray-700/20 rounded-2xl border border-white/10">
                      <FileText className="w-12 h-12 text-gray-400" />
                    </div>
                  </div>
                  <div>
                    <h3 className="text-2xl font-semibold text-white mb-3">
                      Ready to Analyze
                    </h3>
                    <p className="text-gray-300 max-w-md leading-relaxed">
                      Enter a documentation URL above to get started with AI-powered analysis, insights, and automated improvements.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="text-center mt-16">
          <div className="flex items-center justify-center gap-4 text-gray-400 text-sm mb-4">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4" />
              <span>Powered by Advanced AI</span>
            </div>
            <div className="w-1 h-1 bg-gray-500 rounded-full"></div>
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4" />
              <span>Secure & Fast Analysis</span>
            </div>
          </div>
          <p className="text-gray-500 text-xs">© 2025 AI Doc Analyzer. Built with cutting-edge technology.</p>
        </div>
      </div>

      <style jsx>{`
        @keyframes slide-up {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        .animate-slide-up {
          animation: slide-up 0.6s ease-out;
        }

        /* Custom scrollbar for webkit browsers */
        ::-webkit-scrollbar {
          width: 6px;
        }
        
        ::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.1);
          border-radius: 3px;
        }
        
        ::-webkit-scrollbar-thumb {
          background: rgba(99, 102, 241, 0.6);
          border-radius: 3px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
          background: rgba(99, 102, 241, 0.8);
        }
      `}</style>
    </div>
  );
};

export default UserInput;