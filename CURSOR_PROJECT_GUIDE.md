# AI 輔助機器人開發平台：Cursor 開發執行手冊

> 18 個月碩士論文 / 開源平台進度清單 · NVIDIA / ROS 2 / Isaac / Cosmos 路線  
> 版本 0.2 · 2026-09-17 · 新增雙系統 Git/GitHub 協作與備份策略

## 0. 使用方式

這份文件同時是「研究進度表」與「Cursor 專案上下文」。每次開始新的開發階段前，先讓 Cursor 閱讀本文件，再只處理當前里程碑。不要讓 Cursor 任意更換 ROS distribution、系統 Python、模擬器版本或整體架構。

**目前狀態**

- [x] Ubuntu + Windows 10 雙系統已完成
- [x] Cursor 已可使用
- [x] 研究方向：AI 輔助 ROS 2 機器人整合、模板重用、自動除錯、3D 模擬驗證、Jetson 部署
- [ ] 確認 Ubuntu 版本是否為 24.04 LTS
- [ ] 確認 NVIDIA GPU / Driver / VRAM
- [ ] 安裝並驗證 ROS 2 Jazzy
- [ ] 建立研究 Git repository 並連接 GitHub `kim7170719`

**第一原則：Ubuntu 是正式研究環境；Windows 10 作為 Cursor、文件、Git 與一般輔助開發環境。**

**雙系統 Git 原則：Windows 與 Ubuntu 各自使用獨立 clone，不共用同一個 working tree；所有跨系統同步都經由 GitHub。**

GitHub 帳號：[`kim7170719（余建樂kim）`](https://github.com/kim7170719)

---

## 1. 研究目標與範圍

### 1.1 一句話目標

建立一個開源、模型無關（model-agnostic）、硬體感知（hardware-aware）的 AI 機器人開發平台，讓使用者以自然語言描述機器人需求後，系統可利用結構化硬體知識、ROS 2 套件與模板，自動產生與整合專案、建置、診斷錯誤、進入 Isaac Sim 驗證，最後部署到 NVIDIA Jetson 真機。

### 1.2 碩論核心 contribution

1. **Robot Integration Schema**：描述 Hardware → Driver → ROS Interface → Capability。
2. **AI Integration Agent**：需求解析、套件/模板選擇、配置產生與自動診斷。
3. **Simulation Validation Pipeline**：Build → Launch → ROS Graph / TF / Navigation → Isaac Sim 測試。
4. **Community Experience Registry**：保存已驗證配置、失敗案例與解法，供後續 AI 重用。

### 1.3 明確不做（MVP 階段）

- 不同時支援多個 ROS distribution。
- 不把 Windows 10 當正式 ROS / Isaac 部署平台。
- 不同時支援 Drone、Manipulator、Humanoid 等多種機器人。
- 不自行訓練大型 foundation model。
- 不讓 Cosmos 取代 Isaac Sim 的 deterministic physics simulation。
- 不在 M12 前花大量時間做華麗 GUI。

---

## 2. 技術基準（Reference Stack）

| 層 | 基準 | 用途 |
|---|---|---|
| 主 OS | Ubuntu 24.04 LTS | 正式研究 / ROS / Isaac |
| 輔助 OS | Windows 10 | Cursor、文獻、Git、文件 |
| IDE | Cursor | AI 輔助開發 |
| ROS | ROS 2 Jazzy | 機器人 middleware |
| Python | 系統 Python 3.12 系列 | ROS 2 Jazzy / 主應用 |
| Simulator | Isaac Sim | 3D Digital Twin / Physics |
| NVIDIA ROS | Isaac ROS | GPU 加速 perception / robotics |
| Navigation | Nav2 | 自主導航 |
| Control | ros2_control | 控制器與硬體抽象 |
| Agent Backend | Python + FastAPI | AI orchestration |
| Schema | Pydantic + YAML / JSON | 結構化需求與設備描述 |
| Registry | SQLite 起步 | Hardware / Package / Experience |
| Container | Docker | Cosmos / 可重現環境 |
| Physical AI | Cosmos（後期） | scenario / reasoning / Physical AI |
| Deployment | Jetson Orin / Thor | 真機 edge deployment |
| 第一台 Robot | Differential Drive | 控制研究範圍 |

### 2.1 版本管理原則

- 安裝前以官方文件重新確認版本，不因 Cursor 建議任意升級/降級。
- ROS system Python 不隨意用 pip 污染。
- AI backend 與需要特殊 Python 版本的 Cosmos 優先使用獨立 venv / Conda / Docker。
- 每次升級關鍵版本都記錄於 `docs/decisions/`。

---

## 3. 建議 Repository 結構

```text
robot-dev-ai/
├── .gitattributes
├── .gitignore
├── .cursor/
│   └── rules/
│       └── robotics.mdc
├── docs/
│   ├── PROJECT_CONTEXT.md
│   ├── environment.md
│   ├── git_workflow.md
│   ├── progress.md
│   └── decisions/
├── ros_ws/
│   └── src/
├── agent/
│   ├── planner/
│   ├── tools/
│   ├── prompts/
│   └── schemas/
├── registry/
│   ├── hardware/
│   ├── packages/
│   ├── capabilities/
│   └── compatibility/
├── templates/
│   ├── differential_drive/
│   ├── lidar/
│   ├── camera/
│   ├── nav2/
│   └── isaac_ros/
├── simulator/
│   ├── worlds/
│   ├── scenarios/
│   └── evaluator/
├── validator/
│   ├── build/
│   ├── ros_graph/
│   ├── tf/
│   ├── topics/
│   └── navigation/
├── experiments/
├── docker/
├── scripts/
├── tests/
└── README.md
```

---

## 4. Cursor 專案規則

建議把以下內容放入 `.cursor/rules/robotics.mdc`：

```text
Project baseline:
- Ubuntu 24.04 LTS
- ROS 2 Jazzy
- Python 3.12 series
- Isaac Sim as primary 3D physics simulator
- Isaac ROS for NVIDIA-accelerated ROS workloads
- Differential-drive robot as MVP target

Development rules:
1. Do not change ROS distribution without an explicit architecture decision.
2. Do not replace or globally downgrade system Python.
3. Prefer APIs and packages compatible with ROS 2 Jazzy.
4. Prefer official ROS/NVIDIA documentation for version-sensitive instructions.
5. Before editing code, explain which files will change and why.
6. Make the smallest change that satisfies the current milestone.
7. Never hide build/test failures. Report the exact command and error summary.
8. Every generated ROS package must declare dependencies correctly.
9. Keep hardware-dependent code behind clear interfaces.
10. Simulation validation must happen before real-hardware deployment.
11. Do not add a new framework/library if the existing stack can solve the task.
12. Record architecture/version decisions in docs/decisions/.
13. Add or update tests when behavior changes.
14. After finishing a task, update docs/progress.md.
15. Never claim a milestone is complete unless its acceptance criteria pass.
16. Before editing, report `git status` and current branch.
17. Never develop directly on `main`; use a task branch.
18. Never force-push `main` or `develop`.
19. Never commit secrets, `.env`, model credentials, build/install/log outputs, or large generated assets.
20. When switching between Ubuntu and Windows, commit and push first; the other OS must fetch/pull before editing.
21. Update `docs/progress.md` and reference the related issue/milestone in meaningful commits.
```

---

## 5. Day 0 → Week 1：環境基線

### 5.1 系統盤點

在 Ubuntu 執行並把結果保存至 `docs/environment.md`：

```bash
lsb_release -a
uname -m
python3 --version
nvidia-smi
lspci | grep -i nvidia
free -h
df -h
git --version
```

### 5.2 Checklist

- [x] Ubuntu / Windows 10 雙系統可啟動
- [x] Cursor 可使用
- [ ] Ubuntu = 24.04 LTS（若不是，先決定是否調整）
- [ ] `nvidia-smi` 正常
- [ ] 記錄 GPU 型號 / VRAM / Driver
- [ ] 記錄 RAM / SSD 剩餘空間
- [ ] Git 正常
- [ ] 建立 `robot-dev-ai` repository（GitHub owner：`kim7170719`）
- [ ] 建立上述目錄
- [ ] 建立 `.gitignore`
- [ ] 建立 `.gitattributes`，固定跨 Windows/Linux 行尾規則
- [ ] Windows 與 Ubuntu 各自 clone repository，不共用 working tree
- [ ] 兩個 OS 各自設定 Git identity / authentication
- [ ] 建立 `docs/environment.md`
- [ ] 建立 `docs/progress.md`
- [ ] 建立 Cursor rules
- [ ] Windows / Ubuntu 各自 clone repository
- [ ] 設定兩邊 GitHub SSH/HTTPS authentication
- [ ] 完成雙系統往返 commit/push/pull 測試
- [ ] 完成第一次 commit / push
- [ ] 完成 Ubuntu → GitHub → Windows → GitHub → Ubuntu 的跨系統同步測試

### 5.3 Gate 0 驗收

- Ubuntu 版本、GPU、Python、磁碟空間都有明確紀錄。
- Repository 可正常 commit / push。
- Ubuntu 與 Windows 各自有獨立 clone，跨系統往返同步測試成功且內容一致。
- Cursor 能讀本文件與專案規則。

---

## 6. 18 個月總進度表

| 月份 | 核心工作 | 必須產出 | Gate |
|---|---|---|---|
| M0 | Environment Audit | environment.md / repo | G0 |
| M1 | ROS 2 Jazzy 基礎 | 自建 ROS package | G1 |
| M2 | URDF + ros2_control | Diff-drive 控制 | G2 |
| M3 | Isaac Sim | Digital Twin + ROS bridge | G3 |
| M4 | Nav2 | 模擬自主導航 | G4 |
| M5 | Isaac ROS | GPU robotics baseline | G5 |
| M6 | Proposal | 研究問題 / 架構 / 評估方法 | G6 |
| M7 | Robot Knowledge Schema | Hardware / capability schema | G7 |
| M8 | Template Engine | 模板產生 ROS project | G8 |
| M9 | AI Requirement Agent | NL → structured robot spec | G9 |
| M10 | Compatibility Resolver | hardware/software reasoning | G10 |
| M11 | Auto Debug Agent | build / ROS diagnosis loop | G11 |
| **M12** | **完整 MVP** | **Prompt → Simulation PASS/FAIL** | **G12** |
| M13 | Cosmos integration | scenario / physical reasoning | G13 |
| M14 | Jetson deployment | PC → Jetson pipeline | G14 |
| M15 | Real Robot | 真機驗證 | G15 |
| M16 | Experiments | baseline / ablation / metrics | G16 |
| M17 | Thesis | 完整初稿 | G17 |
| M18 | Release | v1.0 / docs / 口試 | G18 |

> **硬性原則：M12 完成 MVP；M13 之後不再大幅擴張平台核心範圍。**

---

## 7. Phase A — 基礎能力（M1–M5）

### M1：ROS 2 Jazzy

**學習 / 實作**

- [ ] 安裝 ROS 2 Jazzy
- [ ] 建立 workspace
- [ ] `colcon build`
- [ ] Publisher / Subscriber
- [ ] Service
- [ ] Action
- [ ] Parameter
- [ ] Launch
- [ ] TF2
- [ ] RViz2
- [ ] 自建 `sensor_node → planner_node → controller_node`

**Gate G1**

- [ ] 可從乾淨 terminal source ROS / workspace
- [ ] 自建 package 可 build
- [ ] Launch 一次啟動多 node
- [ ] 能用 CLI 檢查 topic / node / service / action

### M2：URDF + ros2_control

- [ ] 建立 `simple_diff_robot`
- [ ] base / wheel / lidar / camera links
- [ ] Xacro
- [ ] collision / inertia
- [ ] robot_state_publisher
- [ ] joint_state_broadcaster
- [ ] diff_drive_controller
- [ ] `/cmd_vel`
- [ ] `/odom`

**Gate G2**

- [ ] RViz 可正確顯示 robot / TF
- [ ] 控制命令可使模擬底盤前進 / 後退 / 轉向

### M3：Isaac Sim

- [ ] 安裝 / 驗證 Isaac Sim
- [ ] 開啟基本 scene
- [ ] Import URDF
- [ ] 產生 / 保存 USD
- [ ] Physics / collision
- [ ] Camera
- [ ] LiDAR
- [ ] ROS 2 Bridge
- [ ] `/cmd_vel`
- [ ] `/odom`
- [ ] `/scan`
- [ ] `/camera`

**Gate G3**

- [ ] ROS `/cmd_vel` 可以控制 Isaac Sim robot
- [ ] Isaac Sim sensor data 可進 ROS 2

### M4：Nav2

- [ ] SLAM / map
- [ ] AMCL / localization
- [ ] Nav2 planner / controller
- [ ] global / local costmap
- [ ] goal navigation
- [ ] obstacle avoidance

**Gate G4**

- [ ] 在 Isaac Sim 給定 navigation goal，robot 可自主到達並避障

### M5：Isaac ROS

- [ ] 建立 Isaac ROS 開發 container
- [ ] Image pipeline baseline
- [ ] Object detection baseline
- [ ] Visual SLAM baseline
- [ ] 記錄 CPU generic ROS 與 NVIDIA accelerated pipeline 的介面差異

**Gate G5**

- [ ] 至少一個 Isaac ROS pipeline 可穩定重現
- [ ] 建立 `docs/isaac_ros_baseline.md`

---

## 8. Phase B — 研究核心（M6–M12）

### M6：Proposal

- [ ] Problem statement
- [ ] Related work
- [ ] Research gap
- [ ] System architecture
- [ ] Research questions
- [ ] Metrics
- [ ] Baseline groups
- [ ] MVP scope freeze

**建議研究問題**

- RQ1：AI + verified templates 是否降低 integration time？
- RQ2：simulation-in-the-loop validation 是否提升整合成功率？
- RQ3：experience registry 增長時，是否降低人工介入與 AI iteration？

### M7：Robot Knowledge Schema

第一版只使用 YAML/JSON + Pydantic + SQLite。

- [ ] Hardware schema
- [ ] Driver schema
- [ ] ROS interface schema
- [ ] Capability schema
- [ ] Package schema
- [ ] Compatibility relation
- [ ] Validation status
- [ ] Known issue / solution

**核心關係**

```text
Hardware → Driver → ROS Interface → Capability → Package / Template
```

### M8：Template Engine

- [ ] differential-drive template
- [ ] LiDAR template
- [ ] Camera template
- [ ] Nav2 config template
- [ ] Isaac ROS pipeline template
- [ ] launch template
- [ ] YAML config template
- [ ] package metadata template

**Gate G8**

給定 structured spec，可以不經 LLM，穩定產生可 build 的專案骨架。

### M9：AI Requirement Agent

流程：

```text
Natural Language
→ LLM
→ Structured Specification
→ Pydantic Validation
→ Planner
```

- [ ] 定義 robot specification JSON schema
- [ ] LLM provider abstraction
- [ ] structured output
- [ ] validation / retry
- [ ] requirement ambiguity handling
- [ ] provenance：記錄哪些欄位由 user / template / AI 產生

### M10：Compatibility Resolver

- [ ] capability requirements
- [ ] message type compatibility
- [ ] ROS distro compatibility
- [ ] target platform compatibility
- [ ] required conversion node
- [ ] dependency reasoning
- [ ] explainable resolution output

**重要原則**：Resolver 先依結構化規則 / registry 推理，LLM 用於補充規劃與說明，而不是讓 LLM 完全猜相容性。

### M11：Auto Debug Agent

Agent tools 第一版：

```text
build_workspace()
inspect_nodes()
inspect_topics()
inspect_services()
inspect_actions()
inspect_parameters()
inspect_tf()
inspect_controllers()
launch_robot()
stop_robot()
read_build_error()
run_validation()
```

循環：

```text
Generate → Build → Observe → Diagnose → Patch → Rebuild → Validate
```

- [ ] Build error parser
- [ ] launch failure parser
- [ ] ROS graph snapshot
- [ ] TF validator
- [ ] topic/type validator
- [ ] controller validator
- [ ] 修改前 diff
- [ ] 最大修復迭代次數
- [ ] failure report

### M12：MVP Freeze

使用者輸入：

> 我要建立一台 NVIDIA 差速機器車，LiDAR + Camera，能自主導航。

平台必須完成：

- [ ] requirement parsing
- [ ] structured spec
- [ ] hardware / package lookup
- [ ] compatibility resolution
- [ ] template generation
- [ ] ROS workspace generation
- [ ] `colcon build`
- [ ] launch
- [ ] Isaac Sim start
- [ ] ROS graph validation
- [ ] TF validation
- [ ] navigation scenario
- [ ] PASS / FAIL report
- [ ] 至少一次可重現自動修復案例

**Gate G12：這一關沒過，不進 Cosmos / GUI 擴充。**

---

## 9. Phase C — 延伸、真機與論文（M13–M18）

### M13：Cosmos

定位：**Physical AI / scenario / reasoning，不取代 Isaac Sim physics。**

- [ ] Cosmos 獨立 container / env
- [ ] 最小官方範例復現
- [ ] scenario generation 或 physical reasoning 選一項
- [ ] 與 simulation validator 定義清楚接口
- [ ] Cosmos 不可用時，核心 MVP 仍可運行

### M14：Jetson Deployment

- [ ] 選定 Orin 或 Thor 為 primary target
- [ ] JetPack / Isaac ROS baseline
- [ ] container / package deployment
- [ ] camera / LiDAR bring-up
- [ ] PC simulation 與 Jetson ROS interface 對齊
- [ ] deployment manifest

### M15：Real Robot

- [ ] Navigation
- [ ] Obstacle avoidance
- [ ] Camera perception
- [ ] LiDAR replacement test
- [ ] simulation → real interface consistency
- [ ] safety / stop mechanism（真機測試必須有人監督）

### M16：Experiments

三組 baseline：

- A：Manual ROS development
- B：Cursor / Generic LLM coding
- C：本研究平台

至少量測：

- Development Time
- Integration Time
- Build Failure Count
- Configuration Error Count
- Human Intervention Count
- LLM Iterations
- Simulation Success Rate
- Deployment Success Rate
- Experience Reuse Rate

### M17：Thesis

- [ ] Introduction
- [ ] Related Work
- [ ] System Architecture
- [ ] Knowledge Representation
- [ ] AI Integration Agent
- [ ] Simulation Validation
- [ ] Implementation
- [ ] Experiments
- [ ] Discussion
- [ ] Conclusion

**本月禁止大型新功能，只允許 bug fix、實驗、圖表與論文。**

### M18：Open-source Release

- [ ] README
- [ ] Installation guide
- [ ] Architecture docs
- [ ] CONTRIBUTING
- [ ] Hardware schema guide
- [ ] Template guide
- [ ] API docs
- [ ] Example robot
- [ ] Demo video
- [ ] Reproducible experiment instructions
- [ ] License
- [ ] Release `v1.0.0`

---

## 10. 每週工作節奏

### 週一：定義本週唯一主要里程碑

在 `docs/progress.md` 寫：

```text
Week XX Goal:

Acceptance criteria:
1.
2.
3.

Out of scope:
-
-
```

### 開發循環

```text
Issue
→ Cursor 讀 context
→ Cursor 提出最小修改計畫
→ 人工確認架構方向
→ 寫 code
→ Build / Test
→ 記錄錯誤
→ 修正
→ Gate 驗收
→ Commit
→ 更新 progress.md
```

### 每週五輸出

- [ ] 本週完成項目
- [ ] 可重現 command
- [ ] 未解問題
- [ ] 關鍵錯誤與解法
- [ ] 下週目標
- [ ] Git commit / tag

---

## 11. Definition of Done（DoD）

不要以「Cursor 說完成了」作為完成標準。

一個功能只有同時滿足以下條件才算完成：

- [ ] 有清楚 requirement
- [ ] Code 已 commit
- [ ] Build 通過
- [ ] Test / validation 通過
- [ ] 可從乾淨 terminal 重現
- [ ] command 寫進文件
- [ ] 依賴版本有紀錄
- [ ] 錯誤情況有合理 failure message
- [ ] 沒有留下無說明 temporary hack
- [ ] `docs/progress.md` 已更新

---

## 12. Cursor 工作 Prompt 模板

### 12.1 開始新任務

```text
先閱讀：
1. docs/PROJECT_CONTEXT.md
2. CURSOR_PROJECT_GUIDE.md
3. docs/progress.md
4. .cursor/rules/robotics.mdc

目前只處理這個任務：<TASK>

請先不要修改程式。
先回覆：
- 你理解的目標
- 會影響哪些檔案
- 目前 architecture 中應該放在哪一層
- 最小實作方案
- 驗收方法
- 可能風險

不得更換 ROS distribution、Python 主版本或核心框架。
```

### 12.2 要 Cursor 實作

```text
依照剛才的最小方案實作。
限制：
- 一次只處理目前任務
- 不重構無關程式
- 不新增非必要 dependency
- 保持 ROS 2 Jazzy 相容
- 修改完成後列出 changed files
- 提供 build/test commands
- 若測試失敗，保留錯誤資訊，不要假裝成功
```

### 12.3 Debug

```text
這是目前完整錯誤輸出：
<ERROR>

請依序：
1. 區分 build / dependency / runtime / ROS graph / TF / config / hardware 類問題。
2. 指出最可能 root cause 與證據。
3. 先提出最小修正，不要一次改很多地方。
4. 告訴我要執行什麼 command 驗證。
5. 如果資訊不足，指定需要的 diagnostic command，而不是猜。
```

### 12.4 Code Review

```text
請 review 目前 diff，重點檢查：
- ROS 2 Jazzy compatibility
- package.xml / dependency declaration
- node / topic / service / action interface
- error handling
- hardware coupling
- testability
- 是否破壞既有 architecture
- 是否有 Cursor/LLM 猜測但未驗證的設定

只列出有實際證據的問題，依嚴重程度排序。
```

### 12.5 完成里程碑

```text
不要直接宣告完成。
請依 CURSOR_PROJECT_GUIDE.md 中目前 Gate 的 acceptance criteria 逐項核對。
每項輸出 PASS / FAIL / NOT TESTED，並附驗證 command 或 evidence。
最後只在全部必要項目 PASS 時才建議關閉 issue。
```

---

## 13. Git / GitHub / Issue 規範：雙系統開發、版本、備份與合併

### 13.1 GitHub 身份與 Repository

- GitHub：[`kim7170719（余建樂kim）`](https://github.com/kim7170719)
- 建議主要 repository：`robot-dev-ai`
- 建議遠端：`origin`
- Repository 建立後，SSH URL 預期為：`git@github.com:kim7170719/robot-dev-ai.git`
- Git 的 `user.name` 建議設為 `余建樂kim`；`user.email` 請使用你在 GitHub 已驗證的 email 或 GitHub noreply email，不要在文件內硬編碼私人 email。

> GitHub account 名稱和 `git config user.name` 不是同一件事。真正辨識 commit 身份的是 commit 內的 name/email；GitHub 會依已驗證 email 關聯帳號。

### 13.2 Windows / Ubuntu 必須各自獨立 clone

不要把 repository 放在 Windows/Ubuntu 共用 NTFS 分割區後，讓兩個 OS 共用同一個 `.git` / working tree。ROS、Linux executable bit、symlink、大小寫與 CRLF/LF 都可能造成不必要的差異。

建議：

```text
Ubuntu:  ~/dev/robot-dev-ai
Windows: C:\dev\robot-dev-ai
                     │
                     └── GitHub origin 作為唯一同步中心
```

**跨系統規則：**

1. 在目前 OS 停止工作前，先 `git status`。
2. 有有效修改就 commit；若只是未完成但必須切 OS，可用 `wip:` commit，之後在合併前 squash。
3. `git push` 到目前 task branch。
4. 切換 OS 後先 `git fetch --prune`。
5. `git switch <same-branch>`。
6. `git pull --ff-only`。
7. `git status` 必須乾淨後才開始新的修改。

**不要依賴 `git stash` 來跨 OS。** stash 只存在該 clone，本身不會同步到另一套系統。

### 13.3 第一次 Git 設定

Ubuntu 與 Windows 都各自設定一次：

```bash
git config --global user.name "余建樂kim"
git config --global user.email "<your verified GitHub email or noreply email>"
git config --global pull.ff only
git config --global fetch.prune true
git config --global init.defaultBranch main
```

行尾由 repository 的 `.gitattributes` 控制，因此建議不要靠 OS 自動改寫：

```bash
git config --global core.autocrlf false
```

認證建議每套 OS 使用各自的 SSH key，兩把 key 都加入同一個 GitHub `kim7170719` 帳號。不要把 private key 跨 OS 複製或 commit 進 repository。

### 13.4 Branch 策略

分支按照「工作內容」分，不按照 Windows / Ubuntu 永久分流：

```text
main                         # 穩定、可重現、可發布
└── develop                  # 日常整合分支
    ├── feature/m1-ros-baseline
    ├── feature/isaac-sim-bridge
    ├── feature/robot-schema
    ├── feature/template-engine
    ├── feature/compatibility-resolver
    ├── fix/tf-odom-transform
    ├── experiment/lidar-swap
    └── docs/thesis-methodology
```

**合併方向：**

```text
feature / fix / experiment
          ↓ Pull Request
       develop
          ↓ Gate / Milestone PASS
       main
          ↓
        Tag / Release
```

規則：

- `main`：只放通過 Gate 的版本，不直接開發。
- `develop`：整合已完成的 task branch。
- `feature/*`：新功能。
- `fix/*`：修正 bug。
- `experiment/*`：論文實驗、替代方案；未必全部合入產品核心。
- `docs/*`：大型文件或論文章節修改。
- 不建立長期 `windows` / `ubuntu` 分支；OS 只是執行環境，不是功能版本。
- 已推送且多人使用的共享分支不要 rebase 改寫歷史；自己的私人 feature branch 可在 PR 前整理/squash。

### 13.5 每個任務標準 Git Flow

開始任務：

```bash
git switch develop
git pull --ff-only
git switch -c feature/m1-ros-baseline
```

開發中：

```bash
git status
git add <files>
git commit -m "feat: add ROS 2 baseline package"
git push -u origin feature/m1-ros-baseline
```

合併前同步 develop：

```bash
git fetch origin
git switch feature/m1-ros-baseline
git merge origin/develop
# resolve conflicts, then run tests again
git push
```

接著建立 Pull Request：`feature/... → develop`。Gate 通過後再建立 `develop → main` 的 milestone PR。

### 13.6 雙系統切換 SOP

**Ubuntu → Windows：**

```bash
git status
git add <files>
git commit -m "wip: checkpoint before switching to Windows"   # 只有必要時
git push
```

Windows 開始工作：

```powershell
git fetch --prune
git switch <current-task-branch>
git pull --ff-only
git status
```

Windows → Ubuntu 同理。若 `git pull --ff-only` 失敗，**先停止修改並確認兩邊是否都有不同 commit，不要直接 force push。**

### 13.7 `.gitattributes`：避免雙系統行尾污染

Repository root 建立：

```gitattributes
* text=auto
*.sh text eol=lf
*.py text eol=lf
*.yaml text eol=lf
*.yml text eol=lf
*.xml text eol=lf
*.urdf text eol=lf
*.xacro text eol=lf
*.md text eol=lf
*.json text eol=lf
*.bat text eol=crlf
*.cmd text eol=crlf
*.ps1 text eol=crlf
```

ROS/Linux 執行腳本一律 LF。建立 `.gitattributes` 後若既有檔案行尾很亂，可在獨立 housekeeping commit 做一次 renormalize，不要和功能修改混在同一 commit。

### 13.8 `.gitignore` 基線

至少忽略：

```gitignore
# ROS/colcon
ros_ws/build/
ros_ws/install/
ros_ws/log/

# Python
.venv/
venv/
__pycache__/
*.pyc

# Secrets / local config
.env
.env.*
!.env.example

# IDE / OS
.vscode/
.idea/
.DS_Store
Thumbs.db

# Logs / caches
*.log
.cache/

# Experiment generated data
experiments/tmp/
```

大型模型、dataset、rosbag、Isaac cache、生成影片不要直接塞進普通 Git。需要版本化的大型二進位檔才評估 Git LFS；模型權重與可重新下載的資源優先以 manifest / download script 記錄來源與 checksum。

### 13.9 Commit 規範

建議 Conventional Commits：

```text
feat: add differential drive template
fix: correct odom to base_link transform
refactor: separate registry interface from sqlite backend
test: add nav2 validation scenario
docs: record Isaac ROS environment baseline
exp: add lidar replacement experiment
chore: update development tooling
wip: checkpoint before OS switch
```

一個 commit 只處理一個邏輯變更。不要用 `update`, `new`, `fix stuff` 這類無法追蹤的訊息。

### 13.10 版本與 checkpoint

Git branch 是開發線；**Tag / Release 才是論文里程碑版本標記**。

建議：

```text
g0-environment-baseline
m1-g1-ros-baseline
m3-g3-isaac-sim
m6-proposal-freeze
m12-mvp-v0.1.0
m15-real-robot
v1.0.0-thesis-release
```

建立 annotated tag：

```bash
git tag -a m1-g1-ros-baseline -m "Gate G1 passed: ROS 2 baseline"
git push origin m1-g1-ros-baseline
```

### 13.11 Git 不等於唯一備份：三層備份

建議至少保留：

```text
Layer 1  Windows clone
Layer 2  Ubuntu clone
Layer 3  GitHub origin
```

對重要 Gate / 論文提交點，再增加離線快照：

```bash
mkdir -p backups
git bundle create backups/robot-dev-ai-YYYYMMDD.bundle --all
```

`.bundle` 應存到 repository **外部**的另一顆磁碟/加密備份位置，不要再 commit 回同一個 repository。後期若專案價值提高，可增加第二個 remote mirror（例如另一個 Git hosting 或實驗室 server）。

### 13.12 Merge / Conflict 原則

遇到 conflict：

1. `git status` 看衝突檔案。
2. 理解兩邊修改意圖後再解，不要讓 Cursor 盲目「Accept All Current/Incoming」。
3. ROS config、URDF/Xacro、YAML、launch file 解衝突後必須重新 build/test。
4. 執行對應 Gate 的 acceptance command。
5. 再 commit merge resolution。
6. 禁止用 `git push --force` 解決 main/develop 問題。

Cursor 可以協助分析 conflict，但必須先顯示：衝突區塊、兩邊意圖、預計保留內容與測試方式。

### 13.13 Issue / Pull Request 必須包含

Issue：

- Problem
- Expected result
- Acceptance criteria
- Reproduction command
- Environment
- Logs / screenshots（需要時）
- Related milestone / Gate
- Target branch

Pull Request：

- What changed
- Why
- Related Issue
- Test / build commands
- Actual result
- Affected ROS/Isaac/Jetson environment
- Risk / rollback notes
- Checklist：文件是否更新、測試是否通過、是否包含秘密或大型生成檔

### 13.14 Gate 0 新增：跨系統 Git 驗收

Gate 0 除了環境盤點外，必須完成以下實測：

```text
Ubuntu clone
  ↓ modify docs/environment.md
commit + push
  ↓
GitHub
  ↓
Windows clone pull
  ↓ modify docs/progress.md
commit + push
  ↓
GitHub
  ↓
Ubuntu pull
```

**驗收條件：**

- [ ] Windows / Ubuntu 都能正確認證 GitHub。
- [ ] 兩邊為不同 working tree / clone。
- [ ] 雙向 commit / push / pull 成功。
- [ ] `git status` 最後兩邊皆 clean。
- [ ] 同一檔案沒有因 CRLF/LF 產生整份假變更。
- [ ] 能建立 task branch → push → merge/PR → pull 回兩個 OS。
- [ ] 建立第一個 milestone tag。

---

## 14. 論文實驗從第一天就開始留資料

不要等 M16 才想「要量什麼」。每次任務至少記錄：

```text
task_id
start_time
end_time
method = manual / cursor / platform
build_failures
runtime_failures
human_interventions
llm_iterations
final_status
notes
```

建議把原始紀錄放：

```text
experiments/raw/
```

分析結果放：

```text
experiments/results/
```

---

## 15. 當前立即執行清單

### 現在（Day 0）

- [ ] 執行系統盤點 commands
- [ ] 建立 `docs/environment.md`
- [ ] 確認 Ubuntu 版本
- [ ] 確認 NVIDIA GPU / VRAM / Driver
- [ ] 建立 GitHub repository `kim7170719/robot-dev-ai`
- [ ] Windows / Ubuntu 各自 clone repository，不共用 working tree
- [ ] 兩套 OS 各自完成 GitHub SSH/HTTPS 認證
- [ ] 建立 `.gitattributes` 並驗證 CRLF/LF 不造成假變更
- [ ] 完成 Ubuntu → GitHub → Windows → GitHub → Ubuntu 往返同步
- [ ] 建立 Gate 0 milestone tag：`g0-environment-baseline`
- [ ] 建立專案目錄
- [ ] 加入本 `CURSOR_PROJECT_GUIDE.md`
- [ ] 建立 `.cursor/rules/robotics.mdc`
- [ ] 建立 `docs/progress.md`
- [ ] commit：`docs: initialize research development baseline`

### 下一步（Gate 0 通過後）

**只做 ROS 2 Jazzy M1，不先碰 Cosmos。**

第一個 issue：

```text
M1-01: Install and verify ROS 2 Jazzy on Ubuntu 24.04
```

Acceptance criteria：

- `ros2 --help` 正常
- `source /opt/ros/jazzy/setup.bash` 正常
- turtlesim 可啟動
- workspace 可 `colcon build`
- 建立第一個自有 package
- 紀錄完整安裝與驗證 command

---

## 16. 官方參考來源（版本敏感，安裝前重查）

- ROS 2 Jazzy 官方文件：https://docs.ros.org/en/jazzy/
- Isaac Sim ROS 2 Installation：https://docs.isaacsim.omniverse.nvidia.com/latest/installation/install_ros.html
- Isaac ROS Getting Started：https://nvidia-isaac-ros.github.io/getting_started/index.html
- NVIDIA Cosmos Prerequisites：https://docs.nvidia.com/cosmos/latest/prerequisites.html

**截至本文件版本，NVIDIA Isaac Sim 官方文件推薦 Ubuntu 24.04 + ROS 2 Jazzy；Isaac ROS 官方亦以 ROS 2 Jazzy 為主要測試組合。版本會變動，因此真正安裝前必須重新查官方文件。**

---

## 17. 最後的範圍控制

當你不知道「這功能現在要不要做」時，使用以下判斷：

1. 它是否直接幫助 G12 MVP？
2. 它是否能形成論文可量化 contribution？
3. 它是否能在 Isaac Sim 或真機被驗證？
4. 它是否能產生可重現的實驗資料？

若四題大多數為「否」，先放入 Backlog，不做。

**最重要的路徑：ROS 2 → Robot model/control → Isaac Sim → Nav2/Isaac ROS → Knowledge/Template → AI Agent → Auto Debug → MVP → Cosmos → Jetson → 真機 → 實驗 → 論文。**
