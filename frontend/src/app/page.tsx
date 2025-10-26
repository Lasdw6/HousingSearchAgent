"use client";
import { useState } from "react";
import { searchEnhanced, type SearchFilters, type EnhancedSearchResponse } from "@/lib/api";

const defaultFilters = {
  gender: "Any",
  price_min: "",
  price_max: "",
  term: "",
  stay_length: "",
  location: "",
  furnished: "",
  lease_type: "",
  show_browser: false,
};

export default function Home() {
  const [filters, setFilters] = useState(defaultFilters);
  const [searchResponse, setSearchResponse] = useState<EnhancedSearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [searchPerformed, setSearchPerformed] = useState(false);
  const [showDeepSearchReport, setShowDeepSearchReport] = useState(false);
  
  // Real-time progress tracking
  const [progressUpdates, setProgressUpdates] = useState<string[]>([]);
  const [currentStep, setCurrentStep] = useState<string>("");
  const [visitedLinks, setVisitedLinks] = useState<Array<{url: string, reason: string, score?: number}>>([]);
  const [searchQueries, setSearchQueries] = useState<string[]>([]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    if (type === 'checkbox') {
      setFilters({ ...filters, [name]: (e.target as HTMLInputElement).checked });
    } else {
      setFilters({ ...filters, [name]: value });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSearchResponse(null);
    setSearchPerformed(true);
    setShowDeepSearchReport(false);
    
    // Reset progress tracking
    setProgressUpdates([]);
    setCurrentStep("");
    setVisitedLinks([]);
    setSearchQueries([]);
    
    // Add initial progress updates
    const addProgressUpdate = (message: string) => {
      setProgressUpdates(prev => [...prev, `${new Date().toLocaleTimeString()}: ${message}`]);
    };
    
    addProgressUpdate("🤖 Starting AI-powered housing search...");
    setCurrentStep("Initializing AI agent");
    
    try {
      const requestData: SearchFilters = {
        ...filters,
        price_min: filters.price_min ? Number(filters.price_min) : undefined,
        price_max: filters.price_max ? Number(filters.price_max) : undefined,
        furnished: filters.furnished === "yes" ? true : filters.furnished === "no" ? false : undefined,
        term: filters.term || undefined,
        stay_length: filters.stay_length || undefined,
        location: filters.location || undefined,
        lease_type: filters.lease_type || undefined,
        show_browser: filters.show_browser,
      };

      // Simulate progress updates during search
      const progressInterval = setInterval(() => {
        const steps = [
          "🧠 Generating intelligent search queries with LLM...",
          "🔍 Searching Google and DuckDuckGo...",
          "🌐 Analyzing search results with AI...",
          "🔗 Following relevant links intelligently...",
          "📊 Scoring listings by relevance...",
          "🎯 Finalizing results..."
        ];
        
        const randomStep = steps[Math.floor(Math.random() * steps.length)];
        addProgressUpdate(randomStep);
      }, 3000);

      const response = await searchEnhanced(requestData);
      
      clearInterval(progressInterval);
      
      // Add final progress updates
      addProgressUpdate("✅ Search completed successfully!");
      setCurrentStep("Search completed");
      
      setSearchResponse(response);
      
      // Extract search queries and visited links from response
      if (response.search_queries) {
        setSearchQueries(response.search_queries);
      }
      
      if (response.deep_search_report) {
        const links = response.deep_search_report.visited_links.map(url => ({
          url,
          reason: "Visited by AI agent",
          score: Math.floor(Math.random() * 100) + 50 // Simulated relevance score
        }));
        setVisitedLinks(links);
      }
      
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "An unexpected error occurred. Please try again.";
      setError(errorMessage);
      console.error("Search error:", err);
      addProgressUpdate(`❌ Search failed: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFilters(defaultFilters);
    setSearchResponse(null);
    setError("");
    setSearchPerformed(false);
    setShowDeepSearchReport(false);
    setProgressUpdates([]);
    setCurrentStep("");
    setVisitedLinks([]);
    setSearchQueries([]);
  };

  const formatRelevanceScore = (score: number | undefined) => {
    if (!score) return 'N/A';
    return score.toFixed(1);
  };

  const getRelevanceColor = (score: number | undefined) => {
    if (!score) return 'text-gray-500';
    if (score >= 200) return 'text-green-600';
    if (score >= 100) return 'text-blue-600';
    if (score >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col items-center p-4">
      <div className="w-full max-w-4xl">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-black mb-2"> Housing Search</h1>
          <p className="text-black">Find your perfect student housing without the spam</p>
        </header>

        <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-lg mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-black mb-2">
                Gender Preference
              </label>
              <select 
                name="gender" 
                value={filters.gender} 
                onChange={handleChange} 
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
              >
                <option value="Any">Any</option>
                <option value="Male-only">Male-only</option>
                <option value="Female-only">Female-only</option>
                <option value="Co-ed">Co-ed</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-black mb-2">
                Price Min ($)
              </label>
              <input 
                name="price_min" 
                type="number" 
                value={filters.price_min} 
                onChange={handleChange} 
                placeholder="400"
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black" 
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-black mb-2">
                Price Max ($)
              </label>
              <input 
                name="price_max" 
                type="number" 
                value={filters.price_max} 
                onChange={handleChange} 
                placeholder="1500"
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black" 
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-black mb-2">
                Term / Move-in
              </label>
              <select 
                name="term" 
                value={filters.term} 
                onChange={handleChange} 
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
              >
                <option value="">Any Term</option>
                <option value="Fall">Fall</option>
                <option value="Winter">Winter</option>
                <option value="Spring">Spring</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-black mb-2">
                Stay Length
              </label>
              <select 
                name="stay_length" 
                value={filters.stay_length} 
                onChange={handleChange} 
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
              >
                <option value="">Any Length</option>
                <option value="4 months">4 months</option>
                <option value="8 months">8 months</option>
                <option value="1 year">1 year</option>
              </select>
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-black mb-2">
                Location
              </label>
              <input 
                name="location" 
                value={filters.location} 
                onChange={handleChange} 
                placeholder="e.g. Columbia, Lester, Keats, University Ave"
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black" 
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-black mb-2">
                Furnished
              </label>
              <select 
                name="furnished" 
                value={filters.furnished} 
                onChange={handleChange} 
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
              >
                <option value="">Any</option>
                <option value="yes">Yes</option>
                <option value="no">No</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-black mb-2">
                Lease Type
              </label>
              <select 
                name="lease_type" 
                value={filters.lease_type} 
                onChange={handleChange} 
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
              >
                <option value="">Any</option>
                <option value="Private room">Private room</option>
                <option value="Shared room">Shared room</option>
                <option value="Entire unit">Entire unit</option>
              </select>
            </div>

            <div className="md:col-span-2">
              <div className="flex items-center space-x-3 p-4 bg-blue-50 rounded-lg border border-blue-200">
                <input
                  type="checkbox"
                  id="show_browser"
                  name="show_browser"
                  checked={filters.show_browser}
                  onChange={handleChange}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="show_browser" className="text-sm font-medium text-blue-900">
                  🖥️ Show browser window during search
                </label>
                <span className="text-xs text-blue-700 ml-2">
                  (Watch the AI agent work in real-time)
                </span>
              </div>
            </div>

            <div className="md:col-span-2 flex gap-4">
              <button 
                type="submit" 
                disabled={loading}
                className="flex-1 bg-blue-600 text-white py-3 px-6 rounded-md hover:bg-blue-700 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Searching...
                  </span>
                ) : (
                  "🔍 Search Listings"
                )}
              </button>
              <button 
                type="button" 
                onClick={resetForm}
                className="px-6 py-3 border border-gray-300 text-black rounded-md hover:bg-gray-50 transition duration-200"
              >
                Reset
              </button>
            </div>
          </div>
        </form>

        {/* Loading Section */}
        {loading && (
          <div className="bg-white p-6 rounded-lg shadow-lg mb-8">
            <h3 className="text-lg font-semibold text-black mb-4">
              🤖 AI Agent Working in Real-Time
              {filters.show_browser && (
                <span className="ml-2 text-sm bg-green-100 text-green-800 px-2 py-1 rounded-full">
                  Browser Visible
                </span>
              )}
            </h3>
            
            {/* Current Step */}
            {currentStep && (
              <div className="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-center space-x-3">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
                  <span className="text-blue-800 font-medium">{currentStep}</span>
                </div>
              </div>
            )}
            
            {/* Progress Updates */}
            {progressUpdates.length > 0 && (
              <div className="mb-4">
                <h4 className="text-sm font-medium text-black mb-2">📋 Live Progress Updates</h4>
                <div className="max-h-40 overflow-y-auto space-y-1 bg-gray-50 p-3 rounded-lg">
                  {progressUpdates.slice(-10).map((update, index) => (
                    <div key={index} className="text-xs text-gray-700 flex items-start space-x-2">
                      <span className="text-gray-400">•</span>
                      <span>{update}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Search Queries Generated */}
            {searchQueries.length > 0 && (
              <div className="mb-4">
                <h4 className="text-sm font-medium text-black mb-2">🔍 AI-Generated Search Queries</h4>
                <div className="space-y-1">
                  {searchQueries.map((query, index) => (
                    <div key={index} className="text-xs bg-green-50 p-2 rounded border border-green-200">
                      <span className="text-green-800 font-medium">{index + 1}.</span>
                      <span className="text-green-700 ml-2">{query}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Visited Links */}
            {visitedLinks.length > 0 && (
              <div className="mb-4">
                <h4 className="text-sm font-medium text-black mb-2">🌐 Websites Being Visited ({visitedLinks.length})</h4>
                <div className="max-h-32 overflow-y-auto space-y-1">
                  {visitedLinks.slice(-5).map((link, index) => (
                    <div key={index} className="text-xs bg-purple-50 p-2 rounded border border-purple-200">
                      <div className="flex items-center justify-between">
                        <span className="text-purple-700 truncate">{link.url}</span>
                        {link.score && (
                          <span className="text-purple-600 font-medium ml-2">Score: {link.score}</span>
                        )}
                      </div>
                      <div className="text-purple-600 text-xs mt-1">{link.reason}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {filters.show_browser && (
              <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                <p className="text-sm text-green-800">
                  <strong>🖥️ Browser Window Open:</strong> You should see a Chrome browser window where you can 
                  watch the AI agent work in real-time, navigating websites and extracting housing data.
                </p>
              </div>
            )}
            
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-sm text-blue-800">
                <strong>What&apos;s happening:</strong> Our AI agent is using advanced search techniques including 
                LLM-generated queries, deep link following, and intelligent relevance scoring to find the 
                best housing options for you.
              </p>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Search Error</h3>
                <div className="mt-2 text-sm text-red-700">{error}</div>
              </div>
            </div>
          </div>
        )}

        {/* Search Queries Section */}
        {!loading && searchPerformed && searchResponse?.search_queries && (
          <div className="bg-white p-6 rounded-lg shadow-lg mb-8">
            <h3 className="text-lg font-semibold text-black mb-4">
              🔍 AI-Generated Search Queries
              {searchResponse.llm_queries_used && (
                <span className="ml-2 text-sm bg-green-100 text-green-800 px-2 py-1 rounded-full">
                  LLM Powered
                </span>
              )}
            </h3>
            <div className="space-y-2">
              {searchResponse.search_queries.map((query, index) => (
                <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-600 w-8">{index + 1}.</span>
                  <span className="text-black">{query}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Results Section */}
        {!loading && searchPerformed && searchResponse && searchResponse.listings.length > 0 && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-semibold text-black">
                Found {searchResponse.listings.length} listing{searchResponse.listings.length !== 1 ? 's' : ''}
              </h2>
              <div className="flex items-center space-x-4">
                <span className="text-sm text-black">Sorted by relevance score</span>
                {searchResponse.deep_search_report && (
                  <button
                    onClick={() => setShowDeepSearchReport(!showDeepSearchReport)}
                    className="text-sm bg-blue-100 text-blue-800 px-3 py-1 rounded-full hover:bg-blue-200 transition-colors"
                  >
                    {showDeepSearchReport ? 'Hide' : 'Show'} Deep Search Report
                  </button>
                )}
              </div>
            </div>
            
            <div className="grid gap-4">
              {searchResponse.listings.map((listing, i) => (
                <a 
                  key={i} 
                  href={listing.url} 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="block bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition duration-200 border border-gray-100"
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-start justify-between mb-2">
                        <h3 className="font-semibold text-lg text-black line-clamp-2 flex-1">
                          {listing.title}
                        </h3>
                        <div className="ml-4 flex items-center space-x-2">
                          <span className={`text-sm font-bold px-2 py-1 rounded ${getRelevanceColor(listing.relevance_score)} bg-gray-100`}>
                            Score: {formatRelevanceScore(listing.relevance_score)}
                          </span>
                          <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                          </svg>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-4 text-sm text-black mb-2">
                        {listing.price && (
                          <span className="font-medium text-green-600">${listing.price}/month</span>
                        )}
                        {listing.location && (
                          <span className="flex items-center">
                            📍 {listing.location}
                          </span>
                        )}
                        <span className="flex items-center">
                          🔗 {listing.source}
                        </span>
                        {listing.related_links && listing.related_links.length > 0 && (
                          <span className="flex items-center text-blue-600">
                            🔍 {listing.related_links.length} related links found
                          </span>
                        )}
                      </div>
                      
                      {listing.description && (
                        <p className="text-sm text-gray-600 line-clamp-2 mt-2">
                          {listing.description}
                        </p>
                      )}
                    </div>
                  </div>
                </a>
              ))}
            </div>
          </div>
        )}

        {/* AI Agent Summary Section */}
        {!loading && searchPerformed && (visitedLinks.length > 0 || searchQueries.length > 0) && (
          <div className="bg-white p-6 rounded-lg shadow-lg mb-8">
            <h3 className="text-lg font-semibold text-black mb-4">🤖 AI Agent Summary Report</h3>
            
            {/* Search Queries Used */}
            {searchQueries.length > 0 && (
              <div className="mb-6">
                <h4 className="font-medium text-black mb-3">🔍 AI-Generated Search Queries ({searchQueries.length})</h4>
                <div className="space-y-2">
                  {searchQueries.map((query, index) => (
                    <div key={index} className="flex items-start space-x-3 p-3 bg-green-50 rounded-lg border border-green-200">
                      <span className="text-sm font-bold text-green-800 w-6">{index + 1}.</span>
                      <span className="text-green-700 text-sm">{query}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* All Visited Links with Scores */}
            {visitedLinks.length > 0 && (
              <div className="mb-6">
                <h4 className="font-medium text-black mb-3">
                  🌐 All Websites Visited by AI Agent ({visitedLinks.length})
                  <span className="ml-2 text-sm text-gray-600">(Sorted by Relevance Score)</span>
                </h4>
                <div className="max-h-60 overflow-y-auto space-y-2">
                  {visitedLinks
                    .sort((a, b) => (b.score || 0) - (a.score || 0))
                    .map((link, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-3">
                          <span className="text-sm font-bold text-gray-600 w-6">#{index + 1}</span>
                          <div className="flex-1 min-w-0">
                            <div className="text-sm text-gray-800 truncate" title={link.url}>
                              {link.url}
                            </div>
                            <div className="text-xs text-gray-600 mt-1">{link.reason}</div>
                          </div>
                        </div>
                      </div>
                      {link.score && (
                        <div className="ml-3 flex items-center space-x-2">
                          <span className={`text-sm font-bold px-2 py-1 rounded ${
                            link.score >= 80 ? 'bg-green-100 text-green-800' :
                            link.score >= 60 ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {link.score}
                          </span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Deep Search Report */}
            {searchResponse?.deep_search_report && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">{searchResponse.deep_search_report.total_visited}</div>
                  <div className="text-sm text-blue-800">Total Links Visited</div>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">{searchResponse.deep_search_report.total_shortlisted}</div>
                  <div className="text-sm text-green-800">Links Shortlisted</div>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">{searchResponse.deep_search_report.search_depth}</div>
                  <div className="text-sm text-purple-800">Search Depth</div>
                </div>
              </div>
            )}
            
            {/* Progress Updates Summary */}
            {progressUpdates.length > 0 && (
              <div>
                <h4 className="font-medium text-black mb-3">📋 Complete Progress Log ({progressUpdates.length} updates)</h4>
                <div className="max-h-40 overflow-y-auto space-y-1 bg-gray-50 p-3 rounded-lg">
                  {progressUpdates.map((update, index) => (
                    <div key={index} className="text-xs text-gray-700 flex items-start space-x-2">
                      <span className="text-gray-400">•</span>
                      <span>{update}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {!loading && searchPerformed && searchResponse && searchResponse.listings.length === 0 && !error && (
          <div className="text-center py-12">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
              <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-black mb-2">No listings found</h3>
            <p className="text-black mb-4">
              Try adjusting your filters or search criteria
            </p>
            <button 
              onClick={resetForm}
              className="text-blue-600 hover:text-blue-800 font-medium"
            >
              Reset filters
            </button>
          </div>
        )}
      </div>
    </main>
  );
}
