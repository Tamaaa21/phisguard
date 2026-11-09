export interface CheckRequest {
  url: string;
}

export interface CheckResponse {
  url: string;
  label: "phishing" | "legitimate";
  score: number;
  risk_level: "low" | "medium" | "high";
  reasons: string[];
  model_version: string;
  disclaimer: string;
  engine?: string;
  features?: Record<string, number>;
  contributions?: Record<string, number>;
}

export interface ModelInfoResponse {
  model_name: string;
  model_version: string;
  trained_at: string;
  feature_count: number;
  train_samples: number;
  test_samples: number;
  metrics_test: Record<string, number>;
  metrics_validation: Record<string, number>;
  threshold_config: Record<string, number>;
  top_features: Array<{ feature: string; importance: number }>;
}

export interface TreeNode {
  v?: number; // leaf_value
  f?: number; // split_feature index
  t?: number; // threshold
  l?: TreeNode; // left child (<= threshold)
  r?: TreeNode; // right child (> threshold)
  dl?: boolean; // default left if missing
}

export interface PrunedModelData {
  model_name: string;
  version: string;
  feature_names: string[];
  threshold_config: {
    low_risk_upper: number;
    high_risk_lower: number;
    default_decision_threshold: number;
    optimal_f1_threshold?: number;
  };
  trained_at: string;
  pruned_trees: TreeNode[];
}
