import fs from "fs";
import path from "path";
import { PrunedModelData, TreeNode } from "./types";
import { extractFeatures } from "./extractor";
import { generateReasons } from "./reasons";

let cachedModel: PrunedModelData | null = null;

export function getModel(): PrunedModelData {
  if (cachedModel) return cachedModel;

  const modelPath = path.join(process.cwd(), "models", "model_pruned.json");
  if (!fs.existsSync(modelPath)) {
    throw new Error(`Model artifact not found at ${modelPath}`);
  }

  const raw = fs.readFileSync(modelPath, "utf-8");
  cachedModel = JSON.parse(raw) as PrunedModelData;
  return cachedModel;
}

function evalTree(
  node: TreeNode,
  vector: number[],
  contributions: Record<number, number>
): number {
  if (node.v !== undefined) {
    return node.v;
  }

  const featIdx = node.f ?? 0;
  const featVal = vector[featIdx] ?? 0;
  const thresh = node.t ?? 0;

  if (featVal <= thresh) {
    const leafVal = evalTree(node.l!, vector, contributions);
    contributions[featIdx] = (contributions[featIdx] || 0) + leafVal * 0.1;
    return leafVal;
  } else {
    const leafVal = evalTree(node.r!, vector, contributions);
    contributions[featIdx] = (contributions[featIdx] || 0) + leafVal * 0.1;
    return leafVal;
  }
}

function sigmoid(x: number): number {
  return 1.0 / (1.0 + Math.exp(-x));
}

export function predictUrl(rawUrl: string): {
  url: string;
  label: "phishing" | "legitimate";
  score: number;
  risk_level: "low" | "medium" | "high";
  reasons: string[];
  model_version: string;
  disclaimer: string;
  features: Record<string, number>;
  contributions: Record<string, number>;
} {
  const model = getModel();
  const features = extractFeatures(rawUrl);

  const vector = model.feature_names.map((name) => features[name] ?? 0);
  const rawContribs: Record<number, number> = {};

  let rawScore = 0.0;
  for (const tree of model.pruned_trees) {
    rawScore += evalTree(tree, vector, rawContribs);
  }

  const proba = Number(sigmoid(rawScore).toFixed(4));
  const lowThresh = model.threshold_config.low_risk_upper || 0.35;
  const highThresh = model.threshold_config.high_risk_lower || 0.70;
  const decThresh = model.threshold_config.default_decision_threshold || 0.50;

  let riskLevel: "low" | "medium" | "high" = "low";
  if (proba < lowThresh) {
    riskLevel = "low";
  } else if (proba < highThresh) {
    riskLevel = "medium";
  } else {
    riskLevel = "high";
  }

  const isPhishing = proba >= decThresh;
  const label: "phishing" | "legitimate" = isPhishing ? "phishing" : "legitimate";

  const contributionsByName: Record<string, number> = {};
  for (let i = 0; i < model.feature_names.length; i++) {
    const fName = model.feature_names[i];
    contributionsByName[fName] = rawContribs[i] || 0;
  }

  const reasons = generateReasons(
    rawUrl,
    features,
    proba,
    riskLevel,
    contributionsByName
  );

  const disclaimer =
    "Hasil ini merupakan perkiraan berbasis model machine learning pada struktur URL, " +
    "bukan jaminan mutlak. Jangan memasukkan data rahasia atau kredensial pada situs yang mencurigakan.";

  return {
    url: rawUrl,
    label,
    score: proba,
    risk_level: riskLevel,
    reasons,
    model_version: model.version,
    disclaimer,
    features,
    contributions: contributionsByName,
  };
}
