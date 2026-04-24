# 大学生志愿者管理系统设计规格

## 1. 项目背景

本项目基于开题报告《基于web的大学生志愿者管理系统设计与开发》和任务书要求实施，目标是完成一个可在电脑浏览器中运行的高校内部志愿者管理系统，并同步形成毕业设计所需的代码、数据库设计、测试材料、部署说明和论文支撑内容。

当前工作区没有任何现成源代码、数据库脚本或 Git 仓库，属于从 0 到 1 的空白项目启动状态，因此本规格既是项目实施边界，也是后续数据库设计、接口拆分、页面开发和论文撰写的统一依据。

## 2. 项目目标

- 实现一个基于 B/S 架构的大学生志愿者管理系统
- 覆盖活动发布、报名审核、签到签退、时长认定、统计报表等完整业务流程
- 提供学生端和管理员端两类角色
- 支持本机部署与答辩演示
- 使用贴近高校真实场景的模拟数据，保证字段、流程和统计结果合理可信

## 3. 范围边界

### 3.1 纳入范围

- 电脑网页版系统
- 学生端功能
- 管理端功能
- 登录鉴权与角色控制
- 活动封面、公告附件、学生头像上传
- 图表统计
- Excel 导出
- 初始化模拟数据
- 本机部署
- 测试文档和部署说明

### 3.2 明确不做

- 微信小程序
- 移动端专门适配
- 短信、邮件等外部通知
- 第三方平台打通
- 复杂推荐算法
- 区块链存证
- 地图定位签到
- 细粒度 RBAC 权限树

## 4. 技术架构

系统采用前后端分离模式：

- 前端：Vue 3 + Vite + Element Plus + Axios + Vue Router + Pinia + ECharts
- 后端：Spring Boot + MyBatis-Plus + MySQL + JWT
- 部署环境：Windows 本机部署
- 文件存储：本地 `uploads/` 目录

论文与答辩口径保持为 `Vue + Spring Boot + MyBatis` 主路线，工程实现允许使用 MyBatis-Plus 和 Element Plus 提升开发效率。

## 5. 角色与账号模型

系统只保留两类固定角色，不引入复杂权限树：

- `STUDENT`
- `ADMIN`

### 5.1 账号产生方式

- 不提供学生自主注册
- 管理员账号由初始化脚本直接生成
- 学生账号由初始化脚本批量生成，也支持后续管理员新增
- 学生登录用户名使用学号
- 管理员登录用户名使用工号或预设管理员账号
- 初始化默认密码统一为 `123456`，数据库中使用加密后的密码存储

### 5.2 账号关联方式

- `sys_user` 存储登录账号与角色
- `student` 存储学生档案
- `admin_user` 存储管理员档案
- `sys_user.ref_id` 指向学生或管理员档案主键

## 6. 功能模块与页面清单

### 6.1 学生端

- 登录页
- 首页
  - 公告展示
  - 近期活动
  - 个人累计时长概览
- 活动列表页
- 活动详情页
- 我的报名页
- 签到页
- 我的时长页
- 我的消息页
- 个人中心页

### 6.2 管理端

- 管理员登录页
- 后台首页
- 学生管理页
- 活动管理页
- 报名审核页
- 签到管理页
- 时长认定页
- 公告管理页
- 统计报表页
- 管理员管理页

## 7. 核心业务闭环

1. 管理员创建活动并发布
2. 学生浏览活动并提交报名
3. 管理员审核报名
4. 学生在规定时间窗内签到与签退
5. 系统根据有效签到签退结果生成服务时长记录
6. 管理员确认或修正时长
7. 系统生成报表、消息通知与导出数据

## 8. 数据库设计

### 8.1 表设计总则

- 所有主表主键使用 `bigint`
- 所有业务表包含 `created_at`、`updated_at`
- 需要逻辑删除的表包含 `is_deleted`，默认值为 `0`
- 所有状态字段使用约定枚举值，不使用自由文本
- 所有唯一业务约束必须在数据库层体现
- 所有外键关系在数据库脚本中显式声明

### 8.1.1 字段类型与默认值约定

- 主键：`bigint`，自增，非空
- 编码类字段：`varchar(20)`，非空
- 用户名、学号、工号：`varchar(50)`，非空
- 名称类字段：`varchar(100)`，非空
- 手机号：`varchar(20)`，可空
- 邮箱：`varchar(100)`，可空
- 地址、地点、文件路径：`varchar(255)`，可空
- 简短备注：`varchar(255)`，可空
- 正文、描述：`text`，可空
- 时间字段：`datetime`，非空或按业务定义可空
- 时长字段：`decimal(6,2)`，默认值 `0.00`
- 数量字段：`int`，默认值按业务字段确定
- 布尔标记：`tinyint(1)`，默认值 `0`

### 8.1.2 删除策略

- 使用逻辑删除：`sys_user`、`student`、`admin_user`、`volunteer_activity`、`activity_signup`、`notice`
- 不允许物理或逻辑删除，仅允许状态流转：`activity_sign`、`service_hours_record`、`message_notice`、`operation_log`

### 8.1.3 外键归属统一约定

- 所有 `student_id` 均关联 `student.id`
- 所有 `activity_id` 均关联 `volunteer_activity.id`
- 所有 `signup_id` 均关联 `activity_signup.id`
- 所有 `sign_id` 均关联 `activity_sign.id`
- 所有 `user_id`、`published_by`、`reviewed_by`、`sign_in_operator_id`、`sign_out_operator_id`、`confirmed_by`、`operator_user_id` 均统一关联 `sys_user.id`
- 管理员姓名展示通过 `sys_user.ref_id -> admin_user.id` 关联获得

### 8.2 表结构明细

#### 8.2.1 `sys_user`

用途：登录账号表

字段：

- `id`
- `username`
- `password_hash`
- `role_code`，取值 `STUDENT` 或 `ADMIN`
- `ref_id`，关联学生或管理员档案
- `account_status`，取值 `ENABLED`、`DISABLED`
- `last_login_time`
- `created_at`
- `updated_at`
- `is_deleted`

约束：

- `username` 唯一
- `role_code + ref_id` 组合唯一

#### 8.2.2 `student`

用途：学生档案表

字段：

- `id`
- `student_no`
- `name`
- `gender`
- `college_name`
- `major_name`
- `class_name`
- `phone`
- `email`
- `avatar_url`
- `total_service_hours`
- `student_status`，取值 `NORMAL`、`DISABLED`
- `remark`
- `created_at`
- `updated_at`
- `is_deleted`

约束：

- `student_no` 唯一

#### 8.2.3 `admin_user`

用途：管理员档案表

字段：

- `id`
- `admin_no`
- `name`
- `phone`
- `email`
- `title_name`
- `admin_status`，取值 `NORMAL`、`DISABLED`
- `created_at`
- `updated_at`
- `is_deleted`

约束：

- `admin_no` 唯一

#### 8.2.4 `dict_activity_category`

用途：活动类别字典表

字段：

- `id`
- `category_code`
- `category_name`
- `sort_no`
- `category_status`
- `created_at`
- `updated_at`

约束：

- `category_code` 唯一

#### 8.2.5 `volunteer_activity`

用途：志愿活动表

字段：

- `id`
- `title`
- `category_code`
- `location`
- `organizer_name`
- `description`
- `cover_url`
- `attachment_url`
- `recruit_count`
- `signup_deadline`
- `start_time`
- `end_time`
- `service_hours`
- `check_in_code`
- `check_out_code`
- `activity_status`
- `published_by`
- `published_at`
- `created_at`
- `updated_at`
- `is_deleted`

约束：

- `end_time > start_time`
- `signup_deadline <= start_time`
- `recruit_count > 0`
- `service_hours > 0`

说明：

- `cover_url` 用于活动封面上传
- `attachment_url` 用于活动附件上传，可为空
- `check_in_code`、`check_out_code` 为 6 位签到码
- `check_in_code`、`check_out_code` 默认在活动发布时生成

#### 8.2.6 `activity_signup`

用途：活动报名表

字段：

- `id`
- `activity_id`
- `student_id`
- `signup_status`
- `review_comment`
- `reviewed_by`
- `reviewed_at`
- `cancel_reason`
- `signup_time`
- `created_at`
- `updated_at`
- `is_deleted`

约束：

- `activity_id + student_id` 唯一

默认值：

- `signup_status` 默认值为 `PENDING`

#### 8.2.7 `activity_sign`

用途：签到签退表

字段：

- `id`
- `activity_id`
- `student_id`
- `sign_status`
- `sign_in_time`
- `sign_out_time`
- `sign_in_mode`
- `sign_out_mode`
- `sign_in_operator_id`
- `sign_out_operator_id`
- `exception_remark`
- `created_at`
- `updated_at`

约束：

- `activity_id + student_id` 唯一

说明：

- 报名审核通过时预创建签到记录，初始状态为 `UNSIGNED`
- 若报名未通过，则不创建签到记录

#### 8.2.8 `service_hours_record`

用途：服务时长记录表

字段：

- `id`
- `activity_id`
- `student_id`
- `signup_id`
- `sign_id`
- `hours_value`
- `hours_status`
- `generated_at`
- `confirmed_by`
- `confirmed_at`
- `remark`
- `created_at`
- `updated_at`

约束：

- `activity_id + student_id` 唯一

#### 8.2.9 `notice`

用途：公共公告表

字段：

- `id`
- `title`
- `content`
- `attachment_url`
- `target_scope`
- `publish_status`
- `published_by`
- `published_at`
- `created_at`
- `updated_at`
- `is_deleted`

说明：

- `target_scope` 当前固定为 `ALL_STUDENTS`
- `attachment_url` 用于公告附件上传

#### 8.2.10 `message_notice`

用途：学生个人消息表

字段：

- `id`
- `user_id`
- `message_type`
- `title`
- `content`
- `biz_type`
- `biz_id`
- `is_read`
- `created_at`
- `read_at`

说明：

- `user_id` 关联 `sys_user.id`
- `message_type` 取值包括 `SIGNUP_APPROVED`、`SIGNUP_REJECTED`、`ACTIVITY_CHANGED`、`NOTICE_PUBLISHED`、`HOURS_CONFIRMED`
- 公告发布后系统批量为所有启用中的学生账号生成一条个人消息

#### 8.2.11 `operation_log`

用途：关键操作日志表

字段：

- `id`
- `operator_user_id`
- `operator_role_code`
- `module_name`
- `operation_type`
- `biz_id`
- `request_path`
- `operation_desc`
- `operation_time`

### 8.3 关键索引

- `student.student_no`
- `admin_user.admin_no`
- `volunteer_activity.activity_status`
- `volunteer_activity.start_time`
- `activity_signup.activity_id + signup_status`
- `activity_signup.student_id + signup_status`
- `service_hours_record.student_id + hours_status`

## 9. 状态机设计

### 9.1 活动状态 `activity_status`

- `DRAFT` 草稿
- `PUBLISHED` 已发布，可报名
- `SIGNUP_CLOSED` 报名截止
- `IN_PROGRESS` 进行中
- `COMPLETED` 已完成
- `CANCELLED` 已取消

状态流转：

- 草稿 -> 已发布
- 已发布 -> 报名截止
- 已发布或报名截止 -> 进行中
- 进行中 -> 已完成
- 草稿、已发布、报名截止 -> 已取消

### 9.2 报名状态 `signup_status`

- `PENDING` 待审核
- `APPROVED` 已通过
- `REJECTED` 已驳回
- `CANCELLED` 已取消

状态流转：

- 待审核 -> 已通过
- 待审核 -> 已驳回
- 待审核 -> 已取消
- 已通过 -> 已取消

### 9.3 签到状态 `sign_status`

- `UNSIGNED` 未签到
- `SIGNED_IN` 已签到未签退
- `SIGNED_OUT` 已签到已签退
- `ABSENT` 缺席
- `ADMIN_FIXED` 管理员补录

状态流转：

- 审核通过后预创建签到记录，初始为 `UNSIGNED`
- `UNSIGNED` -> `SIGNED_IN`
- `SIGNED_IN` -> `SIGNED_OUT`
- `UNSIGNED` -> `ABSENT`
- `UNSIGNED`、`ABSENT`、`SIGNED_IN` -> `ADMIN_FIXED`

补充定义：

- `ADMIN_FIXED` 表示管理员人工修正后的有效完成记录
- 进入 `ADMIN_FIXED` 状态时，`sign_in_time` 和 `sign_out_time` 必须同时有值
- `ADMIN_FIXED` 在统计口径上视同“已签到且已完成”

### 9.4 时长状态 `hours_status`

- `PENDING_CONFIRM` 待确认
- `CONFIRMED` 已确认
- `REVOKED` 已撤销

## 10. 关键业务规则

### 10.1 活动规则

- 活动必须填写标题、类别、地点、人数上限、报名截止时间、开始结束时间、服务时长
- 活动发布后方可被学生查看和报名
- 报名截止时间不能晚于活动开始时间

### 10.2 报名规则

- 同一学生对同一活动只能报名一次
- 活动已满员、已截止、已开始、已取消时不可报名
- 报名后默认状态为 `PENDING`
- 管理员审核通过后才可签到
- 学生只能在活动开始前且未签到时取消报名
- 活动满员的判定口径为：`APPROVED` 状态报名人数大于等于 `recruit_count`
- `PENDING` 状态不占正式名额
- 管理员审核通过时必须再次校验剩余名额
- 学生取消报名或管理员驳回报名后，名额立即释放

### 10.3 签到规则

签到采用“签到码”方式，不使用定位、不使用二维码识别作为必选能力。

- 活动发布时系统生成 `check_in_code` 和 `check_out_code`
- 学生在签到页输入签到码完成签到
- 签到时间窗：活动开始前 30 分钟至活动开始后 30 分钟
- 签退时间窗：活动结束前 30 分钟至活动结束后 120 分钟
- 仅报名审核通过的学生可签到
- 重复签到、重复签退必须拦截
- 管理员可在后台执行补签，补签记录状态记为 `ADMIN_FIXED`
- 超时未签到的报名记录可标记为 `ABSENT`
- 报名审核通过时，系统预创建一条 `activity_sign` 记录
- 活动结束后若仍为 `UNSIGNED`，系统或管理员将其置为 `ABSENT`
- 若学生已签到但未签退，管理员补齐签退时间后，签到记录状态更新为 `ADMIN_FIXED`
- 管理员执行补录时，必须一次性补齐有效签到时间和签退时间

### 10.4 时长规则

- 只有有效签到并完成签退的学生，系统才生成时长记录
- 系统默认按活动预设 `service_hours` 生成 `PENDING_CONFIRM` 记录
- 管理员可确认、修正或撤销时长
- 时长确认后同步汇总到学生累计时长
- `student.total_service_hours` 为冗余汇总字段，不直接增减维护
- 每次确认、修正、撤销时长后，系统在同一事务中按 `service_hours_record` 中所有 `CONFIRMED` 记录重新汇总该学生累计时长
- 活动取消且已存在时长记录时，相关时长记录统一改为 `REVOKED`，并重新汇总学生累计时长

### 10.5 公告与消息规则

- `notice` 为公共公告
- `message_notice` 为个人消息
- 以下场景触发个人消息：
  - 报名审核通过
  - 报名审核驳回
  - 活动时间或地点变更
  - 公告发布
  - 时长确认完成
- `message_notice.user_id` 固定关联登录账号 `sys_user.id`
- 公告发布一定会派生个人消息，不保留“仅首页展示不派生”的第二方案

### 10.6 文件上传规则

- 活动支持上传封面和附件
- 公告支持上传附件
- 学生支持上传头像
- 文件统一存储到本地 `uploads/` 目录，数据库只保存相对路径

## 11. 报表与导出定义

### 11.1 后台首页图表

- 活动总数
- 本月活动数
- 报名总人数
- 已完成活动数
- 累计服务时长
- 按月份统计活动数柱状图
- 按类别统计活动数饼图
- 按学院统计累计时长柱状图

### 11.2 报表页

- 活动统计报表
  - 筛选条件：活动名称、类别、状态、时间范围
  - 字段：活动名称、类别、地点、报名人数、审核通过人数、签到人数、完成人数、总时长
- 学生时长报表
  - 筛选条件：学院、专业、班级、学生姓名、学号
  - 字段：学号、姓名、学院、专业、班级、累计时长、参与活动次数
- 月度统计报表
  - 筛选条件：月份
  - 字段：活动数、参与人数、总时长

### 11.3 导出功能

- 导出活动报名名单
  - 字段：活动名称、学号、姓名、学院、专业、班级、报名状态、签到状态
- 导出学生时长统计
  - 字段：学号、姓名、学院、专业、班级、累计时长、已完成活动数
- 导出活动完成情况
  - 字段：活动名称、类别、地点、活动时间、人数上限、报名人数、签到人数、完成人数、累计时长

### 11.4 统计口径统一约定

- 报名人数：`activity_signup` 全部有效记录总数
- 审核通过人数：`activity_signup.signup_status = APPROVED`
- 签到人数：`activity_sign.sign_status` 为 `SIGNED_IN`、`SIGNED_OUT`、`ADMIN_FIXED` 的人数
- 完成人数：`activity_sign.sign_status` 为 `SIGNED_OUT`、`ADMIN_FIXED` 的人数
- 参与活动次数：学生 `service_hours_record.hours_status = CONFIRMED` 的记录条数
- 累计服务时长：学生所有 `service_hours_record.hours_status = CONFIRMED` 的 `hours_value` 总和
- `CANCELLED` 活动不计入已完成活动数、参与活动次数和累计服务时长
- `REVOKED` 时长记录不计入累计服务时长

## 12. 活动变更与取消规则

- 活动开始前允许修改时间、地点、人数上限、封面、附件和描述
- 活动进入 `IN_PROGRESS` 后，不允许修改开始时间和结束时间
- 活动取消仅允许发生在 `COMPLETED` 之前
- 活动取消后：
  - 所有未完成签到的报名记录保持原报名状态，但活动本身标记为 `CANCELLED`
  - 已存在的签到记录保留原始签到状态，仅用于审计追踪，不再允许继续签到或签退
  - 所有已生成且未撤销的时长记录统一改为 `REVOKED`
  - 已报名学生收到一条 `ACTIVITY_CHANGED` 类型消息，内容说明活动已取消
  - 统计报表默认不将 `CANCELLED` 活动计入“已完成活动数”和累计服务时长
- 活动时间或地点修改后：
  - 所有 `PENDING` 和 `APPROVED` 状态的报名学生收到一条 `ACTIVITY_CHANGED` 消息
  - 原签到码失效，系统重新生成签到码和签退码

## 13. 模拟数据方案

### 13.1 数据规模

- 管理员账号 2 个
- 学生账号 80 到 120 个
- 活动类别 6 到 8 个
- 志愿活动 20 到 30 个
- 报名记录 200 到 400 条
- 时长记录 100 到 200 条
- 公告 8 到 12 条

### 13.2 数据口径

- 学院、专业、班级按高校常见结构构造
- 学生活动参与度要有差异，保证统计图表可展示
- 活动时间覆盖过去、当前和未来，便于演示不同状态
- 报名、签到、时长数据之间必须自洽

## 14. 非功能要求

### 14.1 易用性

- 表格、筛选、分页完整
- 所有关键操作给出明确提示

### 14.2 可靠性

- 统一返回结构
- 全局异常处理
- 参数校验

### 14.3 安全性

- JWT 身份认证
- 基于角色的接口访问控制
- 密码加密存储
- 管理员关键操作日志留痕

### 14.4 可维护性

- 前后端目录清晰
- 数据库脚本、初始化脚本、部署说明齐备

## 15. 测试范围

- 登录测试
- 学生报名测试
- 管理员审核测试
- 学生签到签退测试
- 时长生成与确认测试
- 公告发布与消息生成测试
- 报表与导出测试
- 权限拦截测试

## 16. 实施阶段规划

1. 初始化前后端工程和数据库环境
2. 完成数据库建模、建表脚本和初始化数据脚本
3. 完成后端基础设施，包括登录、鉴权、统一响应、异常处理、文件上传
4. 完成学生端功能
5. 完成管理端功能
6. 完成统计、导出、消息和日志
7. 完成联调、测试和部署
8. 完成论文支撑材料整理

## 17. 预期交付物

- 前端工程代码
- 后端工程代码
- 数据库建表脚本
- 初始化模拟数据脚本
- 部署说明
- 测试用例与测试报告
- 系统设计、数据库设计、流程图和页面截图素材

## 18. 风险与约束

- 当前无现成代码基础，需要完整搭建前后端项目
- 当前无真实校方业务数据，需要构建可信的模拟数据集
- 当前无 Git 仓库，无法执行规范中的提交步骤；若后续需要可初始化 Git
- 项目必须优先保证毕业设计的完整闭环，而不是追求超范围扩展

## 19. 实施原则

- 优先完成可演示的完整业务闭环
- 所有功能都必须具备页面、接口、数据库字段和测试依据
- 所有实现都应直接支撑论文撰写和答辩展示
