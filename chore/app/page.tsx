"use client";
import { useEffect, useState } from "react";

type Chore = { id:string; title:string; items:string[]; steps:string[]; time_min:number };

export default function Home() {
  const [q, setQ] = useState("");
  const [chores, setChores] = useState<Chore[]>([]);
  const [sel, setSel] = useState<Chore | null>(null);
  const [loadingChores, setLoadingChores] = useState(false);

  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [loadingSpeak, setLoadingSpeak] = useState(false);
  const [congratsPlaying, setCongratsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [advice, setAdvice] = useState<string | null>(null);
  const [loadingAdvice, setLoadingAdvice] = useState(false);
  const [showAdvice, setShowAdvice] = useState(false);

  // Default voice ID 
  const defaultVoiceId = "21m00Tcm4TlvDq8ikWAM"; 

  // Load chores from FastAPI
  useEffect(() => {
    const fetchChores = async () => {
      if (!q.trim()) {
        setChores([]);
        setLoadingChores(false);
        return;
      }
      
      setLoadingChores(true);
      try {
        const url = `${process.env.NEXT_PUBLIC_API_BASE}/chores?q=${encodeURIComponent(q)}`;
        const response = await fetch(url);
        const data = await response.json();
        setChores(data.chores || []);
      } catch (error) {
        console.error('Error fetching chores:', error);
        setChores([]);
      } finally {
        setLoadingChores(false);
      }
    };

    // Add a small delay to avoid too many requests while typing
    const timeoutId = setTimeout(fetchChores, 300);
    return () => clearTimeout(timeoutId);
  }, [q]);

  // Checklist state for selected chore
  const [checked, setChecked] = useState<boolean[]>([]);
  useEffect(() => { 
    setChecked(sel?.steps?.map(() => false) || []); 
    setAdvice(null);
    setShowAdvice(false);
  }, [sel]);

  // Auto-speak chore when selected
  useEffect(() => {
    if (sel) {
      speakChore();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sel]);

  async function speakChore() {
    if (!sel || isMuted) return;
    setLoadingSpeak(true); setAudioUrl(null);

    // call Next.js proxy so INTERNAL_API_KEY is not exposed
    const r = await fetch("/api/tts-proxy", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ chore_id: sel.id, voice_id: defaultVoiceId })
    });
    if (!r.ok) { alert("TTS failed"); setLoadingSpeak(false); return; }

    const ct = r.headers.get("content-type") || "";
    if (ct.includes("application/json")) {
      const data = await r.json();   // { audio_url }
      setAudioUrl(data.audio_url);
    } else {
      const buf = await r.arrayBuffer();
      const blob = new Blob([buf], { type: "audio/mpeg" });
      setAudioUrl(URL.createObjectURL(blob));
    }
    setLoadingSpeak(false);
  }

  async function speakCongrats() {
    if (isMuted) return;
    console.log('Playing congrats message!'); // Debug log
    setLoadingSpeak(true); setAudioUrl(null); setCongratsPlaying(true);
    const r = await fetch("/api/tts-proxy", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: "Nice work! You finished the chore. Take a breath, hydrate, and enjoy your accomplishment!",
        voice_id: defaultVoiceId
      })
    });
    if (!r.ok) { 
      alert("TTS failed"); 
      setLoadingSpeak(false); 
      setCongratsPlaying(false);
      return; 
    }

    const ct = r.headers.get("content-type") || "";
    if (ct.includes("application/json")) {
      const data = await r.json();
      setAudioUrl(data.audio_url);
    } else {
      const buf = await r.arrayBuffer();
      const blob = new Blob([buf], { type: "audio/mpeg" });
      setAudioUrl(URL.createObjectURL(blob));
    }
    setLoadingSpeak(false);
    setCongratsPlaying(false);
  }

  async function getAdvice() {
    if (!sel || loadingAdvice) return;
    setLoadingAdvice(true);
    
    try {
      const response = await fetch("/api/advice-proxy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          chore_id: sel.id,
          user_context: "" // Could be extended to include user preferences
        })
      });
      
      if (!response.ok) {
        throw new Error("Failed to get advice");
      }
      
      const data = await response.json();
      setAdvice(data.advice);
      setShowAdvice(true);
    } catch (error) {
      console.error("Error getting advice:", error);
      setAdvice("Sorry, I couldn't generate advice right now. Try breaking the task into smaller steps and remember that done is better than perfect!");
      setShowAdvice(true);
    } finally {
      setLoadingAdvice(false);
    }
  }

  // when all steps checked → auto congrats
  useEffect(() => {
    if (!sel || !checked.length) return;
    const all = checked.every(Boolean);
    console.log('Checked status:', checked, 'All done?', all); // Debug log
    if (all) {
      console.log('All steps completed! Playing congrats...'); // Debug log
      speakCongrats();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [checked.join("|")]); // watch changes compactly

  return (
    <div className="min-h-screen bg-black text-cyan-400 flex flex-col" style={{
      backgroundImage: `
        radial-gradient(circle at 25% 25%, #1a0033 0%, transparent 50%),
        radial-gradient(circle at 75% 75%, #001a33 0%, transparent 50%),
        linear-gradient(135deg, #000000 0%, #0a0a0a 100%)
      `
    }}>
      <main className="flex-1">
        <div className="p-6 max-w-4xl mx-auto">
        <div className="text-center mb-12 border-4 border-cyan-400 bg-black bg-opacity-80 p-8 rounded-none shadow-lg shadow-cyan-400/20" style={{
          boxShadow: '0 0 20px rgba(34, 211, 238, 0.3), inset 0 0 20px rgba(34, 211, 238, 0.1)'
        }}>
          <h1 className="text-5xl font-bold text-cyan-400 mb-4 tracking-widest" style={{
            textShadow: '0 0 10px rgba(34, 211, 238, 0.8), 0 0 20px rgba(34, 211, 238, 0.5), 0 0 30px rgba(34, 211, 238, 0.3)',
            fontFamily: 'monospace'
          }}>
            CHORE LOG 
          </h1>
          <p className="text-green-400 text-lg tracking-wide" style={{
            textShadow: '0 0 5px rgba(34, 197, 94, 0.5)',
            fontFamily: 'monospace'
          }}>
            &gt; Complete daily missions with audio guidance_
          </p>
        </div>

        {!sel && (
          <div className="max-w-xl mx-auto">
            <div className="relative">
              <input
                value={q}
                onChange={e => setQ(e.target.value)}
                placeholder="SEARCH MISSIONS... [TYPE HERE]"
                className="w-full p-4 text-lg bg-black border-2 border-magenta-500 text-cyan-400 placeholder-magenta-400 focus:outline-none focus:border-cyan-400 focus:shadow-lg focus:shadow-cyan-400/30 rounded-none font-mono tracking-wide"
                style={{
                  boxShadow: 'inset 0 0 10px rgba(139, 69, 19, 0.3)',
                  textShadow: '0 0 5px rgba(34, 211, 238, 0.5)'
                }}
              />
              <div className="absolute right-4 top-1/2 transform -translate-y-1/2 text-magenta-400 text-xl">
                ◆
              </div>
            </div>
            {q && (
              <div className="mt-6 space-y-3">
                {loadingChores ? (
                  <div className="bg-black border-2 border-cyan-400 p-6 rounded-none animate-pulse" style={{
                    boxShadow: '0 0 15px rgba(34, 211, 238, 0.4)'
                  }}>
                    <div className="flex items-center gap-3 font-mono tracking-wide">
                      <div className="animate-spin text-xl text-cyan-400">◆</div>
                      <div className="text-cyan-400">
                        SCANNING MISSION DATABASE...
                      </div>
                    </div>
                    <div className="mt-3 space-y-2">
                      <div className="h-4 bg-gray-700 rounded animate-pulse"></div>
                      <div className="h-4 bg-gray-700 rounded animate-pulse w-3/4"></div>
                      <div className="h-4 bg-gray-700 rounded animate-pulse w-1/2"></div>
                    </div>
                  </div>
                ) : chores.length > 0 ? (
                  chores.map(c => (
                    <div key={c.id} className="bg-black border-2 border-yellow-400 hover:border-cyan-400 transition-all duration-200 rounded-none" style={{
                      boxShadow: '0 0 10px rgba(251, 191, 36, 0.3)'
                    }}>
                      <button 
                        className="w-full p-4 text-left hover:bg-gray-900 hover:bg-opacity-50 transition-all duration-200 font-mono"
                        onClick={() => setSel(c)}
                        style={{
                          textShadow: '0 0 5px rgba(34, 211, 238, 0.5)'
                        }}
                      >
                        <div className="flex justify-between items-center">
                          <div>
                            <h3 className="text-lg font-bold text-yellow-400 tracking-wide">▶ {c.title.toUpperCase()}</h3>
                            <p className="text-green-400 text-sm mt-1 tracking-wide">DURATION: ~{c.time_min} MIN</p>
                          </div>
                          <div className="text-cyan-400 text-xl animate-pulse">►</div>
                        </div>
                      </button>
                    </div>
                  ))
                ) : q.trim() && (
                  <div className="bg-black border-2 border-red-500 p-6 rounded-none" style={{
                    boxShadow: '0 0 15px rgba(239, 68, 68, 0.4)'
                  }}>
                    <div className="text-red-400 font-mono tracking-wide text-center">
                      <div className="text-xl mb-2">⚠</div>
                      NO MISSIONS FOUND FOR "{q.toUpperCase()}"
                      <div className="text-sm mt-2 text-gray-400">
                        Try keywords like: kitchen, bathroom, laundry, desk
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {sel && (
          <div className="max-w-3xl mx-auto">
            <div className="bg-black border-4 border-cyan-400 p-6 rounded-none" style={{
              boxShadow: '0 0 30px rgba(34, 211, 238, 0.4), inset 0 0 30px rgba(34, 211, 238, 0.1)'
            }}>
              <div className="flex items-center gap-4 mb-6">
                <button 
                  className="flex items-center gap-2 px-4 py-2 bg-black border-2 border-red-500 hover:border-red-400 hover:bg-red-900 hover:bg-opacity-30 transition-all duration-200 text-red-400 font-mono tracking-wide rounded-none"
                  onClick={() => setSel(null)}
                  style={{
                    textShadow: '0 0 5px rgba(239, 68, 68, 0.5)',
                    boxShadow: '0 0 10px rgba(239, 68, 68, 0.3)'
                  }}
                >
                  ◄ BACK
                </button>
                <div className="flex-1">
                  <h2 className="text-3xl font-bold text-yellow-400 tracking-widest font-mono" style={{
                    textShadow: '0 0 10px rgba(251, 191, 36, 0.8)'
                  }}>
                    {sel.title.toUpperCase()} 
                  </h2>
                  <p className="text-green-400 mt-1 font-mono tracking-wide" style={{
                    textShadow: '0 0 5px rgba(34, 197, 94, 0.5)'
                  }}>
                    MISSION TIME: ~{sel.time_min} MINUTES
                  </p>
                </div>
              </div>

              {sel.items?.length ? (
                <div className="bg-black border-2 border-purple-500 p-4 mb-6 rounded-none" style={{
                  boxShadow: '0 0 15px rgba(147, 51, 234, 0.3)'
                }}>
                  <h3 className="text-lg font-bold text-purple-400 mb-2 font-mono tracking-wide" style={{
                    textShadow: '0 0 5px rgba(147, 51, 234, 0.8)'
                  }}>
                    ▼ REQUIRED ITEMS:
                  </h3>
                  <p className="text-cyan-400 font-mono tracking-wide" style={{
                    textShadow: '0 0 5px rgba(34, 211, 238, 0.5)'
                  }}>
                    {sel.items.join(" • ")}
                  </p>
                </div>
              ) : null}

              {loadingSpeak && (
                <div className="mb-6 p-4 bg-black border-2 border-blue-400 text-blue-400 rounded-none" style={{
                  boxShadow: '0 0 15px rgba(59, 130, 246, 0.4)'
                }}>
                  <div className="flex items-center gap-2 font-mono tracking-wide">
                    <div className="animate-spin text-xl">◆</div>
                    GENERATING AUDIO TRANSMISSION...
                  </div>
                </div>
              )}

              <div className="flex items-center gap-3 mb-6">
                <button 
                  className={`flex items-center gap-2 px-4 py-2 rounded-none transition-all duration-200 border-2 font-mono tracking-wide ${
                    isMuted 
                      ? 'bg-black border-red-500 text-red-400 hover:bg-red-900 hover:bg-opacity-30' 
                      : 'bg-black border-green-500 text-green-400 hover:bg-green-900 hover:bg-opacity-30'
                  }`}
                  onClick={() => setIsMuted(!isMuted)}
                  style={{
                    textShadow: isMuted 
                      ? '0 0 5px rgba(239, 68, 68, 0.5)' 
                      : '0 0 5px rgba(34, 197, 94, 0.5)',
                    boxShadow: isMuted 
                      ? '0 0 10px rgba(239, 68, 68, 0.3)' 
                      : '0 0 10px rgba(34, 197, 94, 0.3)'
                  }}
                >
                  {isMuted ? "◄◄" : "►►"} {isMuted ? "AUDIO OFF" : "AUDIO ON"}
                </button>
                
                <button 
                  className="flex items-center gap-2 px-4 py-2 rounded-none transition-all duration-200 border-2 font-mono tracking-wide bg-black border-purple-500 text-purple-400 hover:bg-purple-900 hover:bg-opacity-30 disabled:opacity-50 disabled:cursor-not-allowed"
                  onClick={getAdvice}
                  disabled={loadingAdvice}
                  style={{
                    textShadow: '0 0 5px rgba(147, 51, 234, 0.5)',
                    boxShadow: '0 0 10px rgba(147, 51, 234, 0.3)'
                  }}
                >
                  {loadingAdvice ? (
                    <>
                      <div className="animate-spin text-lg">◆</div>
                      ANALYZING...
                    </>
                  ) : (
                    <>
                      ★ GET ADVICE
                    </>
                  )}
                </button>
              </div>

              <div className="space-y-3">
                <h3 className="text-xl font-bold text-cyan-400 mb-4 font-mono tracking-widest" style={{
                  textShadow: '0 0 10px rgba(34, 211, 238, 0.8)'
                }}>
                  ▼ MISSION OBJECTIVES:
                </h3>
                {sel.steps.map((s, i) => (
                  <div 
                    key={i} 
                    className={`flex gap-3 items-start p-3 rounded-none transition-all duration-200 border-2 ${
                      checked[i] 
                        ? 'bg-green-900 bg-opacity-30 border-green-400' 
                        : 'bg-black border-gray-600'
                    }`}
                    style={{
                      boxShadow: checked[i] 
                        ? '0 0 15px rgba(34, 197, 94, 0.4)' 
                        : '0 0 5px rgba(75, 85, 99, 0.3)'
                    }}
                  >
                    <div className="mt-1">
                      <div 
                        className={`w-5 h-5 border-2 cursor-pointer transition-all duration-200 ${
                          checked[i] 
                            ? 'bg-green-400 border-green-400' 
                            : 'bg-black border-cyan-400'
                        }`}
                        onClick={() => {
                          setChecked(prev => {
                            const copy = [...prev];
                            copy[i] = !copy[i];
                            return copy;
                          });
                        }}
                        style={{
                          boxShadow: checked[i] 
                            ? '0 0 10px rgba(34, 197, 94, 0.6)' 
                            : '0 0 5px rgba(34, 211, 238, 0.4)'
                        }}
                      >
                        {checked[i] && (
                          <div className="text-black text-center font-bold text-xs leading-none">
                            ✓
                          </div>
                        )}
                      </div>
                    </div>
                    <span className={`text-sm font-mono tracking-wide ${
                      checked[i] ? 'text-green-200 line-through' : 'text-cyan-400'
                    }`} style={{
                      textShadow: checked[i] 
                        ? '0 0 5px rgba(34, 197, 94, 0.5)' 
                        : '0 0 5px rgba(34, 211, 238, 0.5)'
                    }}>
                      {checked[i] ? '[COMPLETE]' : '[PENDING]'} {s}
                    </span>
                  </div>
                ))}
              </div>

              {/* Advice Panel */}
              {showAdvice && advice && (
                <div className="mt-6 bg-black border-4 border-purple-400 p-6 rounded-none" style={{
                  boxShadow: '0 0 30px rgba(147, 51, 234, 0.4), inset 0 0 30px rgba(147, 51, 234, 0.1)'
                }}>
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-xl font-bold text-purple-400 font-mono tracking-widest" style={{
                      textShadow: '0 0 10px rgba(147, 51, 234, 0.8)'
                    }}>
                      ▼ MISSION ADVISOR:
                    </h3>
                    <button 
                      className="text-purple-400 hover:text-purple-300 transition-colors duration-200 font-mono text-lg"
                      onClick={() => setShowAdvice(false)}
                      style={{
                        textShadow: '0 0 5px rgba(147, 51, 234, 0.5)'
                      }}
                    >
                      ✕
                    </button>
                  </div>
                  <div className="text-cyan-400 font-mono tracking-wide leading-relaxed" style={{
                    textShadow: '0 0 5px rgba(34, 211, 238, 0.5)'
                  }}>
                    {advice.split('\n').map((line, i) => (
                      <p key={i} className={line.startsWith('•') ? 'ml-2 mb-2' : 'mb-2'}>
                        {line}
                      </p>
                    ))}
                  </div>
                </div>
              )}

              {/* Hidden audio player for automatic playback */}
              {audioUrl && !isMuted && (
                <audio 
                  src={audioUrl} 
                  autoPlay 
                  onEnded={() => setAudioUrl(null)}
                  style={{ display: 'none' }}
                />
              )}

              {congratsPlaying && (
                <div className="mt-6 p-4 bg-black border-2 border-green-400 text-green-400 rounded-none" style={{
                  boxShadow: '0 0 20px rgba(34, 197, 94, 0.5)'
                }}>
                  <div className="flex items-center gap-2 font-mono tracking-wide">
                    <div className="animate-pulse text-xl">★</div>
                    PLAYING VICTORY TRANSMISSION...
                  </div>
                </div>
              )}

              {checked.length > 0 && checked.every(Boolean) && !congratsPlaying && (
                <div className="mt-6 p-6 bg-black border-4 border-yellow-400 text-center rounded-none animate-pulse" style={{
                  boxShadow: '0 0 30px rgba(251, 191, 36, 0.6), inset 0 0 20px rgba(251, 191, 36, 0.2)'
                }}>
                  <div className="text-4xl mb-2 animate-bounce">★★★</div>
                  <h3 className="text-2xl font-bold text-yellow-400 mb-2 font-mono tracking-widest" style={{
                    textShadow: '0 0 15px rgba(251, 191, 36, 1)'
                  }}>
                    ▓▓ MISSION COMPLETE! ▓▓
                  </h3>
                  <p className="text-green-400 font-mono tracking-wide" style={{
                    textShadow: '0 0 10px rgba(34, 197, 94, 0.8)'
                  }}>
                    EXCELLENT WORK, AGENT! OBJECTIVE ACHIEVED!
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
        </div>
      </main>
      
      {/* Credit Footer */}
      <footer className="text-center py-6">
        <p className="text-gray-500 text-sm font-mono tracking-widest" style={{
          textShadow: '0 0 3px rgba(107, 114, 128, 0.5)'
        }}>
          ▓ Developed by{' '}
          <button
            onClick={() => window.open('https://camgitblame.netlify.app/', '_blank')}
            className="text-cyan-400 hover:text-cyan-300 transition-colors duration-200 cursor-pointer underline decoration-dotted hover:decoration-solid"
            style={{
              textShadow: '0 0 5px rgba(34, 211, 238, 0.5)'
            }}
          >
            Cam Nguyen
          </button>
          {' '}© 2025 ▓
        </p>
      </footer>
    </div>
  );
}
