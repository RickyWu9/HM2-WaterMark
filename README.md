# Watermark Studio - 批量图片水印工具

一个功能强大的批量图片水印处理工具，支持文本和图片水印，提供实时预览和灵活的导出选项。

## 功能特性

### 核心功能 (MVP)
- ✅ **图片导入**: 支持单张/批量/文件夹导入，拖拽支持
- ✅ **格式支持**: JPEG、PNG（支持透明通道）、BMP、TIFF
- ✅ **文本水印**: 自定义文本、字体、大小、颜色、透明度
- ✅ **实时预览**: 所见即所得的水印效果预览
- ✅ **位置控制**: 九宫格预设位置 + 精确偏移调整
- ✅ **批量导出**: JPEG/PNG格式，质量可调
- ✅ **文件命名**: 保留原名/添加前缀/添加后缀
- ✅ **模板管理**: 保存/加载水印配置模板

### 高级功能
- ✅ **图片水印**: 支持PNG透明图片作为水印
- ✅ **水印旋转**: 任意角度旋转水印
- ✅ **字体设置**: 系统字体选择、字号调节
- ✅ **颜色选择**: 图形化颜色选择器
- ✅ **导出设置**: JPEG质量调节、输出目录选择
- ✅ **安全保护**: 防止覆盖原图，自动处理文件名冲突

## 系统要求

- Python 3.7+
- Windows 10/11 或 macOS 10.14+ 或 Linux
- 至少 4GB RAM（处理大量图片时建议 8GB+）

## 安装说明

### 方法一：直接运行（推荐）

1. 克隆或下载项目：
```bash
git clone https://github.com/RickyWu9/HM2-WaterMark.git
cd HM2-WaterMark
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行程序：
```bash
python main.py
```

### 方法二：创建虚拟环境

```bash
# 创建虚拟环境
python -m venv watermark_env

# 激活虚拟环境
# Windows:
watermark_env\\Scripts\\activate
# macOS/Linux:
source watermark_env/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行程序
python main.py
```

## 使用指南

### 基本使用流程

1. **导入图片**
   - 点击"导入图片"选择单张或多张图片
   - 点击"导入文件夹"批量导入整个文件夹
   - 直接拖拽图片或文件夹到程序窗口

2. **设置水印**
   - 在右侧"水印"标签页中选择文本或图片水印
   - 调整水印内容、字体、大小、颜色、透明度等
   - 实时预览区域会显示水印效果

3. **调整布局**
   - 在"布局"标签页中选择九宫格位置
   - 使用偏移滑块精确调整位置
   - 可选择旋转角度

4. **配置导出**
   - 在"导出"标签页中选择输出格式（JPEG/PNG）
   - 设置文件命名规则
   - 选择输出目录

5. **开始导出**
   - 点击工具栏"开始导出"按钮
   - 等待处理完成，查看结果

### 高级功能

#### 模板管理
- **保存模板**: 将当前所有设置保存为模板，方便重复使用
- **加载模板**: 快速应用已保存的配置
- **默认模板**: 程序提供预设的文本和Logo水印模板

#### 图片水印
- 支持PNG格式的透明图片作为水印
- 可调整水印图片的缩放比例和透明度
- 适合添加Logo、签名等图形水印

#### 批量处理优化
- 异步处理，不阻塞界面操作
- 进度条显示处理进度
- 错误处理和重试机制

## 项目结构

```
watermark-studio/
├── main.py                 # 程序入口
├── main_window.py          # 主窗口界面
├── config.py               # 配置文件
├── utils.py                # 工具函数
├── image_manager.py        # 图片管理
├── watermark_engine.py     # 水印处理引擎
├── template_manager.py     # 模板管理
├── requirements.txt        # 依赖列表
├── README.md              # 说明文档
├── prd-watermark.md       # 产品需求文档
└── templates/             # 模板存储目录（自动创建）
```

## 技术架构

- **GUI框架**: Tkinter（Python内置）
- **图像处理**: Pillow (PIL)
- **配置管理**: JSON格式
- **多线程**: 后台处理，保持界面响应
- **模块化设计**: 功能分离，易于维护和扩展

## 支持的格式

### 输入格式
- JPEG (.jpg, .jpeg)
- PNG (.png) - 支持透明通道
- BMP (.bmp)
- TIFF (.tiff, .tif)

### 输出格式
- JPEG - 可调节质量（1-100）
- PNG - 保持透明通道

## 常见问题

### Q: 程序启动失败，提示缺少依赖？
A: 请确保已安装Pillow库：`pip install Pillow`

### Q: 预览显示空白？
A: 检查图片格式是否支持，尝试刷新预览或重新选择图片

### Q: 导出的图片质量不好？
A: 调整JPEG质量设置，或选择PNG格式以获得无损输出

### Q: 水印位置不准确？
A: 使用偏移滑块进行精确调整，或尝试不同的九宫格位置

### Q: 批量处理很慢？
A: 大图片处理需要时间，建议关闭其他占用内存的程序

## 开发计划

- [ ] 批量差异化水印（不同图片不同水印）
- [ ] 更多水印样式（阴影、描边、渐变）
- [ ] 图片尺寸调整功能
- [ ] 更多输出格式支持
- [ ] 命令行版本
- [ ] 插件系统

## 贡献指南

欢迎提交Issue和Pull Request！

1. Fork本项目
2. 创建功能分支：`git checkout -b feature/new-feature`
3. 提交更改：`git commit -am 'Add new feature'`
4. 推送分支：`git push origin feature/new-feature`
5. 创建Pull Request

## 许可证

本项目采用MIT许可证 - 详见LICENSE文件

## 联系方式

- 项目地址: https://github.com/RickyWu9/HM2-WaterMark
- 问题反馈: 请在GitHub上提交Issue

---

**Watermark Studio** - 让批量水印处理变得简单高效！
