# 🎨 ComfyUI Dual-Track Agent Edition

[![GitHub License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-Core%20v0.3+-success.svg)](https://github.com/comfyanonymous/ComfyUI)
[![AMD ZLUDA Verified](https://img.shields.io/badge/AMD%20ZLUDA-Radeon%20780M%20Passed-orange.svg)](docs/HARDWARE_CONFIG_ZLUDA_AMD.md)
[![Agent Ready](https://img.shields.io/badge/Agent-Autonomous%20Contract-purple.svg)](AGENT_GUIDE.md)
[![Turnkey Setup](https://img.shields.io/badge/Setup-One--Click%20Deploy-brightgreen.svg)](docs/EDITION_SETUP_GUIDE.md)

工业级 ComfyUI 双轨自动化工作流矩阵、硬件级调优套件与大模型智能体调度方案。  
**本仓库是此专版 ComfyUI 的唯一权威源**：未来在任何全新电脑、重装系统或已有环境中，均可通过本仓库在数分钟内一键配置或复刻出 100% 相同标准的专版 ComfyUI。

---

## 🌟 核心特色与设计哲学

- 🎯 **质量绝对优先 (Quality-First Invariant)**：
  - 彻底淘汰粗制滥造的 8 步直接出图，根除塑料蜡像假面与结构融化；
  - 移除了诱发高频重影与色散的 `FreeU_V2` 频域算子；
  - 彻底解耦真人写实 LoRA 与 2D 二次元底模，解决“油画模糊涂抹”痛点，实现纯净锐利的赛璐珞硬线稿与工业三视图。
- ⚡ **标准化双轨拓扑 (Dual-Track Architecture)**：
  - **默认交付主链路 `[MODE:QUALITY]`**：26~28 步全精度 DPM++ 2M Karras + 1.35x~1.5x 潜空间放大 + 14~15 步高分微雕重绘（Denoise 0.44~0.52）-> `[OUTPUT:QUALITY]`；
  - **旁路极速预览链路 `[MODE:PREVIEW]`**：8 步轻量 Hyper-SD 旁路分支，专供 LLM Agent 进行秒级粗览构图与灵感探索；
  - **全体系唯一保留极速盲盒流**：`04_极速抽卡_无限多风格探索流`，兼顾秒级大批量抽卡。
- 🚀 **跨机器一键配置 (Turnkey Setup & Deploy)**：
  - 提供自动化脚本 `scripts/setup_edition.ps1` 与 `scripts/download_models.ps1`；
  - 现有 ComfyUI / 秋叶整合包 10 秒升级为专版，全新机器从零快速拉起。
- 🖥️ **深度适配 AMD APU (Radeon 780M / gfx1103) + ZLUDA**：
  - 独家调优的 Windows 11 + ZLUDA + ROCm 5.7 纯静默后台守护脚本；
  - `--cpu-vae` 与 `--reserve-vram 0.9` 显存保命配置，让轻薄本/迷你主机以 ~4.2s/it 稳定连续生图不黑屏、不崩溃；
  - 解决 LayerNorm 引起的 `0xC0000005` 驱动崩溃。
- 🤖 **Agent 机器可读调度契约 (`AGENT_GUIDE.md`)**：
  - 详尽的 Node ID 映射字典、REST API 队列控制协议与自愈防爆指南，支持外部智能体（Claude, GPT, Antigravity, OpenCode）100% 自主闭环调用。

---

## 📑 17 套工业级双轨工作流矩阵

所有工作流均通过解剖结构（30%）、面部五官（30%）、材质纹理（20%）、锐度纯净度（20%）四维量化质检，**质检均分高达 95.3 / 100**。

| 序号 | 工作流名称 | 核心风格定位 | 推荐底模 | 采样策略 | 4D 质检评分 |
| :---: | :--- | :--- | :--- | :--- | :---: |
| **01** | `01_真人写实_极致NanoBanana_次表面透析_电影双段精雕流` | 电影级胶片质感、真实皮肤毛孔、耳廓逆光次表面红润透光 | Realistic Vision V6.0 B1 | 26步 DPM++ + 1.35x微雕 14步 | **94 / 100** |
| **02** | `02_抓拍视角_MOSS灵感_业余POV画中画_多档切换胶片流` | 业余手持手机抓拍视角、新娘微笑、婚纱缎面与闪光灯暗角 | Realistic Vision V6.0 B1 | 26步 DPM++ + 1.35x微雕 14步 | **95 / 100** |
| **03** | `03_智能工具_NSFW精准提示词反推工作台_中英对照融合` | WD14 深度反推 + 双轨中英对照表 + 结构化提示词重构 | 无需生图底模 | 纯图像特征提取 (免 KSampler) | **拓扑达标** |
| **04** | `04_极速抽卡_无限多风格探索流_秒级盲盒` | **全体系唯一保留的极速抽卡流**，轻量盲盒随机探索 | Anything V5 | 8步 Hyper-SD (秒级极速) | **官方保留** |
| **05** | `05_二次元总控_全能风格切换总控台_吉卜力_新海诚_暗黑` | 3 路 LoRA 切换矩阵，吉卜力/新海诚/暗黑自由组合 | Anything V5 | 26步 DPM++ + 1.35x微雕 14步 | **继承达标** |
| **06** | `06_二次元手绘_吉卜力唯美手绘风_童话治愈流` | 宫崎骏/男鹿和雄水彩质感、蓝天白云绿茵草坡与治愈倒影 | Anything V5 | 26步 DPM++ + 1.35x微雕 14步 | **95 / 100** |
| **07** | `07_二次元光影_新海诚光影日漫_双轨纯欲流` | 暮色霞光与彗星尾迹、东京夜景灯火、纯欲少女利落线稿 | Anything V5 | 26步 DPM++ + 1.35x微雕 14步 | **95 / 100** |
| **08** | `08_二次元暗黑_暗黑异界深渊_触手侵蚀流` | 星云发光紫眸、恶魔小虎牙与胸前深V哥特蕾丝刺绣 | Anything V5 | 26步 DPM++ + 1.35x微雕 14步 | **93 / 100** |
| **09** | `09_2D精细厚涂_圣职修女与地牢囚徒_禁断反差专精流` | 哥特厚涂笔触、金边十字架刺绣、半透明黑丝暗纹与彩绘玻璃 | Anything V5 | 26步 DPM++ + 1.35x微雕 14步 | **95 / 100** |
| **10** | `10_2D精细厚涂_4大经典主题快速切换总控台` | 4 大魔幻主题（地牢祭坛/世界之树/女武神/废土机甲） | Anything V5 | 26步 DPM++ + 1.35x微雕 14步 | **96 / 100** |
| **11** | `11_2D精细厚涂_开放式材质强化与反推沙箱` | 重装巴洛克金雕板甲、镜面精钢、紫晶星瞳与半透明白丝披风 | Anything V5 | 26步 DPM++ + 1.35x微雕 14步 | **97 / 100** |
| **12** | `12_BetterWaifu_五阶LoRA矩阵与动态姿态总控台` | 赛璐珞硬线稿二次元机甲少女，彻底杜绝油画模糊 | Anything V5 | 26步 DPM++ + 1.35x微雕 14步 | **96 / 100** |
| **13** | `13_实用工具_局部重绘与垫图图生图修图流` | VAE 羽化遮罩（Feather 8）+ 局部修复高精融合 | 可自由切换 | 26步 DPM++ (Denoise 0.65) | **拓扑达标** |
| **14** | `14_精准控制_ControlNet姿态骨骼与线稿重绘流` | OpenPose 骨骼锁定 + Canny 线稿 1:1 姿态复刻 | 可自由切换 | 26步 DPM++ + 1.35x微雕 14步 | **拓扑达标** |
| **15** | `15_生活写实_日常阳光通勤与社交人像写真流` | 晨光街拍写真、毛线针织针脚微观纹理、真实笑颜与自然手指 | Realistic Vision V6.0 B1 | 26步 DPM++ + 1.35x微雕 14步 | **97 / 100** |
| **16** | `16_宽屏场景_16比9超清唯美风光与桌面壁纸流` | 896x512 宽幅直出、日照金山雪线与高山镜湖宏大景深 | Realistic / Anything | 26步 DPM++ + 1.35x微雕 14步 | **96 / 100** |
| **17** | `17_概念设计_全能设计图与角色三视图设定集` | 工业级角色设计三视图（正/侧/背）+ 5 组表情差分矩阵 | Anything V5 | 28步 DPM++ + 1.5x微雕 15步 | **94 / 100** |

---

## 🛠️ 以后如何通过 GitHub 配置专版 ComfyUI

详细步骤请参阅专版部署指南 [`docs/EDITION_SETUP_GUIDE.md`](docs/EDITION_SETUP_GUIDE.md)。

### 场景 1：在已有 ComfyUI（如秋叶整合包或独立版）上一键升级
克隆本仓库并执行部署脚本，10 秒内即可将现有 ComfyUI 升级为本专版：
```powershell
git clone https://github.com/deancyl/comfyui-agent-workflows.git
cd comfyui-agent-workflows
powershell -ExecutionPolicy Bypass -File scripts/setup_edition.ps1 -TargetDir "您的ComfyUI路径"
```

### 场景 2：在全新电脑上从零配置专版 ComfyUI
```powershell
# 1. 克隆 ComfyUI 原版并建立环境
git clone https://github.com/comfyanonymous/ComfyUI.git C:\Users\deanc\ComfyUI-Zluda
cd C:\Users\deanc\ComfyUI-Zluda
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt

# 2. 克隆本仓库并一键注入专版工作流、节点、补丁与启动器
git clone https://github.com/deancyl/comfyui-agent-workflows.git
powershell -ExecutionPolicy Bypass -File comfyui-agent-workflows/scripts/setup_edition.ps1 -TargetDir "C:\Users\deanc\ComfyUI-Zluda"

# 3. 一键下载核心模型
powershell -ExecutionPolicy Bypass -File comfyui-agent-workflows/scripts/download_models.ps1 -TargetDir "C:\Users\deanc\ComfyUI-Zluda"
```

---

## 🖥️ 桌面启动与运行体验

专版生成了无控制台黑框的静默启动器：
- 双击 **`launch_gui.vbs`**：
  - Windows 原生无窗口模式（`WindowStyle 0`）在后台纯静默托管；
  - 自动以 Edge 独立应用模式（`--app=http://127.0.0.1:8284`）唤出无地址栏的纯粹桌面软件界面。
- 命令行手动启动（AMD 780M / ZLUDA）：
  ```powershell
  powershell -File scripts/start_zluda_amd.ps1 -Foreground
  ```

---

## 🤖 大模型 Agent 程序化调用示例

外部智能体可通过 Python SDK 轻松调用任意工作流：

```python
from scripts.comfy_agent_client import ComfyAgentClient

client = ComfyAgentClient("http://127.0.0.1:8284")

# 1. 载入 WF01 电影级真人写实工作流
graph = client.load_workflow_file("workflows/01_真人写实_极致NanoBanana_次表面透析_电影双段精雕流.json")

# 2. 提交任务并全自动等待微雕成片下载
images = client.run_generation(graph, output_dir="./output_images")
print(f"生成的成片已下载: {images}")
```

更多关于参数热修改、随机种子注入、队列监听与故障自愈的规范，请直接阅读机器可读文档 [`AGENT_GUIDE.md`](AGENT_GUIDE.md)。

---

## 📂 仓库目录结构

```text
comfyui-agent-workflows/
├── README.md                          # 项目主说明文档
├── AGENT_GUIDE.md                     # 🤖 大模型智能体专属自动化调度契约 (Machine-Readable)
├── LICENSE                            # MIT 开源许可证
├── workflows/                         # 17 套经过严格双轨打标的 JSON 工作流
│   ├── 01 ~ 17 全部 17 套工作流
│   └── README.md                      # 工作流矩阵总览与节点映射速查
├── custom_nodes/                      # 配套自定义扩展
│   └── ComfyUI-NSFW-Interrogator/     # WF03 必需的 WD14 + 双轨中英对照反推节点
├── patches/                           # 专版稳定性补丁
│   ├── apply_zluda_ln_patch.py        # ZLUDA LayerNorm 驱动崩溃修复补丁
│   ├── patch_utils.py                 # PyTorch safe_globals 兼容补丁
│   └── extra_model_paths.yaml.example # 多盘与整合包共享模型路径模板
├── docs/
│   ├── EDITION_SETUP_GUIDE.md         # 🚀 专版从零部署与跨机器一键配置全指南
│   ├── HARDWARE_CONFIG_ZLUDA_AMD.md   # 🛠️ AMD 780M / ZLUDA / ROCm 5.7 硬件级调优避坑全指南
│   ├── MODEL_ZOO.md                   # 📦 所需 Checkpoint、LoRA、ControlNet 下载清单与放置路径
│   └── API_SPEC.md                    # 🌐 ComfyUI REST API & WebSocket 协议规范
└── scripts/
    ├── setup_edition.ps1              # 专版一键部署与同步脚本 (Master Deployer)
    ├── download_models.ps1            # 核心模型断点续传一键下载器
    ├── comfy_agent_client.py          # 开箱即用的大模型 Agent 调度 SDK (Python)
    ├── start_zluda_amd.ps1            # AMD 780M / ZLUDA Windows 静默无窗口启动脚本
    └── start_nvidia.bat               # NVIDIA CUDA 通用启动批处理
```

---

## 📄 开源许可证 (License)

本项目采用 [MIT 许可证](LICENSE)。
欢迎各类开源 Agent 框架（Antigravity, OpenCode, AutoGPT, MetaGPT）与生图爱好者自由集成、二次分发与拓展！
