"use client";
import { useEffect, useState } from "react";

type Chore = { id:string; title:string; items:string[]; steps:string[]; time_min:number };

export default function Home() {
  const [q, setQ] = useState("");
  const [chores, setChores] = useState<Chore[]>([]);
  const [sel, setSel] = useState<Chore | null>(null);

  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [loadingSpeak, setLoadingSpeak] = useState(false);
  const [congratsPlaying, setCongratsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);

  // Default voice ID 
  const defaultVoiceId = "21m00Tcm4TlvDq8ikWAM"; 

  // Load chores from FastAPI
  useEffect(() => {
    const url = `${process.env.NEXT_PUBLIC_API_BASE}/chores?q=${encodeURIComponent(q)}`;
    fetch(url).then(r => r.json()).then(d => setChores(d.chores || []));
  }, [q]);

  // Checklist state for selected chore
  const [checked, setChecked] = useState<boolean[]>([]);
  useEffect(() => { setChecked(sel?.steps?.map(() => false) || []); }, [sel]);

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

    // call your Next.js proxy so INTERNAL_API_KEY is not exposed
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
        text: "Nice work! You finished the chore. Take a breath, hydrate, and enjoy the clean space.",
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
    <main className="min-h-screen bg-gray-900 text-white">
      <div className="p-6 max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-white mb-4">ADHD Chore Chart</h1>
          <p className="text-gray-400 text-lg">Find and complete your daily tasks with guided audio instructions</p>
        </div>

        {!sel && (
          <div className="max-w-xl mx-auto">
            <div className="relative">
              <input
                value={q}
                onChange={e => setQ(e.target.value)}
                placeholder="Search chores (e.g., microwave, desk, kitchen...)"
                className="w-full p-4 text-lg rounded-xl bg-gray-800 border border-gray-700 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-lg"
              />
              <div className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400">
                🔍
              </div>
            </div>
            {q && (
              <div className="mt-6 space-y-3">
                {chores.map(c => (
                  <div key={c.id} className="bg-gray-800 rounded-lg border border-gray-700 hover:border-gray-600 transition-colors">
                    <button 
                      className="w-full p-4 text-left hover:bg-gray-750 rounded-lg transition-colors"
                      onClick={() => setSel(c)}
                    >
                      <div className="flex justify-between items-center">
                        <div>
                          <h3 className="text-lg font-medium text-white">{c.title}</h3>
                          <p className="text-gray-400 text-sm mt-1">~{c.time_min} minutes</p>
                        </div>
                        <div className="text-gray-400">→</div>
                      </div>
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {sel && (
          <div className="max-w-3xl mx-auto">
            <div className="bg-gray-800 rounded-xl border border-gray-700 p-6 shadow-xl">
              <div className="flex items-center gap-4 mb-6">
                <button 
                  className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors text-white"
                  onClick={() => setSel(null)}
                >
                  ← Back
                </button>
                <div className="flex-1">
                  <h2 className="text-2xl font-bold text-white">{sel.title}</h2>
                  <p className="text-gray-400 mt-1">Estimated time: ~{sel.time_min} minutes</p>
                </div>
              </div>

              {sel.items?.length ? (
                <div className="bg-gray-750 rounded-lg p-4 mb-6 border border-gray-600">
                  <h3 className="text-lg font-semibold text-white mb-2">Items needed:</h3>
                  <p className="text-gray-300">{sel.items.join(", ")}</p>
                </div>
              ) : null}

              {loadingSpeak && (
                <div className="mb-6 p-4 bg-blue-900 border border-blue-700 rounded-lg text-blue-200">
                  <div className="flex items-center gap-2">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-400"></div>
                    🔊 Generating audio...
                  </div>
                </div>
              )}

              <div className="flex items-center gap-3 mb-6">
                <button 
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors border ${
                    isMuted 
                      ? 'bg-red-900 border-red-700 text-red-200 hover:bg-red-800' 
                      : 'bg-green-900 border-green-700 text-green-200 hover:bg-green-800'
                  }`}
                  onClick={() => setIsMuted(!isMuted)}
                >
                  {isMuted ? "🔇" : "🔊"} {isMuted ? "Unmute" : "Mute"} Voice
                </button>
              </div>

              <div className="space-y-3">
                <h3 className="text-lg font-semibold text-white mb-4">Steps to complete:</h3>
                {sel.steps.map((s, i) => (
                  <div 
                    key={i} 
                    className={`flex gap-3 items-start p-3 rounded-lg transition-colors ${
                      checked[i] ? 'bg-green-900 border border-green-700' : 'bg-gray-750 border border-gray-600'
                    }`}
                  >
                    <input
                      type="checkbox"
                      className="mt-1 h-5 w-5 rounded border-gray-500 bg-gray-700 text-green-500 focus:ring-green-500 focus:ring-2"
                      checked={checked[i] || false}
                      onChange={() => {
                        setChecked(prev => {
                          const copy = [...prev];
                          copy[i] = !copy[i];
                          return copy;
                        });
                      }}
                    />
                    <span className={`text-sm ${checked[i] ? 'text-green-200 line-through' : 'text-gray-200'}`}>
                      {s}
                    </span>
                  </div>
                ))}
              </div>

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
                <div className="mt-6 p-4 bg-green-900 border border-green-700 rounded-lg text-green-200">
                  <div className="flex items-center gap-2">
                    <div className="animate-pulse">🎉</div>
                    Playing congratulations message...
                  </div>
                </div>
              )}

              {checked.length > 0 && checked.every(Boolean) && !congratsPlaying && (
                <div className="mt-6 p-6 bg-gradient-to-r from-green-900 to-blue-900 border border-green-700 rounded-lg text-center">
                  <div className="text-2xl mb-2">🎉</div>
                  <h3 className="text-xl font-bold text-white mb-2">Congratulations!</h3>
                  <p className="text-green-200">You completed all the steps! Great job!</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
