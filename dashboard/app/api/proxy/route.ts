import { NextRequest, NextResponse } from 'next/server';

/**
 * Server-side Proxy for n8n API
 * Bypasses CORS restrictions when communicating with local n8n on port 5678
 */
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const endpoint = searchParams.get('endpoint');
  const district = searchParams.get('district');
  
  if (!endpoint) {
    return NextResponse.json({ error: 'Missing endpoint parameter' }, { status: 400 });
  }

  const n8nBaseUrl = process.env.NEXT_PUBLIC_N8N_BASE_URL || 'http://localhost:5678/webhook';
  
  // Clean base URL to remove trailing slashes or /webhook suffix for flexible joining
  const base = n8nBaseUrl.replace(/\/webhook-test\/?$/, '').replace(/\/webhook\/?$/, '');
  
  // Try Production URL first
  const tryUrls = [
    `${base}/webhook${endpoint}`,
    `${base}/webhook-test${endpoint}`
  ];

  let lastError = null;

  for (const url of tryUrls) {
    try {
      const finalUrl = new URL(url);
      if (district) {
        finalUrl.searchParams.append('district', district);
      }

      console.log(`[Proxy] Routing request to: ${finalUrl.toString()}`);

      const response = await fetch(finalUrl.toString(), {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': 'true'
        },
        cache: 'no-store'
      });

      if (response.ok) {
        let data = await response.json();
        console.log(`[Proxy] Success! Received ${Array.isArray(data) ? data.length : '1'} items`);
        
        // Standardization logic
        if (Array.isArray(data) && data.length > 0 && data[0].json) {
          data = data.map((item: any) => item.json);
        } else if (data.data || data.messages || data.events) {
          data = data.data || data.messages || data.events;
        }

        return NextResponse.json(data);
      }
      
      console.warn(`[Proxy] ${url} failed with status: ${response.status}`);
    } catch (error: any) {
      console.error(`[Proxy] Error calling ${url}:`, error.message);
      lastError = error;
    }
  }

  return NextResponse.json({ 
    error: 'n8n Bridge Failed', 
    details: lastError?.message || 'Check n8n Credentials or Workflow Status' 
  }, { status: 502 });
}
