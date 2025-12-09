import React, { useState, useEffect, useCallback, useRef } from 'react';
import './Interface.css';

// --- Simulation Logic (Client-Side Mirror) ---
// In a production app, this would be an API call to the Python backend.
// For this interface demonstration, we implement a lightweight simulator here.

const generateReferences = (text) => {
    if (!text) return [];
    return text.split(',').map(s => {
        const parts = s.trim().split(/\s+/);
        const addr = parseInt(parts[0], 10);
        const type = parts[1] ? parts[1].toUpperCase() : 'R';
        return { address: addr, type, id: Math.random().toString(36).substr(2, 9) };
    }).filter(r => !isNaN(r.address));
};

const Interface = () => {
    // --- Configuration State ---
    const [config, setConfig] = useState({
        vmSize: 65536,
        pmSize: 4096,
        pageSize: 256,
        tlbSize: 4,
        policy: 'LRU', // FIFO, LRU
        refString: "120 R, 240 R, 4095 W, 8192 R, 9000 W, 256 R, 9000 R, 40000 R"
    });

    // --- Simulation State ---
    const [stepIndex, setStepIndex] = useState(0);
    const [references, setReferences] = useState([]);
    const [frames, setFrames] = useState([]); // Array of { pageId: int, lastAccess: int, loadTime: int }
    const [tlb, setTlb] = useState([]); // Array of { vpn: int, pfn: int, lastAccess: int, valid: bool }
    const [pageTable, setPageTable] = useState({}); // Map vpn -> { frame: int, valid: boolean }
    const [logs, setLogs] = useState([]);
    const [stats, setStats] = useState({ hits: 0, faults: 0, tlbHits: 0, tlbMisses: 0 });
    const [isRunning, setIsRunning] = useState(false);
    const [highlightBlock, setHighlightBlock] = useState(null); // { type: 'frame'|'tlb', index: int, status: 'hit'|'miss' }

    // Computed Properties
    const numPages = Math.ceil(config.vmSize / config.pageSize);
    const numFrames = Math.floor(config.pmSize / config.pageSize);
    const offsetBits = Math.log2(config.pageSize);

    const bottomScrollRef = useRef(null);

    // --- Initialization ---
    const initialize = useCallback(() => {
        setStepIndex(0);
        setReferences(generateReferences(config.refString));

        // Init Frames
        const emptyFrames = Array(numFrames).fill(null).map((_, i) => ({
            id: i, pageId: null, dirty: false, lastAccess: 0, loadTime: 0
        }));
        setFrames(emptyFrames);

        // Init TLB
        const emptyTlb = Array(config.tlbSize).fill(null).map((_, i) => ({
            id: i, vpn: null, pfn: null, valid: false, lastAccess: 0
        }));
        setTlb(emptyTlb);

        // Init Page Table (Virtual)
        const pt = {};
        for (let i = 0; i < numPages; i++) {
            pt[i] = { frame: null, valid: false, dirty: false };
        }
        setPageTable(pt);

        setStats({ hits: 0, faults: 0, tlbHits: 0, tlbMisses: 0 });
        setLogs([{ time: new Date().toLocaleTimeString(), msg: "Simulation initialized.", type: 'info' }]);
        setIsRunning(false);
        setHighlightBlock(null);
    }, [config, numFrames, numPages]);

    useEffect(() => {
        initialize();
    }, [initialize]); // Re-init when config changes drastically (handled by user click usually)

    // --- Step Logic ---
    const executeStep = () => {
        if (stepIndex >= references.length) {
            setIsRunning(false);
            return;
        }

        const currentRef = references[stepIndex];
        const vAddress = currentRef.address;
        const vpn = Math.floor(vAddress / config.pageSize);
        const offset = vAddress % config.pageSize;

        let newLogs = [];
        let newStats = { ...stats };
        let newTlb = [...tlb];
        let newFrames = [...frames];
        let newPageTable = { ...pageTable };
        let hit = false;
        let tlbHit = false;
        let fault = false;
        let highlight = null;

        // 1. Check TLB
        const tlbIndex = newTlb.findIndex(e => e.valid && e.vpn === vpn);
        let pfn = -1;

        if (tlbIndex !== -1) {
            tlbHit = true;
            pfn = newTlb[tlbIndex].pfn;
            newStats.tlbHits++;
            newLogs.push({ time: new Date().toLocaleTimeString(), msg: `Addr ${vAddress}: TLB HIT. VPN ${vpn} -> PFN ${pfn}`, type: 'success' });
            highlight = { type: 'tlb', index: tlbIndex, status: 'hit' };

            // Update TLB LRU
            if (config.policy === 'LRU') {
                newTlb[tlbIndex].lastAccess = Date.now();
            }
        } else {
            newStats.tlbMisses++;
            newLogs.push({ time: new Date().toLocaleTimeString(), msg: `Addr ${vAddress}: TLB MISS on VPN ${vpn}. Checking Page Table...`, type: 'info' });

            // 2. Check Page Table
            if (newPageTable[vpn] && newPageTable[vpn].valid) {
                hit = true;
                pfn = newPageTable[vpn].frame;
                newStats.hits++;
                newLogs.push({ time: new Date().toLocaleTimeString(), msg: `Page Table HIT. Page ${vpn} is in Frame ${pfn}`, type: 'success' });
                highlight = { type: 'frame', index: pfn, status: 'hit' };
            } else {
                // Page Fault
                fault = true;
                newStats.faults++;
                newLogs.push({ time: new Date().toLocaleTimeString(), msg: `PAGE FAULT on Page ${vpn}.`, type: 'error' });
                highlight = { type: 'frame', index: -1, status: 'fault' };

                // 3. Find Free Frame or Evict
                let victimFrameIdx = newFrames.findIndex(f => f.pageId === null);

                if (victimFrameIdx === -1) {
                    // Eviction needed
                    if (config.policy === 'FIFO') {
                        // Find minimal loadTime
                        victimFrameIdx = newFrames.reduce((minIdx, f, idx, arr) => f.loadTime < arr[minIdx].loadTime ? idx : minIdx, 0);
                    } else {
                        // LRU: Find minimal lastAccess
                        victimFrameIdx = newFrames.reduce((minIdx, f, idx, arr) => f.lastAccess < arr[minIdx].lastAccess ? idx : minIdx, 0);
                    }
                    const victimPageId = newFrames[victimFrameIdx].pageId;

                    // Invalidate victim in Page Table
                    if (victimPageId !== null && newPageTable[victimPageId]) {
                        newPageTable[victimPageId].valid = false;
                        newPageTable[victimPageId].frame = null;
                    }

                    // Invalidate victim in TLB
                    const tlbVictimIdx = newTlb.findIndex(e => e.valid && e.vpn === victimPageId);
                    if (tlbVictimIdx !== -1) {
                        newTlb[tlbVictimIdx].valid = false;
                    }

                    newLogs.push({ time: new Date().toLocaleTimeString(), msg: `Evicting Page ${victimPageId} from Frame ${victimFrameIdx}.`, type: 'info' });
                }

                pfn = victimFrameIdx;

                // Load Page
                newFrames[pfn] = {
                    id: pfn,
                    pageId: vpn,
                    dirty: currentRef.type === 'W',
                    lastAccess: Date.now(),
                    loadTime: Date.now()
                };

                newPageTable[vpn] = { ...newPageTable[vpn], valid: true, frame: pfn };

                highlight = { type: 'frame', index: pfn, status: 'fault' };
            }

            // Update TLB with new mapping (Simple FIFO replacement for TLB usually, or same policy)
            // Here we assume simple FIFO/LRU for TLB too.
            // Find empty or victim TLB
            let tlbReplaceIdx = newTlb.findIndex(e => !e.valid);
            if (tlbReplaceIdx === -1) {
                // Evict TLB entry
                tlbReplaceIdx = newTlb.reduce((minIdx, entry, idx, arr) => entry.lastAccess < arr[minIdx].lastAccess ? idx : minIdx, 0);
            }

            newTlb[tlbReplaceIdx] = {
                id: tlbReplaceIdx,
                vpn: vpn,
                pfn: pfn,
                valid: true,
                lastAccess: Date.now()
            };
        }

        // Update Frame Access Stats for LRU
        if (pfn !== -1) {
            newFrames[pfn].lastAccess = Date.now();
            if (currentRef.type === 'W') newFrames[pfn].dirty = true;
        }

        // Update State
        setTlb(newTlb);
        setFrames(newFrames);
        setPageTable(newPageTable);
        setStats(newStats);
        setLogs(prev => [...prev, ...newLogs]);
        setStepIndex(stepIndex + 1);
        setHighlightBlock(highlight);
    };

    useEffect(() => {
        if (bottomScrollRef.current) {
            bottomScrollRef.current.scrollTop = bottomScrollRef.current.scrollHeight;
        }
    }, [logs]);

    useEffect(() => {
        let interval;
        if (isRunning && stepIndex < references.length) {
            interval = setInterval(() => {
                executeStep();
            }, 800); // 800ms delay for auto-run
        } else {
            setIsRunning(false);
        }
        return () => clearInterval(interval);
    }, [isRunning, stepIndex, references]);

    // --- Handlers ---
    const handleConfigChange = (e) => {
        const { name, value } = e.target;
        setConfig(prev => ({ ...prev, [name]: value }));
    };

    const handleRestart = () => {
        initialize();
    };

    const handleStep = () => {
        executeStep();
    };

    const toggleRun = () => {
        setIsRunning(!isRunning);
    };

    // --- Rendering ---
    return (
        <div className="interface-container">
            <header className="header">
                <h1>Virtual Memory Simulator</h1>
                <p>Interactive Visualization of Page Replacement & Translation</p>
            </header>

            {/* Configuration */}
            <section className="config-panel">
                <div className="input-group">
                    <label>Virtual Memory (Bytes)</label>
                    <input type="number" name="vmSize" value={config.vmSize} onChange={handleConfigChange} />
                </div>
                <div className="input-group">
                    <label>Physical RAM (Bytes)</label>
                    <input type="number" name="pmSize" value={config.pmSize} onChange={handleConfigChange} />
                </div>
                <div className="input-group">
                    <label>Page Size (Bytes)</label>
                    <select name="pageSize" value={config.pageSize} onChange={handleConfigChange}>
                        <option value="64">64 (6 bits)</option>
                        <option value="256">256 (8 bits)</option>
                        <option value="1024">1024 (10 bits)</option>
                        <option value="4096">4096 (12 bits)</option>
                    </select>
                </div>
                <div className="input-group">
                    <label>Page Policy</label>
                    <select name="policy" value={config.policy} onChange={handleConfigChange}>
                        <option value="LRU">LRU (Least Recently Used)</option>
                        <option value="FIFO">FIFO (First In First Out)</option>
                    </select>
                </div>
                <div className="input-group" style={{ gridColumn: '1 / -1' }}>
                    <label>Reference String (Address Type, ...)</label>
                    <textarea name="refString" value={config.refString} onChange={handleConfigChange} placeholder="e.g. 120 R, 400 W" />
                </div>
            </section>

            {/* Controls */}
            <div className="controls">
                <button className="btn" onClick={handleRestart}>↺ Reset</button>
                <button className="btn" onClick={handleStep} disabled={stepIndex >= references.length || isRunning}>
                    ▶ Step Input
                </button>
                <button className="btn btn-primary" onClick={toggleRun} disabled={stepIndex >= references.length}>
                    {isRunning ? '⏸ Pause' : '▶▶ Auto Run'}
                </button>
            </div>

            <div className="viz-grid">
                {/* Main Visual: RAM & VM */}
                <div className="card">
                    <div className="card-header">
                        <span className="card-title">Physical Memory (Frames)</span>
                        <span className="card-badge">{numFrames} Frames</span>
                    </div>
                    <div className="memory-grid">
                        {frames.map((frame, i) => (
                            <div key={i} className={`memory-block 
                          ${highlightBlock?.type === 'frame' && highlightBlock.index === i ?
                                    (highlightBlock.status === 'hit' ? 'highlight' : 'fault') : ''}
                          ${frame.pageId !== null ? 'active' : ''}
                      `}>
                                <span className="block-label">Frame {i}</span>
                                <span className="block-value">
                                    {frame.pageId !== null ? `Page ${frame.pageId}` : 'Empty'}
                                </span>
                            </div>
                        ))}
                    </div>

                    <div className="stats-bar" style={{ marginTop: 'auto', paddingTop: '1rem', borderTop: '1px solid var(--bg-tertiary)' }}>
                        <div className="stat-item">
                            <span className="stat-value">{stats.hits}</span>
                            <span className="stat-label">Page Hits</span>
                        </div>
                        <div className="stat-item">
                            <span className="stat-value">{stats.faults}</span>
                            <span className="stat-label">Page Faults</span>
                        </div>
                        <div className="stat-item">
                            <span className="stat-value">{(stats.tlbHits / (stats.tlbHits + stats.tlbMisses || 1) * 100).toFixed(1)}%</span>
                            <span className="stat-label">TLB Hit Ratio</span>
                        </div>
                        <div className="stat-item">
                            <span className="stat-value">
                                {stepIndex}/{references.length}
                            </span>
                            <span className="stat-label">Progress</span>
                        </div>
                    </div>
                </div>

                {/* TLB & Page Table */}
                <div className="card">
                    <div className="card-header">
                        <span className="card-title">TLB</span>
                        <span className="card-badge">{config.tlbSize} Entries</span>
                    </div>
                    <div className="memory-grid" style={{ gridTemplateColumns: '1fr' }}>
                        {tlb.map((entry, i) => (
                            <div key={i} className={`memory-block 
                         ${highlightBlock?.type === 'tlb' && highlightBlock.index === i ?
                                    (highlightBlock.status === 'hit' ? 'highlight' : '') : ''} 
                         ${entry.valid ? 'active' : ''}
                      `} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.75rem' }}>
                                <span>Entry {i}</span>
                                <span style={{ fontFamily: 'monospace' }}>
                                    {entry.valid ? `VPN:${entry.vpn} → PFN:${entry.pfn}` : 'Invalid'}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Logs */}
                <div className="card">
                    <div className="card-header">
                        <span className="card-title">Simulation Log</span>
                    </div>
                    <div className="log-container" ref={bottomScrollRef}>
                        {logs.length === 0 && <span style={{ opacity: 0.5 }}>Ready to start...</span>}
                        {logs.map((log, i) => (
                            <div key={i} className="log-entry">
                                <span className="log-time">[{log.time.split(' ')[0]}]</span>
                                <span className={`log-msg log-${log.type}`}>{log.msg}</span>
                            </div>
                        ))}
                    </div>
                    <div className="card-header" style={{ marginTop: '10px' }}>
                        <span className="card-title" style={{ fontSize: '1rem' }}>Next Reference</span>
                    </div>
                    <div style={{ background: 'var(--bg-tertiary)', padding: '1rem', borderRadius: '0.5rem', textAlign: 'center' }}>
                        {stepIndex < references.length ? (
                            <>
                                <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--accent-color)' }}>
                                    {references[stepIndex].address} <span style={{ fontSize: '1rem' }}>({references[stepIndex].type})</span>
                                </div>
                                <div style={{ fontSize: '0.8rem', opacity: 0.7, marginTop: '0.25rem' }}>
                                    VPN: {Math.floor(references[stepIndex].address / config.pageSize)} | Offset: {references[stepIndex].address % config.pageSize}
                                </div>
                            </>
                        ) : (
                            <span style={{ color: 'var(--success-color)' }}>Simulation Complete</span>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Interface;
