# Final Format Audit

## Build Outputs

- Thesis source: `drafts/thesis_source.md`
- Working blueprint: `drafts/thesis-blueprint.md`
- Project analysis notes: `notes/project-analysis.md`
- Final DOCX: `deliverables/thesis-final.docx`
- Reference ledger: `audit/verified-references.md`
- Workspace audit: `audit/latest-audit.md`

## Automated Checks

- [PASS] 模板工作区初始化完成。
- [PASS] 模板 `.doc` 已转换为可编辑的 `thesis-working.docx`。
- [PASS] 最终论文已通过 `scripts/build_thesis.py` 构建。
- [PASS] Word COM 后处理已完成，目录字段已更新。
- [PASS] 公式占位符 `OMATH::` 已消失，说明公式已转为 Word 公式对象。
- [PASS] 文档中存在 7 个正文章节标题，以及“参考文献”“致谢”标题。
- [PASS] 文档中共生成 10 张表格对象，满足功能需求表、数据源表、接口表、测试表和结果表等内容承载。
- [PASS] 文本源文件非空白字符统计约为 16419，满足“13000 字左右”的要求范围。
- [PASS] `pytest -q` 结果为 `8 passed in 2.66s`。
- [PASS] 技能自带工作区审计脚本返回 `AUDIT_OK`。

## Embedded Evidence

- 已插入系统结构图、数据流图和数据模型图。
- 已插入 5 张系统页面截图。
- 已插入趋势、风险、相关性和质量统计图。
- 已插入 3 段核心代码片段。
- 已插入 5 个公式对象。
- 已插入参考文献与致谢章节。

## Residual Manual Review Items

- 建议在 Microsoft Word 或 WPS 中人工检查一次目录页的点线对齐、页码与封面字段的视觉位置。
- 建议人工滚动检查图表与其题注是否始终位于同页附近，避免个别页面因自动分页产生轻微跳动。
- 建议最终提交前按学校要求再次核对学号、日期、导师姓名及英文姓名转写是否需要改成你所在学院常用格式。
