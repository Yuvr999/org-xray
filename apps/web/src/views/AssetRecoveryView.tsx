import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { SoftCard } from '@/components/ui/SoftCard';
import { useApp } from '@/context/AppContext';
import { laptopHardwareDataset, LaptopDatasetItem } from '@/lib/mockData';
import { 
  Box, 
  Battery, 
  Thermometer, 
  Wifi, 
  MapPin, 
  RefreshCw, 
  CheckCircle2, 
  Cpu, 
  HardDrive, 
  Activity, 
  Zap, 
  Sparkles, 
  ShieldCheck, 
  Laptop, 
  Monitor, 
  Radio,
  Search,
  SlidersHorizontal,
  ArrowUpDown,
  Table
} from 'lucide-react';
import { pageFadeVariants, listContainerVariants, listItemVariants } from '@/lib/motion-config';

export const AssetRecoveryView: React.FC = () => {
  const { assets } = useApp();
  const [viewMode, setViewMode] = useState<'telemetry' | 'dataset'>('telemetry');
  const [selectedAssetId, setSelectedAssetId] = useState<string>(assets[0]?.id || '');
  const [expandedCards, setExpandedCards] = useState<Record<string, boolean>>({
    [assets[0]?.id || '1']: true,
  });
  const [isPinging, setIsPinging] = useState(false);
  const [pingMessage, setPingMessage] = useState<string | null>(null);
  
  // Dataset table search & sort
  const [datasetSearch, setDatasetSearch] = useState('');
  const [selectedBrand, setSelectedBrand] = useState<string>('All');
  const [sortBy, setSortBy] = useState<'price-asc' | 'price-desc' | 'score-desc'>('score-desc');

  const selectedAsset = assets.find((a) => a.id === selectedAssetId) || assets[0] || null;

  const toggleCard = (id: string) => {
    setSelectedAssetId(id);
    setExpandedCards((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  const handlePingAll = () => {
    setIsPinging(true);
    setPingMessage('📡 Pinging all IoT sensors across Building A, B, and Server Closets...');
    setTimeout(() => {
      setIsPinging(false);
      setPingMessage('✅ All IoT asset beacons responded with 100% signal integrity.');
      setTimeout(() => setPingMessage(null), 4000);
    }, 1200);
  };

  const getAssetIcon = (name: string) => {
    if (name.toLowerCase().includes('macbook') || name.toLowerCase().includes('laptop') || name.toLowerCase().includes('asus') || name.toLowerCase().includes('hp') || name.toLowerCase().includes('lenovo') || name.toLowerCase().includes('acer')) {
      return Laptop;
    }
    if (name.toLowerCase().includes('monitor') || name.toLowerCase().includes('display')) {
      return Monitor;
    }
    return Radio;
  };

  // Filtered dataset
  const filteredDataset = laptopHardwareDataset
    .filter((item) => {
      const matchesSearch =
        item.model.toLowerCase().includes(datasetSearch.toLowerCase()) ||
        item.brand.toLowerCase().includes(datasetSearch.toLowerCase()) ||
        item.processor.toLowerCase().includes(datasetSearch.toLowerCase());
      const matchesBrand = selectedBrand === 'All' || item.brand.toLowerCase() === selectedBrand.toLowerCase();
      return matchesSearch && matchesBrand;
    })
    .sort((a, b) => {
      if (sortBy === 'price-asc') return a.priceInr - b.priceInr;
      if (sortBy === 'price-desc') return b.priceInr - a.priceInr;
      return b.benchmarkScore - a.benchmarkScore;
    });

  return (
    <motion.div
      variants={pageFadeVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      className="flex flex-col gap-8 max-w-7xl mx-auto pb-24 text-slate-100"
    >
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex flex-col">
          <span className="text-sm font-black text-white flex items-center gap-1.5 uppercase tracking-wider">
            <Sparkles className="w-4 h-4 text-white" />
            IoT & Physical Asset Telemetry
          </span>
          <h1 className="text-3xl sm:text-4xl font-black tracking-tight text-white mt-1">
            Physical Hardware Monitoring & Dataset Matrix
          </h1>
          <p className="text-sm text-blue-100 mt-1 font-medium">
            Click any hardware box to inspect live telemetry, or switch to the Master Dataset Matrix for full specifications.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Mode Switcher */}
          <div className="p-1.5 rounded-2xl bg-white border border-slate-200 shadow-md flex items-center gap-1.5">
            <button
              onClick={() => setViewMode('telemetry')}
              className={`px-4 py-2 rounded-xl text-sm font-extrabold transition-all cursor-pointer ${
                viewMode === 'telemetry'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-700 hover:text-blue-600'
              }`}
            >
              Live Telemetry Grid
            </button>
            <button
              onClick={() => setViewMode('dataset')}
              className={`px-4 py-2 rounded-xl text-sm font-extrabold transition-all cursor-pointer flex items-center gap-1.5 ${
                viewMode === 'dataset'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-700 hover:text-blue-600'
              }`}
            >
              <Table className="w-4 h-4" />
              <span>Dataset Matrix ({laptopHardwareDataset.length})</span>
            </button>
          </div>

          <button
            onClick={handlePingAll}
            disabled={isPinging}
            className="flex items-center gap-2 px-5 py-2.5 rounded-2xl bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-extrabold text-sm shadow-lg shadow-blue-600/25 transition-all cursor-pointer"
          >
            <RefreshCw className={`w-4 h-4 ${isPinging ? 'animate-spin' : ''}`} />
            <span>{isPinging ? 'Pinging...' : 'Ping All IoT'}</span>
          </button>
        </div>
      </div>

      {/* Ping Feedback Notice */}
      <AnimatePresence>
        {pingMessage && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="p-4 rounded-2xl bg-white text-slate-900 text-sm font-bold border border-slate-200 shadow-xl flex items-center gap-3"
          >
            <Activity className="w-5 h-5 text-blue-600 animate-pulse" />
            <span>{pingMessage}</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ========================================================================= */}
      {/* VIEW MODE 1: MASTER DATASET MATRIX (Exact Specifications from Image) */}
      {/* ========================================================================= */}
      {viewMode === 'dataset' && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col gap-4"
        >
          {/* Filter and Search Bar */}
          <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-lg flex flex-col sm:flex-row items-center justify-between gap-3">
            <div className="flex items-center gap-3 w-full sm:w-auto">
              <div className="relative flex-1 sm:w-72">
                <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  value={datasetSearch}
                  onChange={(e) => setDatasetSearch(e.target.value)}
                  placeholder="Search model, processor, brand..."
                  className="w-full pl-10 pr-3.5 py-2 rounded-xl bg-slate-50 border border-slate-200 text-sm font-medium text-slate-900 placeholder:text-slate-400 focus:outline-hidden focus:border-blue-500"
                />
              </div>

              {/* Brand Filter */}
              <div className="flex items-center gap-1.5">
                {['All', 'HP', 'Acer', 'Lenovo', 'Apple', 'Asus'].map((b) => (
                  <button
                    key={b}
                    onClick={() => setSelectedBrand(b)}
                    className={`px-3 py-1.5 rounded-xl text-xs font-black transition-all cursor-pointer ${
                      selectedBrand === b
                        ? 'bg-blue-600 text-white'
                        : 'bg-slate-100 text-slate-700 hover:text-slate-900 border border-slate-200'
                    }`}
                  >
                    {b}
                  </button>
                ))}
              </div>
            </div>

            {/* Sort Selector */}
            <div className="flex items-center gap-2 self-end sm:self-auto text-sm text-slate-700 font-bold">
              <ArrowUpDown className="w-4 h-4 text-blue-600" />
              <span>Sort:</span>
              <select
                value={sortBy}
                onChange={(e: any) => setSortBy(e.target.value)}
                className="bg-slate-50 border border-slate-200 text-slate-900 text-xs font-bold rounded-xl px-3 py-1.5 focus:outline-hidden"
              >
                <option value="score-desc">Highest Benchmark Score</option>
                <option value="price-asc">Lowest Price (₹)</option>
                <option value="price-desc">Highest Price (₹)</option>
              </select>
            </div>
          </div>

          {/* Master Dataset Table */}
          <div className="rounded-3xl border border-slate-200 bg-white overflow-hidden shadow-2xl">
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="bg-slate-50 text-slate-600 font-black uppercase tracking-wider border-b border-slate-200 text-xs">
                  <tr>
                    <th className="p-4">Brand</th>
                    <th className="p-4">Model Name</th>
                    <th className="p-4">Price (₹)</th>
                    <th className="p-4">Benchmark Score</th>
                    <th className="p-4">Processor / CPU</th>
                    <th className="p-4">Cores & Threads</th>
                    <th className="p-4">RAM</th>
                    <th className="p-4">RAM Type</th>
                    <th className="p-4">Storage</th>
                    <th className="p-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-slate-800">
                  {filteredDataset.map((item) => (
                    <tr key={item.id} className="hover:bg-blue-50/60 transition-colors group">
                      <td className="p-4 font-bold text-slate-900">
                        <span className="px-2.5 py-1 rounded-lg bg-blue-50 text-blue-700 border border-blue-200 font-mono font-black text-xs">
                          {item.brand}
                        </span>
                      </td>
                      <td className="p-4 font-black text-slate-900 group-hover:text-blue-600 transition-colors max-w-[240px]">
                        {item.model}
                      </td>
                      <td className="p-4 font-black text-blue-600 text-base">
                        ₹{item.priceInr.toLocaleString()}
                      </td>
                      <td className="p-4">
                        <span className="px-3 py-1 rounded-full bg-blue-100 text-blue-800 font-mono font-black text-xs border border-blue-200">
                          {item.benchmarkScore.toFixed(2)}
                        </span>
                      </td>
                      <td className="p-4 text-slate-800 font-semibold">
                        {item.processor}
                      </td>
                      <td className="p-4 text-slate-600 font-medium">
                        {item.cores}
                      </td>
                      <td className="p-4 font-extrabold text-slate-900">
                        {item.ram}
                      </td>
                      <td className="p-4 text-slate-600 font-mono font-semibold">
                        {item.ramType}
                      </td>
                      <td className="p-4 font-bold text-slate-800">
                        {item.storage}
                      </td>
                      <td className="p-4 text-right">
                        <button
                          onClick={() => {
                            setViewMode('telemetry');
                            setSelectedAssetId(assets[0]?.id || '');
                          }}
                          className="px-3.5 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-black text-xs shadow-sm transition-all cursor-pointer"
                        >
                          View In Telemetry
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </motion.div>
      )}

      {/* ========================================================================= */}
      {/* VIEW MODE 2: REAL-TIME TELEMETRY & RECOVERY GRID */}
      {/* ========================================================================= */}
      {viewMode === 'telemetry' && (
        <>
          {assets.length === 0 ? (
            <div className="p-12 rounded-3xl bg-white border border-slate-200 text-center flex flex-col items-center justify-center gap-4 shadow-xl">
              <div className="w-14 h-14 rounded-2xl bg-blue-100 border border-blue-200 flex items-center justify-center text-blue-600">
                <Box className="w-7 h-7" />
              </div>
              <div>
                <h3 className="text-lg font-black text-slate-900">No Monitored Hardware Assets</h3>
                <p className="text-sm text-slate-500 max-w-md mx-auto mt-1 leading-relaxed">
                  Register a new hardware workstation or IoT asset beacon to monitor battery and telemetry.
                </p>
              </div>
            </div>
          ) : (
            <>
              {/* SECTION 1: Minimal Brand-Style Hardware Box Selector */}
              <div className="flex flex-col gap-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-black uppercase tracking-wider text-slate-500">
                    Hardware Asset Selector (Click a box to reveal information)
                  </span>
                  <span className="text-sm text-blue-600 font-extrabold">
                    {assets.length} Monitored Devices
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {assets.map((asset) => {
                    const isSelected = selectedAssetId === asset.id;
                    const Icon = getAssetIcon(asset.name);
                    const isDormant = asset.status.includes('Dormant');

                    return (
                      <button
                        key={asset.id}
                        onClick={() => {
                          setSelectedAssetId(asset.id);
                          setExpandedCards((prev) => ({ ...prev, [asset.id]: true }));
                        }}
                        className={`group relative p-5 rounded-2xl text-left transition-all duration-300 flex flex-col justify-between h-34 cursor-pointer border ${
                          isSelected
                            ? 'bg-blue-600 text-white border-blue-500 shadow-xl shadow-blue-600/25 ring-2 ring-blue-400/40'
                            : 'bg-white hover:bg-blue-50/60 text-slate-900 border-slate-200 shadow-md'
                        }`}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex flex-col">
                            <span
                              className={`text-base font-black tracking-tight truncate max-w-[200px] transition-colors ${
                                isSelected ? 'text-white' : 'text-slate-900 group-hover:text-blue-600'
                              }`}
                            >
                              {asset.name}
                            </span>
                            <span
                              className={`text-xs font-bold mt-1 tracking-wide ${
                                isSelected ? 'text-blue-100' : 'text-slate-500'
                              }`}
                            >
                              Sign-off & Telemetry
                            </span>
                          </div>

                          <div
                            className={`p-2.5 rounded-xl transition-colors ${
                              isSelected
                                ? 'bg-white/20 text-white'
                                : 'bg-blue-50 text-blue-600 border border-blue-200'
                            }`}
                          >
                            <Icon className="w-5 h-5" />
                          </div>
                        </div>

                        <div className="flex items-center justify-between text-xs pt-2.5 border-t border-slate-100">
                          <span
                            className={`font-mono font-bold text-xs ${
                              isSelected ? 'text-blue-100' : 'text-slate-500'
                            }`}
                          >
                            {asset.assetTag}
                          </span>

                          <span
                            className={`px-2.5 py-0.5 rounded-full text-xs font-black ${
                              isDormant
                                ? isSelected
                                  ? 'bg-white text-blue-900'
                                  : 'bg-amber-100 text-amber-900 border border-amber-200'
                                : isSelected
                                ? 'bg-white text-blue-900'
                                : 'bg-emerald-100 text-emerald-900 border border-emerald-200'
                            }`}
                          >
                            {isDormant ? 'Reallocatable' : 'Active'}
                          </span>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* SECTION 2: Expanded Hardware Detail Panel */}
              <AnimatePresence mode="wait">
                {selectedAsset && (
                  <motion.div
                    key={selectedAsset.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.25 }}
                    className="w-full"
                  >
                    <div className="rounded-3xl p-6 sm:p-8 bg-white border border-slate-200 shadow-2xl relative overflow-hidden text-slate-900">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-6">
                        <div className="flex flex-col">
                          <div className="flex items-center gap-2">
                            <span className="px-3 py-1 rounded-full text-xs font-mono font-black bg-blue-100 text-blue-800 border border-blue-200">
                              {selectedAsset.assetTag}
                            </span>
                            <span className="text-xs text-blue-600 font-bold flex items-center gap-1.5">
                              <span className="w-2.5 h-2.5 rounded-full bg-blue-600 animate-pulse" />
                              Hardware Beacon Active
                            </span>
                          </div>

                          <h2 className="text-3xl sm:text-4xl font-black text-slate-900 mt-1">
                            {selectedAsset.name}
                          </h2>

                          <div className="flex flex-wrap items-center gap-4 text-sm text-slate-600 mt-1 font-medium">
                            <span className="flex items-center gap-1.5">
                              <MapPin className="w-4 h-4 text-blue-600" />
                              {selectedAsset.location}
                            </span>
                            <span>•</span>
                            <span>Assignee: <strong className="text-slate-900">{selectedAsset.assignedUser}</strong></span>
                            {selectedAsset.priceInr && (
                              <>
                                <span>•</span>
                                <span>Cost: <strong className="text-blue-600 font-black">₹{selectedAsset.priceInr.toLocaleString()}</strong></span>
                              </>
                            )}
                            {selectedAsset.benchmarkScore && (
                              <>
                                <span>•</span>
                                <span>Benchmark: <strong className="text-blue-600 font-mono font-black">{selectedAsset.benchmarkScore}</strong></span>
                              </>
                            )}
                          </div>
                        </div>

                        <span
                          className={`self-start sm:self-auto px-3.5 py-1.5 rounded-xl text-xs font-bold ${
                            selectedAsset.status.includes('Dormant')
                              ? 'bg-blue-950 text-sky-300 border border-blue-800'
                              : 'bg-blue-900 text-white'
                          }`}
                        >
                          {selectedAsset.status}
                        </span>
                      </div>

                      {/* Real-time Hardware Telemetry Grid */}
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 my-6">
                        <div className="p-4 rounded-2xl bg-blue-950/40 border border-blue-900/60 flex flex-col justify-between gap-2">
                          <div className="flex items-center justify-between text-slate-400 text-xs font-bold">
                            <span className="flex items-center gap-1.5">
                              <Battery className="w-4 h-4 text-sky-400" />
                              <span>Battery Health</span>
                            </span>
                            <span className="text-[10px] text-sky-400 font-mono">IoT Telemetry</span>
                          </div>
                          <div className="flex items-baseline gap-2 mt-1">
                            <span className="text-3xl font-extrabold text-white">
                              {selectedAsset.telemetry.batteryPct}%
                            </span>
                            <span className="text-xs text-slate-400 font-semibold">Lithium Polymer</span>
                          </div>
                          <div className="w-full h-2 rounded-full bg-blue-950 border border-blue-800/80 overflow-hidden mt-1">
                            <div
                              className="h-full bg-gradient-to-r from-blue-500 to-sky-400 rounded-full"
                              style={{ width: `${selectedAsset.telemetry.batteryPct}%` }}
                            />
                          </div>
                        </div>

                        <div className="p-4 rounded-2xl bg-blue-950/40 border border-blue-900/60 flex flex-col justify-between gap-2">
                          <div className="flex items-center justify-between text-slate-400 text-xs font-bold">
                            <span className="flex items-center gap-1.5">
                              <Thermometer className="w-4 h-4 text-sky-400" />
                              <span>Die Temperature</span>
                            </span>
                            <span className="text-[10px] text-sky-400 font-mono">Thermal Probe</span>
                          </div>
                          <div className="flex items-baseline gap-2 mt-1">
                            <span className="text-3xl font-extrabold text-white">
                              {selectedAsset.telemetry.tempCelsius}°C
                            </span>
                            <span className="text-xs text-sky-300 font-semibold">Normal Thermal Band</span>
                          </div>
                          <div className="w-full h-2 rounded-full bg-blue-950 border border-blue-800/80 overflow-hidden mt-1">
                            <div
                              className="h-full bg-gradient-to-r from-blue-600 to-blue-400 rounded-full"
                              style={{ width: `${Math.min(100, (selectedAsset.telemetry.tempCelsius / 80) * 100)}%` }}
                            />
                          </div>
                        </div>

                        <div className="p-4 rounded-2xl bg-blue-950/40 border border-blue-900/60 flex flex-col justify-between gap-2">
                          <div className="flex items-center justify-between text-slate-400 text-xs font-bold">
                            <span className="flex items-center gap-1.5">
                              <Wifi className="w-4 h-4 text-sky-400" />
                              <span>Telemetry Ping</span>
                            </span>
                            <span className="text-[10px] text-sky-400 font-mono">Mesh Protocol</span>
                          </div>
                          <div className="flex items-baseline gap-2 mt-1">
                            <span className="text-2xl font-extrabold text-white">
                              {selectedAsset.telemetry.lastPing}
                            </span>
                          </div>
                          <div className="flex items-center gap-1 text-[11px] text-sky-300 font-medium">
                            <span className="w-2 h-2 rounded-full bg-sky-400 animate-ping" />
                            <span>{selectedAsset.telemetry.signalStrength}</span>
                          </div>
                        </div>
                      </div>

                      {/* Bottom Action Controls */}
                      <div className="flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-blue-900/60">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="px-3 py-1.5 rounded-xl text-xs font-extrabold bg-slate-900/90 text-sky-300 border border-blue-800/60 uppercase">
                            HARDWARE ASSET
                          </span>
                          <span className="px-3 py-1.5 rounded-xl text-xs font-extrabold bg-slate-900/90 text-sky-300 border border-blue-800/60 uppercase">
                            {selectedAsset.location.split('-')[0].trim()}
                          </span>
                          <span className="px-3 py-1.5 rounded-xl text-xs font-extrabold bg-slate-900/90 text-sky-300 border border-blue-800/60 uppercase">
                            ORG-XRAY IOT
                          </span>
                        </div>

                        <div className="flex items-center gap-3">
                          <button
                            onClick={() => setViewMode('dataset')}
                            className="px-4 py-2 rounded-xl bg-blue-950 hover:bg-blue-900 text-sky-200 border border-blue-800 text-xs font-bold transition-all cursor-pointer"
                          >
                            Full Specs Matrix
                          </button>
                          <button className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-lg shadow-blue-600/30 transition-all hover:scale-105 active:scale-95 cursor-pointer">
                            {selectedAsset.status.includes('Dormant') ? 'Assign & Reallocate' : 'Manage Device'}
                          </button>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </>
          )}
        </>
      )}
    </motion.div>
  );
};
