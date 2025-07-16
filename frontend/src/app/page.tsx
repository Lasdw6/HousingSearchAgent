"use client";
import { useState } from "react";
import { searchListingsWithProgress, type SearchFilters, type Listing, type ProgressMessage } from "@/lib/api";

const defaultFilters = {
  gender: "Any",
  price_min: "",
  price_max: "",
  term: "",
  stay_length: "",
  location: "",
  furnished: "",
  lease_type: "",
};

export default function Home() {
  const [filters, setFilters] = useState(defaultFilters);
  const [results, setResults] = useState<Listing[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [searchPerformed, setSearchPerformed] = useState(false);
  const [progress, setProgress] = useState<ProgressMessage[]>([]);
  const [currentProgress, setCurrentProgress] = useState<ProgressMessage | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFilters({ ...filters, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResults([]);
    setSearchPerformed(true);
    setProgress([]);
    setCurrentProgress(null);
    
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
      };

      const listings = await searchListingsWithProgress(requestData, (message: ProgressMessage) => {
        setProgress(prev => [...prev, message]);
        setCurrentProgress(message);
      });
      
      setResults(listings);
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred. Please try again.");
      console.error("Search error:", err);
    } finally {
      setLoading(false);
      setCurrentProgress(null);
    }
  };

  const resetForm = () => {
    setFilters(defaultFilters);
    setResults([]);
    setError("");
    setSearchPerformed(false);
    setProgress([]);
    setCurrentProgress(null);
  };

  const getProgressColor = (type: string) => {
    switch (type) {
      case 'error':
        return 'text-red-600';
      case 'complete':
        return 'text-green-600';
      case 'source_complete':
        return 'text-blue-600';
      default:
        return 'text-gray-600';
    }
  };

  const getProgressIcon = (type: string) => {
    switch (type) {
      case 'error':
        return '❌';
      case 'complete':
        return '✅';
      case 'source_complete':
        return '✓';
      case 'searching':
        return '🔍';
      case 'processing':
        return '⚙️';
      default:
        return 'ℹ️';
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col items-center p-4">
      <div className="w-full max-w-4xl">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-black mb-2">🏠 Waterloo Student Housing Search</h1>
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

        {/* Progress Section */}
        {loading && (
          <div className="bg-white p-6 rounded-lg shadow-lg mb-8">
            <h3 className="text-lg font-semibold text-black mb-4">🤖 Intelligent Agent Progress</h3>
            
            {/* Progress Bar */}
            {currentProgress && currentProgress.progress !== undefined && (
              <div className="mb-4">
                <div className="flex justify-between text-sm text-black mb-2">
                  <span>{currentProgress.message}</span>
                  <span>{currentProgress.progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${currentProgress.progress}%` }}
                  ></div>
                </div>
              </div>
            )}
            
            {/* Progress Log */}
            <div className="max-h-64 overflow-y-auto space-y-2">
              {progress.map((msg, index) => (
                <div 
                  key={index} 
                  className={`flex items-start space-x-2 p-2 rounded ${msg.type === 'error' ? 'bg-red-50' : 'bg-gray-50'}`}
                >
                  <span className="text-sm">{getProgressIcon(msg.type)}</span>
                  <span className={`text-sm ${getProgressColor(msg.type)}`}>
                    {msg.message}
                  </span>
                </div>
              ))}
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

        {/* Results Section */}
        {!loading && searchPerformed && results.length > 0 && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-semibold text-black">
                Found {results.length} listing{results.length !== 1 ? 's' : ''}
              </h2>
              <span className="text-sm text-black">Sorted by relevance</span>
            </div>
            <div className="grid gap-4">
              {results.map((listing, i) => (
                <a 
                  key={i} 
                  href={listing.url} 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="block bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition duration-200 border border-gray-100"
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h3 className="font-semibold text-lg text-black mb-2 line-clamp-2">
                        {listing.title}
                      </h3>
                      <div className="flex items-center gap-4 text-sm text-black">
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
                      </div>
                    </div>
                    <div className="ml-4">
                      <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                      </svg>
                    </div>
                  </div>
                </a>
              ))}
            </div>
          </div>
        )}

        {!loading && searchPerformed && results.length === 0 && !error && (
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
