import { NextRequest, NextResponse } from "next/server";

/**
 * This is a UX-layer guard only — it redirects unauthenticated/wrong-role
 * users away from a route group before the page even renders. It is NOT
 * the source of truth for authorization: every API call is independently
 * verified by the FastAPI backend via the JWT (see core/deps.py). Do not
 * rely on this middleware alone to protect data.
 *
 * `placer_role` is a small, non-httpOnly cookie set by the frontend right
 * after a successful login (see Phase 4's auth flow), distinct from the
 * httpOnly refresh-token cookie which JS/middleware never reads.
 */
const ROLE_ROUTE_PREFIX: Record<string, string> = {
  student: "/dashboard",
  tpo: "/tpo/dashboard",
  admin: "/admin/dashboard",
};

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const role = request.cookies.get("placer_role")?.value;

  const isProtected =
    pathname.startsWith("/dashboard") ||
    pathname.startsWith("/tpo") ||
    pathname.startsWith("/admin");

  if (!isProtected) {
    return NextResponse.next();
  }

  if (!role) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("redirect", pathname);
    return NextResponse.redirect(loginUrl);
  }

  const allowedPrefix = ROLE_ROUTE_PREFIX[role];
  if (allowedPrefix && !pathname.startsWith(allowedPrefix)) {
    return NextResponse.redirect(new URL(allowedPrefix, request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/tpo/:path*", "/admin/:path*"],
};
