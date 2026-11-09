import { NextRequest, NextResponse } from "next/server";
import { predictUrl } from "@/lib/ml/predictor";

const MAX_URL_LENGTH = 2048;
const ALLOWED_SCHEMES = new Set(["http", "https"]);

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const rawUrl = body?.url;

    if (typeof rawUrl !== "string") {
      return NextResponse.json(
        { detail: "Field 'url' wajib disertakan berupa string." },
        { status: 400 }
      );
    }

    // 1. Length check
    if (rawUrl.length > MAX_URL_LENGTH) {
      return NextResponse.json(
        {
          detail: `URL terlalu panjang (${rawUrl.length} karakter). Maksimum ${MAX_URL_LENGTH} karakter.`,
        },
        { status: 413 }
      );
    }

    // 2. Empty check
    const cleanUrl = rawUrl.trim();
    if (!cleanUrl) {
      return NextResponse.json(
        { detail: "URL tidak boleh kosong." },
        { status: 400 }
      );
    }

    // 3. Control character check
    for (let i = 0; i < cleanUrl.length; i++) {
      if (cleanUrl.charCodeAt(i) < 32) {
        return NextResponse.json(
          { detail: "URL mengandung karakter kontrol ilegal." },
          { status: 400 }
        );
      }
    }

    // 4. Scheme validation
    let checkUrlStr = cleanUrl;
    if (cleanUrl.includes(":")) {
      const schemeCandidate = cleanUrl.split(":", 1)[0].toLowerCase();
      if (
        schemeCandidate &&
        /^[a-z][a-z0-9+.-]*$/.test(schemeCandidate) &&
        !schemeCandidate.includes("/") &&
        !schemeCandidate.includes(".")
      ) {
        if (!ALLOWED_SCHEMES.has(schemeCandidate)) {
          return NextResponse.json(
            {
              detail: `Skema URL '${schemeCandidate}' tidak didukung. Gunakan HTTP atau HTTPS.`,
            },
            { status: 400 }
          );
        }
      }
    }

    if (!checkUrlStr.includes("://")) {
      if (checkUrlStr.startsWith("//")) {
        checkUrlStr = "http:" + checkUrlStr;
      } else {
        checkUrlStr = "http://" + checkUrlStr;
      }
    }

    let parsed: URL;
    try {
      parsed = new URL(checkUrlStr);
    } catch {
      return NextResponse.json(
        { detail: "Format URL tidak valid." },
        { status: 400 }
      );
    }

    const scheme = parsed.protocol.replace(":", "").toLowerCase();
    if (!ALLOWED_SCHEMES.has(scheme)) {
      return NextResponse.json(
        {
          detail: `Skema URL '${scheme}' tidak didukung. Gunakan HTTP atau HTTPS.`,
        },
        { status: 400 }
      );
    }

    if (!parsed.host.trim()) {
      return NextResponse.json(
        { detail: "URL tidak memiliki nama domain/host yang valid." },
        { status: 400 }
      );
    }

    // 5. Check if external FastAPI forwarding is configured
    const fastapiUrl = process.env.FASTAPI_BACKEND_URL;
    if (fastapiUrl) {
      try {
        const backendResp = await fetch(`${fastapiUrl.replace(/\/$/, "")}/api/check`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url: cleanUrl }),
        });
        const backendData = await backendResp.json();
        return NextResponse.json(backendData, { status: backendResp.status });
      } catch (fwdErr: any) {
        console.warn("FastAPI backend forwarding failed, falling back to local TypeScript engine:", fwdErr);
        // Fallback to local engine below
      }
    }

    // 6. Predict using embedded native TypeScript ML engine
    const prediction = predictUrl(cleanUrl);

    return NextResponse.json({
      url: prediction.url,
      label: prediction.label,
      score: prediction.score,
      risk_level: prediction.risk_level,
      reasons: prediction.reasons,
      model_version: prediction.model_version,
      disclaimer: prediction.disclaimer,
      engine: "TypeScript-Native / LightGBM",
    });
  } catch (err: any) {
    console.error("Check URL error:", err);
    return NextResponse.json(
      { detail: "Terjadi kesalahan internal saat memeriksa URL." },
      { status: 500 }
    );
  }
}
