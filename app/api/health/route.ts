import { NextResponse } from "next/server";
import { getModel } from "@/lib/ml/predictor";

export async function GET() {
  try {
    const model = getModel();
    return NextResponse.json({
      status: "ok",
      model_loaded: true,
      version: model.version || "1.0.0",
      engine: "TypeScript-Native / LightGBM (Zero Python Dependency)",
    });
  } catch (error: any) {
    return NextResponse.json(
      {
        status: "error",
        model_loaded: false,
        detail: error?.message || "Failed to load model",
      },
      { status: 500 }
    );
  }
}
