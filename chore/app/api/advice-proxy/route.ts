import { NextRequest, NextResponse } from 'next/server';

// RAG-enabled advice proxy for production deployment
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    console.log('Advice proxy received body:', body);
    
    const backendUrl = `${process.env.NEXT_PUBLIC_API_BASE}/advice`;
    console.log('Calling backend URL:', backendUrl);
    console.log('Using API key:', process.env.INTERNAL_API_KEY ? 'Present' : 'Missing');
    
    const response = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': process.env.INTERNAL_API_KEY || '',
      },
      body: JSON.stringify(body),
    });

    console.log('Backend response status:', response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend error response:', errorText);
      return NextResponse.json(
        { error: 'Failed to get advice', details: errorText },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('Backend success response:', data);
    return NextResponse.json(data);
  } catch (error) {
    console.error('Advice proxy error:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error.message },
      { status: 500 }
    );
  }
}
