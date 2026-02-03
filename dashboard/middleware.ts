import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // Allow public access to login page
  if (request.nextUrl.pathname === '/login') {
    return NextResponse.next();
  }

  // Allow access to root (redirects to login)
  if (request.nextUrl.pathname === '/') {
    return NextResponse.next();
  }

  // For all other routes, check if district is logged in
  // This is handled client-side, but middleware can add headers if needed
  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico|assets).*)'],
};
