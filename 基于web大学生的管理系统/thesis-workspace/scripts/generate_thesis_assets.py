from __future__ import annotations

from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
CHARTS_DIR = ROOT / "charts"


def _pick_font() -> str:
    candidates = ["Microsoft YaHei", "SimHei", "SimSun", "KaiTi"]
    names = {font.name for font in fm.fontManager.ttflist}
    for candidate in candidates:
        if candidate in names:
            return candidate
    return "DejaVu Sans"


FONT_NAME = _pick_font()


def _setup_style():
    plt.rcParams["font.family"] = FONT_NAME
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.facecolor"] = "white"
    plt.rcParams["axes.facecolor"] = "white"


def _rounded_box(ax, x, y, w, h, title, subtitle="", fc="#EAF2FF", ec="#31425B", fontsize=11):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.025",
        linewidth=1.6,
        edgecolor=ec,
        facecolor=fc,
    )
    ax.add_patch(patch)
    text = title if not subtitle else f"{title}\n{subtitle}"
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize, color="#1F2D3D")


def _entity_box(ax, x, y, w, h, title, lines, header_fc="#CFE3FF", body_fc="#FFFFFF"):
    ax.add_patch(Rectangle((x, y), w, h, linewidth=1.5, edgecolor="#2F3F59", facecolor=body_fc))
    header_h = min(0.06, h * 0.22)
    ax.add_patch(Rectangle((x, y + h - header_h), w, header_h, linewidth=1.5, edgecolor="#2F3F59", facecolor=header_fc))
    ax.text(x + w / 2, y + h - header_h / 2, title, ha="center", va="center", fontsize=10.5, weight="bold")
    inner_top = y + h - header_h - 0.01
    usable_h = h - header_h - 0.02
    step = usable_h / max(len(lines), 1)
    for index, line in enumerate(lines):
        yy = inner_top - step * (index + 0.5)
        ax.text(x + 0.01, yy, line, ha="left", va="center", fontsize=7.4, color="#243447")


def _arrow(ax, start, end, label="", lw=1.8, color="#31425B"):
    arrow = FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=16, linewidth=lw, color=color)
    ax.add_patch(arrow)
    if label:
        ax.text((start[0] + end[0]) / 2, (start[1] + end[1]) / 2 + 0.02, label, ha="center", va="center", fontsize=9, color=color)


def generate_system_architecture():
    fig, ax = plt.subplots(figsize=(11.2, 6.6), dpi=220)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    _rounded_box(ax, 0.04, 0.63, 0.18, 0.18, "学生端界面", "Vue 3 + Element Plus", "#D9EAFF")
    _rounded_box(ax, 0.04, 0.29, 0.18, 0.18, "管理端界面", "Vue 3 + Element Plus", "#D9EAFF")
    _rounded_box(ax, 0.34, 0.44, 0.23, 0.20, "业务服务层", "Spring Boot REST API", "#DDF5E5")
    _rounded_box(ax, 0.68, 0.73, 0.24, 0.11, "认证与鉴权模块", "JWT / 登录身份恢复", "#FFF2C6")
    _rounded_box(ax, 0.68, 0.54, 0.24, 0.11, "活动治理模块", "活动 / 报名 / 签到 / 时长", "#FFE6A6")
    _rounded_box(ax, 0.68, 0.35, 0.24, 0.11, "通知与统计模块", "公告 / 消息 / 报表", "#FFF2C6")
    _rounded_box(ax, 0.68, 0.16, 0.24, 0.11, "数据访问层", "MyBatis-Plus Mapper", "#F4E8FF")
    _rounded_box(ax, 0.34, 0.10, 0.23, 0.12, "数据存储层", "H2 / MySQL + 文件目录", "#F9DDE0")

    _arrow(ax, (0.22, 0.72), (0.34, 0.55))
    _arrow(ax, (0.22, 0.38), (0.34, 0.53))
    _arrow(ax, (0.57, 0.59), (0.68, 0.78))
    _arrow(ax, (0.57, 0.54), (0.68, 0.60))
    _arrow(ax, (0.57, 0.49), (0.68, 0.41))
    _arrow(ax, (0.80, 0.35), (0.80, 0.27))
    _arrow(ax, (0.68, 0.18), (0.57, 0.16))

    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "system-architecture.png", bbox_inches="tight")
    plt.close(fig)


def generate_business_flow():
    fig, ax = plt.subplots(figsize=(11, 6.5), dpi=220)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    _rounded_box(ax, 0.39, 0.84, 0.22, 0.08, "管理员创建活动", fc="#DCEBFF")
    _rounded_box(ax, 0.39, 0.69, 0.22, 0.08, "发布活动并生成签到码", fc="#DCEBFF")
    _rounded_box(ax, 0.39, 0.54, 0.22, 0.08, "学生在线报名", fc="#DDF5E5")
    _rounded_box(ax, 0.08, 0.54, 0.20, 0.08, "审核通过", "预生成签到记录", "#CCF2D9")
    _rounded_box(ax, 0.73, 0.54, 0.20, 0.08, "审核驳回", "推送审核结果消息", "#FFD7D9")
    _rounded_box(ax, 0.39, 0.39, 0.22, 0.08, "学生签到签退", fc="#FFF0B8")
    _rounded_box(ax, 0.39, 0.24, 0.22, 0.08, "生成待确认时长记录", fc="#F9DDE0")
    _rounded_box(ax, 0.39, 0.09, 0.22, 0.08, "管理员确认时长", "同步更新累计时长", "#E5E1FF")

    _arrow(ax, (0.50, 0.84), (0.50, 0.77))
    _arrow(ax, (0.50, 0.69), (0.50, 0.62))
    _arrow(ax, (0.39, 0.58), (0.28, 0.58))
    _arrow(ax, (0.61, 0.58), (0.73, 0.58))
    _arrow(ax, (0.50, 0.54), (0.50, 0.47))
    _arrow(ax, (0.50, 0.39), (0.50, 0.32))
    _arrow(ax, (0.50, 0.24), (0.50, 0.17))

    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "business-flow.png", bbox_inches="tight")
    plt.close(fig)


def generate_database_er():
    fig, ax = plt.subplots(figsize=(13, 8.6), dpi=220)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    _entity_box(ax, 0.03, 0.69, 0.20, 0.21, "student", ["PK id", "UK student_no", "name", "college_name", "major_name", "class_name", "total_service_hours"])
    _entity_box(ax, 0.03, 0.42, 0.20, 0.17, "admin_user", ["PK id", "UK admin_no", "name", "title_name", "admin_status"])
    _entity_box(ax, 0.29, 0.56, 0.20, 0.24, "sys_user", ["PK id", "UK username", "role_code", "ref_id", "account_status", "last_login_time", "UK(role_code, ref_id)"])
    _entity_box(ax, 0.56, 0.74, 0.18, 0.15, "dict_activity_category", ["PK id", "UK category_code", "category_name", "category_status"])
    _entity_box(ax, 0.53, 0.46, 0.24, 0.25, "volunteer_activity", ["PK id", "title", "FK category_code", "recruit_count", "start_time / end_time", "check_in_code / check_out_code", "FK published_by"])
    _entity_box(ax, 0.81, 0.69, 0.16, 0.15, "notice", ["PK id", "title", "target_scope", "FK published_by", "published_at"])
    _entity_box(ax, 0.23, 0.20, 0.22, 0.22, "activity_signup", ["PK id", "FK activity_id", "FK student_id", "signup_status", "FK reviewed_by", "UK(activity_id, student_id)"])
    _entity_box(ax, 0.50, 0.16, 0.22, 0.24, "activity_sign", ["PK id", "FK activity_id", "FK student_id", "sign_status", "FK sign_in_operator_id", "FK sign_out_operator_id", "UK(activity_id, student_id)"])
    _entity_box(ax, 0.77, 0.16, 0.20, 0.24, "service_hours_record", ["PK id", "FK activity_id", "FK student_id", "FK signup_id", "FK sign_id", "hours_value", "FK confirmed_by", "UK(activity_id, student_id)"])
    _entity_box(ax, 0.79, 0.41, 0.18, 0.18, "message_notice", ["PK id", "FK user_id", "message_type", "biz_type", "biz_id", "is_read"])
    _entity_box(ax, 0.03, 0.10, 0.20, 0.18, "operation_log", ["PK id", "FK operator_user_id", "module_name", "operation_type", "biz_id", "operation_time"])

    _arrow(ax, (0.23, 0.78), (0.29, 0.69), "1:1")
    _arrow(ax, (0.23, 0.50), (0.29, 0.61), "1:1")
    _arrow(ax, (0.49, 0.68), (0.53, 0.60), "1:N")
    _arrow(ax, (0.74, 0.80), (0.67, 0.71), "1:N")
    _arrow(ax, (0.77, 0.77), (0.81, 0.77), "1:N")
    _arrow(ax, (0.64, 0.46), (0.34, 0.42), "1:N")
    _arrow(ax, (0.63, 0.46), (0.61, 0.40), "1:N")
    _arrow(ax, (0.68, 0.46), (0.84, 0.40), "1:N")
    _arrow(ax, (0.34, 0.20), (0.84, 0.28), "1:N")
    _arrow(ax, (0.61, 0.16), (0.86, 0.16), "1:1")
    _arrow(ax, (0.49, 0.58), (0.12, 0.28), "1:N")

    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "database-er.png", bbox_inches="tight")
    plt.close(fig)


def generate_admin_role_split():
    fig, ax = plt.subplots(figsize=(10.8, 5.8), dpi=220)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    _rounded_box(ax, 0.34, 0.72, 0.32, 0.14, "后台 ADMIN 账户族", "统一登录模型：sys_user + admin_user", "#DCEBFF", fontsize=12)
    _rounded_box(ax, 0.08, 0.34, 0.34, 0.22, "系统管理员", "管理员管理\n学生档案治理\n公告与消息治理\n统计报表与运行审计", "#DDF5E5", fontsize=11.5)
    _rounded_box(ax, 0.58, 0.34, 0.34, 0.22, "活动管理员", "活动创建与发布\n报名审核\n签到异常修正\n时长确认与活动过程治理", "#FFF0B8", fontsize=11.5)
    _rounded_box(ax, 0.34, 0.08, 0.32, 0.12, "共同目标", "保障志愿活动全过程数据准确与治理有序", "#F9DDE0", fontsize=11)

    _arrow(ax, (0.43, 0.72), (0.25, 0.56))
    _arrow(ax, (0.57, 0.72), (0.75, 0.56))
    _arrow(ax, (0.25, 0.34), (0.43, 0.20))
    _arrow(ax, (0.75, 0.34), (0.57, 0.20))

    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "admin-role-split.png", bbox_inches="tight")
    plt.close(fig)


def generate_student_module_design():
    fig, ax = plt.subplots(figsize=(10.6, 6.2), dpi=220)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    _rounded_box(ax, 0.38, 0.42, 0.24, 0.16, "学生端模块中心", "参与活动 + 沉淀个人记录", "#DCEBFF", fontsize=12)
    boxes = [
        (0.08, 0.72, "学生首页", "公告 / 近期活动 / 累计时长"),
        (0.39, 0.76, "活动列表与详情", "浏览活动 / 查看条件 / 发起报名"),
        (0.72, 0.72, "我的报名", "查看审核结果 / 取消报名"),
        (0.08, 0.16, "签到签退", "输入签到码 / 签退码"),
        (0.39, 0.08, "我的时长", "时长明细 / 确认状态"),
        (0.72, 0.16, "我的消息与个人中心", "公告提醒 / 档案维护"),
    ]
    for x, y, title, subtitle in boxes:
        _rounded_box(ax, x, y, 0.20, 0.12, title, subtitle, "#EAF4FF", fontsize=10.5)
    centers = [(0.48, 0.58), (0.48, 0.42), (0.38, 0.50), (0.62, 0.50)]
    _arrow(ax, (0.28, 0.78), centers[0])
    _arrow(ax, (0.49, 0.76), centers[0])
    _arrow(ax, (0.72, 0.78), (0.60, 0.56))
    _arrow(ax, (0.28, 0.22), (0.38, 0.44))
    _arrow(ax, (0.49, 0.20), centers[1])
    _arrow(ax, (0.72, 0.22), (0.60, 0.44))

    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "student-module-design.png", bbox_inches="tight")
    plt.close(fig)


def generate_admin_module_design():
    fig, ax = plt.subplots(figsize=(11, 6.5), dpi=220)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    _rounded_box(ax, 0.38, 0.78, 0.24, 0.11, "管理端总体模块", "主数据治理 + 过程治理 + 结果分析", "#DCEBFF", fontsize=12)
    _rounded_box(ax, 0.06, 0.49, 0.25, 0.18, "基础治理层", "学生管理\n管理员管理\n活动分类与基础档案", "#DDF5E5", fontsize=11)
    _rounded_box(ax, 0.38, 0.49, 0.25, 0.18, "活动过程治理层", "活动管理\n报名审核\n签到管理\n时长管理", "#FFF0B8", fontsize=11)
    _rounded_box(ax, 0.69, 0.49, 0.25, 0.18, "信息与分析层", "公告管理\n统计报表\n导出与审计", "#F9DDE0", fontsize=11)
    _rounded_box(ax, 0.06, 0.14, 0.25, 0.16, "系统管理员主路径", "管理员管理 -> 学生管理 -> 公告/报表", "#EAF4FF", fontsize=10.5)
    _rounded_box(ax, 0.38, 0.14, 0.25, 0.16, "活动管理员主路径", "活动管理 -> 审核 -> 签到 -> 时长", "#FFF8D3", fontsize=10.5)
    _rounded_box(ax, 0.69, 0.14, 0.25, 0.16, "分析闭环", "公告触达 -> 消息反馈 -> 报表汇总", "#FCECEF", fontsize=10.5)

    _arrow(ax, (0.50, 0.78), (0.18, 0.67))
    _arrow(ax, (0.50, 0.78), (0.50, 0.67))
    _arrow(ax, (0.50, 0.78), (0.82, 0.67))
    _arrow(ax, (0.18, 0.49), (0.18, 0.30))
    _arrow(ax, (0.50, 0.49), (0.50, 0.30))
    _arrow(ax, (0.82, 0.49), (0.82, 0.30))

    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "admin-module-design.png", bbox_inches="tight")
    plt.close(fig)


def generate_page_data_linkage():
    fig, ax = plt.subplots(figsize=(12, 6.4), dpi=220)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(0.16, 0.94, "页面层", ha="center", va="center", fontsize=13, weight="bold", color="#2F3F59")
    ax.text(0.50, 0.94, "服务层", ha="center", va="center", fontsize=13, weight="bold", color="#2F3F59")
    ax.text(0.84, 0.94, "数据表层", ha="center", va="center", fontsize=13, weight="bold", color="#2F3F59")

    rows = [
        ("登录页 / 个人中心", "AuthService.login", "sys_user + student/admin_user"),
        ("活动管理页 / 活动列表页", "saveActivity / listActivities", "volunteer_activity + dict_activity_category"),
        ("报名审核页 / 签到签退页", "approveSignup / signIn / signOut", "activity_signup + activity_sign + service_hours_record"),
        ("公告管理页 / 我的消息页", "saveNotice / listMessages", "notice + message_notice"),
    ]
    ys = [0.76, 0.56, 0.36, 0.16]
    for (page, service, table), y in zip(rows, ys):
        _rounded_box(ax, 0.04, y, 0.24, 0.12, page, fc="#EAF4FF", fontsize=10.5)
        _rounded_box(ax, 0.38, y, 0.24, 0.12, service, fc="#DDF5E5", fontsize=10.5)
        _rounded_box(ax, 0.72, y, 0.24, 0.12, table, fc="#FFF3CC", fontsize=10.2)
        _arrow(ax, (0.28, y + 0.06), (0.38, y + 0.06))
        _arrow(ax, (0.62, y + 0.06), (0.72, y + 0.06))

    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "page-data-linkage.png", bbox_inches="tight")
    plt.close(fig)


def generate_monthly_stats():
    months = ["2026-01", "2026-02", "2026-03"]
    activity_count = [2, 2, 3]
    service_hours = [64, 86, 112]

    fig, ax1 = plt.subplots(figsize=(10.5, 5.2), dpi=220)
    ax2 = ax1.twinx()

    bars = ax1.bar(months, activity_count, color="#5B9CF1", width=0.75)
    ax2.plot(months, service_hours, color="#F04646", marker="o", linewidth=2.5, markersize=8)

    ax1.set_ylabel("活动数量", fontsize=12)
    ax2.set_ylabel("累计服务时长（小时）", fontsize=12)
    ax1.set_ylim(0, 3.4)
    ax2.set_ylim(60, 115)
    ax1.grid(axis="y", linestyle="--", alpha=0.25)
    for bar, value in zip(bars, activity_count):
        ax1.text(bar.get_x() + bar.get_width() / 2, value + 0.05, str(value), ha="center", va="bottom", fontsize=11)
    for x, y in zip(months, service_hours):
        ax2.text(x, y + 2, str(y), ha="center", va="bottom", fontsize=10, color="#B03030")

    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "monthly-stats.png", bbox_inches="tight")
    plt.close(fig)


def generate_assets():
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    _setup_style()
    generate_business_flow()
    generate_database_er()
    generate_system_architecture()
    generate_admin_role_split()
    generate_student_module_design()
    generate_admin_module_design()
    generate_page_data_linkage()
    generate_monthly_stats()


if __name__ == "__main__":
    generate_assets()
