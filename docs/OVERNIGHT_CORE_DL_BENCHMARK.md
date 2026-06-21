# Overnight Core DL Benchmark

## Status

- Status: `completed`
- Generated: `2026-06-21T02:43:24.740487+00:00`
- Completed: `2026-06-21T03:56:44.603931+00:00`
- Runtime seconds: `4400.167`

## Dataset

- Source dataset: `data/models/run_history_v4/basecamp4_shock_20260618_121556/enterprise_temporal_sequences_v4_shock.csv`
- Target column: `target_v4_opportunity_shock`
- Rows used: `2700`
- Feature count: `120`

## Run configuration

- Seeds: `[3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79]`
- Max rows: `50000`
- Max features: `120`
- Epochs: `240`
- Patience: `28`
- Batch size: `256`

## Model families

### sklearn_mlp_21_seed

- Family: `MLP`
- Framework: `scikit-learn`
- Status: `completed`
- Notes: Twenty-one-seed sklearn MLP with early stopping. Benchmark signal only, not a clinical model claim.

| Metric | Mean | Std | Min | Max | N |
|---|---:|---:|---:|---:|---:|
| `accuracy` | `0.978554` | `0.006822` | `0.967407` | `0.98963` | `21` |
| `balanced_accuracy` | `0.969635` | `0.01114` | `0.949437` | `0.987228` | `21` |
| `brier` | `0.020319` | `0.005923` | `0.007725` | `0.029455` | `21` |
| `f1_macro` | `0.971587` | `0.009104` | `0.956414` | `0.986267` | `21` |
| `pr_auc` | `0.979718` | `0.009639` | `0.956047` | `0.996918` | `21` |
| `roc_auc` | `0.988952` | `0.007439` | `0.965376` | `0.998752` | `21` |
| `runtime_seconds` | `4.691` | `None` | `None` | `8.089` | `None` |

- Completed seeds: `21`
- Failed seeds: `0`

### torch_mlp_21_seed

- Family: `MLP`
- Framework: `PyTorch`
- Status: `completed`
- Device: `cpu`
- Sequence mode: `single_step_tabular_tensor`
- Notes: Architecture benchmark over tabular features shaped as one-step tensors. Stronger temporal claims require a future true sequence construction phase.

| Metric | Mean | Std | Min | Max | N |
|---|---:|---:|---:|---:|---:|
| `accuracy` | `0.981093` | `0.009546` | `0.957037` | `0.995556` | `21` |
| `balanced_accuracy` | `0.971514` | `0.016487` | `0.929088` | `0.99316` | `21` |
| `brier` | `0.015296` | `0.005222` | `0.007464` | `0.024862` | `21` |
| `f1_macro` | `0.974807` | `0.012933` | `0.941725` | `0.994115` | `21` |
| `pr_auc` | `0.989761` | `0.006666` | `0.966878` | `0.998476` | `21` |
| `roc_auc` | `0.995378` | `0.006549` | `0.96685` | `0.999491` | `21` |
| `runtime_seconds` | `31.482` | `None` | `None` | `44.252` | `None` |

- Completed seeds: `21`
- Failed seeds: `0`

### torch_residual_mlp_21_seed

- Family: `ResidualMLP`
- Framework: `PyTorch`
- Status: `completed`
- Device: `cpu`
- Sequence mode: `single_step_tabular_tensor`
- Notes: Architecture benchmark over tabular features shaped as one-step tensors. Stronger temporal claims require a future true sequence construction phase.

| Metric | Mean | Std | Min | Max | N |
|---|---:|---:|---:|---:|---:|
| `accuracy` | `0.984903` | `0.004105` | `0.974815` | `0.992593` | `21` |
| `balanced_accuracy` | `0.980923` | `0.005609` | `0.96768` | `0.992048` | `21` |
| `brier` | `0.012664` | `0.00392` | `0.00713` | `0.022444` | `21` |
| `f1_macro` | `0.980147` | `0.005338` | `0.966778` | `0.990266` | `21` |
| `pr_auc` | `0.991126` | `0.007976` | `0.969298` | `0.999045` | `21` |
| `roc_auc` | `0.996085` | `0.005629` | `0.972199` | `0.999676` | `21` |
| `runtime_seconds` | `14.187` | `None` | `None` | `24.036` | `None` |

- Completed seeds: `21`
- Failed seeds: `0`

### torch_wide_deep_mlp_21_seed

- Family: `WideDeepMLP`
- Framework: `PyTorch`
- Status: `completed`
- Device: `cpu`
- Sequence mode: `single_step_tabular_tensor`
- Notes: Architecture benchmark over tabular features shaped as one-step tensors. Stronger temporal claims require a future true sequence construction phase.

| Metric | Mean | Std | Min | Max | N |
|---|---:|---:|---:|---:|---:|
| `accuracy` | `0.985961` | `0.006127` | `0.974815` | `0.994074` | `21` |
| `balanced_accuracy` | `0.979616` | `0.009491` | `0.963816` | `0.996024` | `21` |
| `brier` | `0.012684` | `0.004676` | `0.005122` | `0.023838` | `21` |
| `f1_macro` | `0.981405` | `0.008154` | `0.966519` | `0.992257` | `21` |
| `pr_auc` | `0.988235` | `0.008822` | `0.963007` | `0.998001` | `21` |
| `roc_auc` | `0.993803` | `0.00782` | `0.961292` | `0.999376` | `21` |
| `runtime_seconds` | `16.236` | `None` | `None` | `17.409` | `None` |

- Completed seeds: `21`
- Failed seeds: `0`

### torch_lstm_21_seed

- Family: `LSTM`
- Framework: `PyTorch`
- Status: `completed`
- Device: `cpu`
- Sequence mode: `single_step_tabular_tensor`
- Notes: Architecture benchmark over tabular features shaped as one-step tensors. Stronger temporal claims require a future true sequence construction phase.

| Metric | Mean | Std | Min | Max | N |
|---|---:|---:|---:|---:|---:|
| `accuracy` | `0.960353` | `0.007371` | `0.948148` | `0.973333` | `21` |
| `balanced_accuracy` | `0.940982` | `0.013158` | `0.918964` | `0.963711` | `21` |
| `brier` | `0.028629` | `0.004286` | `0.019648` | `0.034748` | `21` |
| `f1_macro` | `0.946967` | `0.010027` | `0.930796` | `0.963904` | `21` |
| `pr_auc` | `0.974786` | `0.008134` | `0.951796` | `0.986359` | `21` |
| `roc_auc` | `0.988061` | `0.007736` | `0.95715` | `0.995261` | `21` |
| `runtime_seconds` | `23.856` | `None` | `None` | `27.943` | `None` |

- Completed seeds: `21`
- Failed seeds: `0`

### torch_gru_21_seed

- Family: `GRU`
- Framework: `PyTorch`
- Status: `completed`
- Device: `cpu`
- Sequence mode: `single_step_tabular_tensor`
- Notes: Architecture benchmark over tabular features shaped as one-step tensors. Stronger temporal claims require a future true sequence construction phase.

| Metric | Mean | Std | Min | Max | N |
|---|---:|---:|---:|---:|---:|
| `accuracy` | `0.95478` | `0.007807` | `0.93037` | `0.965926` | `21` |
| `balanced_accuracy` | `0.935598` | `0.014937` | `0.897805` | `0.961759` | `21` |
| `brier` | `0.032678` | `0.00477` | `0.026195` | `0.045778` | `21` |
| `f1_macro` | `0.939721` | `0.010921` | `0.906322` | `0.955224` | `21` |
| `pr_auc` | `0.971588` | `0.008866` | `0.946424` | `0.979705` | `21` |
| `roc_auc` | `0.986829` | `0.008459` | `0.954017` | `0.993389` | `21` |
| `runtime_seconds` | `20.776` | `None` | `None` | `23.14` | `None` |

- Completed seeds: `21`
- Failed seeds: `0`

### torch_tcn_21_seed

- Family: `TCN`
- Framework: `PyTorch`
- Status: `completed`
- Device: `cpu`
- Sequence mode: `single_step_tabular_tensor`
- Notes: Architecture benchmark over tabular features shaped as one-step tensors. Stronger temporal claims require a future true sequence construction phase.

| Metric | Mean | Std | Min | Max | N |
|---|---:|---:|---:|---:|---:|
| `accuracy` | `0.983915` | `0.008557` | `0.964444` | `0.994074` | `21` |
| `balanced_accuracy` | `0.978528` | `0.012309` | `0.937884` | `0.990285` | `21` |
| `brier` | `0.014327` | `0.006712` | `0.005637` | `0.028848` | `21` |
| `f1_macro` | `0.978788` | `0.011317` | `0.951673` | `0.992168` | `21` |
| `pr_auc` | `0.981726` | `0.012288` | `0.952983` | `0.99577` | `21` |
| `roc_auc` | `0.99235` | `0.008298` | `0.957811` | `0.998416` | `21` |
| `runtime_seconds` | `14.369` | `None` | `None` | `17.766` | `None` |

- Completed seeds: `21`
- Failed seeds: `0`

### torch_transformer_encoder_21_seed

- Family: `TransformerEncoder`
- Framework: `PyTorch`
- Status: `completed`
- Device: `cpu`
- Sequence mode: `single_step_tabular_tensor`
- Notes: Architecture benchmark over tabular features shaped as one-step tensors. Stronger temporal claims require a future true sequence construction phase.

| Metric | Mean | Std | Min | Max | N |
|---|---:|---:|---:|---:|---:|
| `accuracy` | `0.986596` | `0.005917` | `0.971852` | `0.995556` | `21` |
| `balanced_accuracy` | `0.981603` | `0.007886` | `0.961984` | `0.991228` | `21` |
| `brier` | `0.010366` | `0.004626` | `0.004306` | `0.019443` | `21` |
| `f1_macro` | `0.982315` | `0.007795` | `0.962869` | `0.994092` | `21` |
| `pr_auc` | `0.995636` | `0.00512` | `0.975842` | `0.9998` | `21` |
| `roc_auc` | `0.997803` | `0.004658` | `0.977316` | `0.999931` | `21` |
| `runtime_seconds` | `46.538` | `None` | `None` | `57.79` | `None` |

- Completed seeds: `21`
- Failed seeds: `0`

### torch_cnn_mlp_hybrid_21_seed

- Family: `CNNMLPHybrid`
- Framework: `PyTorch`
- Status: `completed`
- Device: `cpu`
- Sequence mode: `single_step_tabular_tensor`
- Notes: Architecture benchmark over tabular features shaped as one-step tensors. Stronger temporal claims require a future true sequence construction phase.

| Metric | Mean | Std | Min | Max | N |
|---|---:|---:|---:|---:|---:|
| `accuracy` | `0.982716` | `0.008631` | `0.961481` | `0.995556` | `21` |
| `balanced_accuracy` | `0.974604` | `0.016596` | `0.933983` | `0.991279` | `21` |
| `brier` | `0.014036` | `0.005149` | `0.004874` | `0.026884` | `21` |
| `f1_macro` | `0.976989` | `0.011811` | `0.947646` | `0.994115` | `21` |
| `pr_auc` | `0.985708` | `0.007377` | `0.967383` | `0.996417` | `21` |
| `roc_auc` | `0.992207` | `0.006296` | `0.971712` | `0.998601` | `21` |
| `runtime_seconds` | `18.708` | `None` | `None` | `29.692` | `None` |

- Completed seeds: `21`
- Failed seeds: `0`

### torch_gated_mlp_21_seed

- Family: `GatedMLP`
- Framework: `PyTorch`
- Status: `completed`
- Device: `cpu`
- Sequence mode: `single_step_tabular_tensor`
- Notes: Architecture benchmark over tabular features shaped as one-step tensors. Stronger temporal claims require a future true sequence construction phase.

| Metric | Mean | Std | Min | Max | N |
|---|---:|---:|---:|---:|---:|
| `accuracy` | `0.982363` | `0.008329` | `0.962963` | `0.995556` | `21` |
| `balanced_accuracy` | `0.972003` | `0.015034` | `0.933064` | `0.993192` | `21` |
| `brier` | `0.016469` | `0.005059` | `0.007658` | `0.026464` | `21` |
| `f1_macro` | `0.97644` | `0.011357` | `0.949343` | `0.994137` | `21` |
| `pr_auc` | `0.983247` | `0.008996` | `0.957582` | `0.995446` | `21` |
| `roc_auc` | `0.991599` | `0.007823` | `0.959969` | `0.998012` | `21` |
| `runtime_seconds` | `18.485` | `None` | `None` | `26.469` | `None` |

- Completed seeds: `21`
- Failed seeds: `0`

## Boundaries

- Public-source benchmark only.
- No PHI.
- Not clinical decision support.
- No patient-level prediction claim.
- Sequence-family models are architecture benchmarks unless future work constructs true temporal tensors.
- Metrics are benchmark signals, not clinical-utility claims.

## Outputs

- `apps/web/src/data/deep_benchmark_overnight.json`
- `.run/overnight_core_dl/overnight_core_dl_final.json`
- `.run/overnight_core_dl/overnight_core_dl_events.jsonl`
