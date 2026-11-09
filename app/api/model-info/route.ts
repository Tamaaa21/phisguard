import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function GET() {
  try {
    const metadataPath = path.join(process.cwd(), "models", "metadata.json");
    if (!fs.existsSync(metadataPath)) {
      return NextResponse.json(
        { detail: "Informasi model belum tersedia." },
        { status: 503 }
      );
    }

    const raw = fs.readFileSync(metadataPath, "utf-8");
    const meta = JSON.parse(raw);

    return NextResponse.json({
      model_name: meta.model_name || "Tuned_LightGBM",
      model_version: meta.version || "1.0.0",
      trained_at: meta.trained_at || "",
      feature_count: meta.feature_count || 49,
      train_samples: meta.train_samples || 7550,
      test_samples: meta.test_samples || 1690,
      metrics_test: meta.metrics_test || {},
      metrics_validation: meta.metrics_validation || {},
      threshold_config: meta.threshold_config || {},
      top_features: meta.top_features || [],
    });
  } catch (error: any) {
    return NextResponse.json(
      { detail: error?.message || "Internal server error" },
      { status: 500 }
    );
  }
}
