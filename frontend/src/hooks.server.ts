import type { Handle } from "@sveltejs/kit";

const BACKEND_URL = process.env.BACKEND_URL || "http://backend:8000";

export const handle: Handle = async ({ event, resolve }) => {
  if (event.url.pathname.startsWith("/api/")) {
    const backendUrl = `${BACKEND_URL}${event.url.pathname}${event.url.search}`;

    const headers = new Headers();
    event.request.headers.forEach((value, key) => {
      if (key !== "host") {
        headers.set(key, value);
      }
    });

    try {
      let body: BodyInit | undefined = undefined;

      if (event.request.method !== "GET" && event.request.method !== "HEAD") {
        // Clone the request so the body stream isn't consumed
        const cloned = event.request.clone();
        const buffer = await cloned.arrayBuffer();
        body = buffer;
      }

      const response = await fetch(backendUrl, {
        method: event.request.method,
        headers,
        body,
      });

      const responseHeaders = new Headers();
      // Get raw headers to handle multiple Set-Cookie
      const setCookieHeaders: string[] = [];
      response.headers.forEach((value, key) => {
        if (key.toLowerCase() === "set-cookie") {
          setCookieHeaders.push(value);
        } else if (key !== "transfer-encoding") {
          responseHeaders.set(key, value);
        }
      });

      // Use raw Response to preserve multiple Set-Cookie headers
      const respBody = await response.arrayBuffer();
      const proxyResponse = new Response(respBody, {
        status: response.status,
        statusText: response.statusText,
        headers: responseHeaders,
      });

      // Add Set-Cookie headers individually
      for (const cookie of setCookieHeaders) {
        proxyResponse.headers.append("Set-Cookie", cookie);
      }

      return proxyResponse;
    } catch (error) {
      return new Response(
        JSON.stringify({ detail: { code: "PROXY_ERROR", message: "Backend unreachable" } }),
        { status: 502, headers: { "Content-Type": "application/json" } }
      );
    }
  }

  return resolve(event);
};
