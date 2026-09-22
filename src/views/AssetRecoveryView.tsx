import React from 'react';
import { motion } from 'framer-motion';
import { SoftCard } from '@/components/ui/SoftCard';
import { mockAssets } from '@/lib/mockData';
import { Box, Battery, Thermometer, Wifi, MapPin, RefreshCw, CheckCircle2, AlertOctagon } from 'lucide-react';
import { pageFadeVariants, listContainerVariants, listItemVariants } from '@/lib/motion-config';

export const AssetRecoveryView: React.FC = () => {
  return (
    <motion.div
      variants={pageFadeVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      className="flex flex-col gap-6 max-w-7xl mx-auto pb-20"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex flex-col">
          <span className="text-xs font-bold text-blue-600 dark:text-blue-400">
            IoT & Physical Asset Telemetry
          </span>
          <h1 className="text-2xl font-extrabold tracking-tight text-slate-900 dark:text-white mt-1">
            Physical Hardware Monitoring & Recovery Grid
          </h1>
        </div>

        <button className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-900 dark:bg-slate-100 dark:text-slate-900 text-white font-bold text-xs shadow-md transition-all">
          <RefreshCw className="w-4 h-4" />
          <span>Ping All IoT Sensors</span>
        </button>
      </div>

      {/* Grid of Monitored Assets */}
      <div className="flex flex-col gap-4">
        <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
          Monitored Hardware Devices ({mockAssets.length})
        </span>

        <motion.div variants={listContainerVariants} initial="hidden" animate="show" className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {mockAssets.map((asset) => {
            const isDormant = asset.status.includes('Dormant');

            return (
              <motion.div key={asset.id} variants={listItemVariants}>
                <SoftCard className={`flex flex-col justify-between h-full gap-4 ${isDormant ? 'border-2 border-emerald-400 dark:border-emerald-700 bg-emerald-50/20' : ''}`}>
                  <div className="flex flex-col gap-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-mono font-bold text-slate-400">
                        {asset.assetTag}
                      </span>
                      {isDormant ? (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 animate-pulse">
                          Reallocatable
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300">
                          Active
                        </span>
                      )}
                    </div>

                    <h3 className="text-base font-extrabold text-slate-900 dark:text-white">
                      {asset.name}
                    </h3>

                    <div className="flex items-center gap-1.5 text-xs text-slate-400">
                      <MapPin className="w-3.5 h-3.5 text-indigo-500" />
                      <span>{asset.location}</span>
                    </div>
                  </div>

                  {/* Telemetry Gauge Indicators */}
                  <div className="grid grid-cols-3 gap-2 p-3 rounded-2xl bg-white/50 dark:bg-slate-800/50 border border-slate-200/50 dark:border-slate-700/50 text-center">
                    <div className="flex flex-col items-center">
                      <div className="flex items-center gap-1 text-slate-400 text-[10px] font-bold">
                        <Battery className="w-3 h-3 text-emerald-500" />
                        <span>Battery</span>
                      </div>
                      <span className="text-xs font-extrabold text-slate-800 dark:text-slate-100 mt-0.5">
                        {asset.telemetry.batteryPct}%
                      </span>
                    </div>

                    <div className="flex flex-col items-center border-x border-slate-200/50 dark:border-slate-700/50 px-1">
                      <div className="flex items-center gap-1 text-slate-400 text-[10px] font-bold">
                        <Thermometer className="w-3 h-3 text-amber-500" />
                        <span>Temp</span>
                      </div>
                      <span className="text-xs font-extrabold text-slate-800 dark:text-slate-100 mt-0.5">
                        {asset.telemetry.tempCelsius}°C
                      </span>
                    </div>

                    <div className="flex flex-col items-center">
                      <div className="flex items-center gap-1 text-slate-400 text-[10px] font-bold">
                        <Wifi className="w-3 h-3 text-indigo-500" />
                        <span>Ping</span>
                      </div>
                      <span className="text-[10px] font-bold text-slate-800 dark:text-slate-100 mt-0.5 truncate max-w-[60px]">
                        {asset.telemetry.lastPing}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-2 border-t border-slate-200/50 dark:border-slate-800 text-xs">
                    <span className="text-slate-500 truncate max-w-[150px]">
                      {asset.assignedUser}
                    </span>
                    <button className="px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs transition-all shadow-sm">
                      {isDormant ? 'Assign Asset' : 'Details'}
                    </button>
                  </div>
                </SoftCard>
              </motion.div>
            );
          })}
        </motion.div>
      </div>
    </motion.div>
  );
};
