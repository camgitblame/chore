export const runtime = "nodejs";

export async function POST(req: Request) {
  try {
    const body = await req.text();
    const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "https://chore-api-rag-611389647575.us-central1.run.app";
    
    console.log('TTS Proxy - API Base:', API_BASE);
    console.log('TTS Proxy - Request body:', body);
    
    const resp = await fetch(`${API_BASE}/tts`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": process.env.INTERNAL_API_KEY! // server-side only
      },
      body
    });
    
    console.log('TTS Proxy - Response status:', resp.status);
    console.log('TTS Proxy - Response headers:', Object.fromEntries(resp.headers.entries()));
    
    if (!resp.ok) {
      const errorText = await resp.text();
      console.error('TTS Proxy - Error response:', errorText);
      return new Response(errorText, { status: resp.status });
    }
    
    // Pass through body/headers/status
    return new Response(resp.body, { 
      status: resp.status, 
      headers: {
        'Content-Type': resp.headers.get('Content-Type') || 'application/json',
        'Content-Length': resp.headers.get('Content-Length') || '',
      }
    });
  } catch (error) {
    console.error('TTS Proxy - Catch error:', error);
    return new Response(JSON.stringify({ error: 'TTS proxy failed', details: error.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
