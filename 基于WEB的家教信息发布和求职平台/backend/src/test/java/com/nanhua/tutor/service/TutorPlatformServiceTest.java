package com.nanhua.tutor.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.nanhua.tutor.domain.ApplicationStatus;
import com.nanhua.tutor.domain.AuditStatus;
import com.nanhua.tutor.domain.DemandStatus;
import com.nanhua.tutor.domain.OrderStatus;
import com.nanhua.tutor.domain.TutorApplication;
import com.nanhua.tutor.domain.TutorDemand;
import com.nanhua.tutor.domain.TutorOrder;
import com.nanhua.tutor.domain.TutorProfile;
import com.nanhua.tutor.domain.UserAccount;
import com.nanhua.tutor.domain.UserRole;
import java.math.BigDecimal;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.annotation.Transactional;

@SpringBootTest
@Transactional
class TutorPlatformServiceTest {
  @Autowired
  private TutorPlatformService service;

  @Test
  void parentDemandRequiresAdminAuditBeforeTutorsCanApply() {
    UserAccount admin = service.registerUser("admin_case1", "123456", "管理员", "18810000000", UserRole.ADMIN);
    UserAccount parent = service.registerUser("parent_case1", "123456", "家长", "18810000001", UserRole.PARENT);
    UserAccount tutor = service.registerUser("tutor_case1", "123456", "教员", "18810000002", UserRole.TUTOR);
    TutorProfile profile = service.submitTutorProfile(tutor.getId(), "南华大学", "数学", "数学", "认真负责", 2, "线上", "可提供系统化函数与几何复习资料");
    service.approveTutorProfile(admin.getId(), profile.getId(), true, "材料真实");

    TutorDemand demand = service.publishDemand(
        parent.getId(),
        "高一数学辅导",
        "数学",
        "高一",
        "衡阳",
        BigDecimal.valueOf(100),
        BigDecimal.valueOf(160),
        "周末",
        "提升函数基础"
    );

    assertThat(demand.getStatus()).isEqualTo(DemandStatus.PENDING_REVIEW);
    assertThatThrownBy(() -> service.applyForDemand(tutor.getId(), demand.getId(), "我可以胜任"))
        .isInstanceOf(BusinessException.class)
        .hasMessageContaining("当前需求不可申请");

    service.auditDemand(admin.getId(), demand.getId(), true, "内容合规");
    TutorApplication application = service.applyForDemand(tutor.getId(), demand.getId(), "有相关辅导经验");

    assertThat(application.getStatus()).isEqualTo(ApplicationStatus.SUBMITTED);
  }

  @Test
  void approvingApplicationCreatesActiveOrderAndMatchesDemand() {
    UserAccount admin = service.registerUser("admin_case2", "123456", "管理员", "18820000000", UserRole.ADMIN);
    UserAccount parent = service.registerUser("parent_case2", "123456", "家长", "18820000001", UserRole.PARENT);
    UserAccount tutor = service.registerUser("tutor_case2", "123456", "教员", "18820000002", UserRole.TUTOR);
    TutorProfile profile = service.submitTutorProfile(tutor.getId(), "南华大学", "物理", "物理", "擅长力学", 3, "线上+线下", "曾服务多名初中生完成力学与电学入门");
    assertThat(profile.getStatus()).isEqualTo(AuditStatus.PENDING);
    service.approveTutorProfile(admin.getId(), profile.getId(), true, "通过");
    TutorDemand demand = service.publishDemand(
        parent.getId(),
        "初二物理入门",
        "物理",
        "初二",
        "线上",
        BigDecimal.valueOf(90),
        BigDecimal.valueOf(130),
        "工作日晚上",
        "帮助建立知识框架"
    );
    service.auditDemand(admin.getId(), demand.getId(), true, "通过");
    TutorApplication application = service.applyForDemand(tutor.getId(), demand.getId(), "可线上辅导");

    TutorOrder order = service.approveApplication(admin.getId(), application.getId(), "匹配度高");

    assertThat(order.getStatus()).isEqualTo(OrderStatus.ACTIVE);
    assertThat(order.getDemand().getStatus()).isEqualTo(DemandStatus.MATCHED);
    assertThat(order.getTutor().getId()).isEqualTo(tutor.getId());
  }

  @Test
  void rejectingProfileAndDemandPersistsReviewRemark() {
    UserAccount admin = service.registerUser("admin_case3", "123456", "管理员", "18830000000", UserRole.ADMIN);
    UserAccount parent = service.registerUser("parent_case3", "123456", "家长", "18830000001", UserRole.PARENT);
    UserAccount tutor = service.registerUser("tutor_case3", "123456", "教员", "18830000002", UserRole.TUTOR);

    TutorProfile profile = service.submitTutorProfile(tutor.getId(), "南华大学", "英语", "英语", "待审核资料", 1, "线上", "准备补充英语竞赛和带课记录");
    TutorDemand demand = service.publishDemand(
        parent.getId(),
        "高二英语写作辅导",
        "英语",
        "高二",
        "衡阳",
        BigDecimal.valueOf(100),
        BigDecimal.valueOf(150),
        "周末上午",
        "希望提升写作与语法"
    );

    TutorProfile rejectedProfile = service.approveTutorProfile(admin.getId(), profile.getId(), false, "缺少有效资质说明");
    TutorDemand rejectedDemand = service.auditDemand(admin.getId(), demand.getId(), false, "需求描述不完整");

    assertThat(rejectedProfile.getStatus()).isEqualTo(AuditStatus.REJECTED);
    assertThat(rejectedProfile.getReviewRemark()).isEqualTo("缺少有效资质说明");
    assertThat(rejectedDemand.getStatus()).isEqualTo(DemandStatus.REJECTED);
    assertThat(rejectedDemand.getReviewRemark()).isEqualTo("需求描述不完整");
  }

  @Test
  void demandAndTutorProfileCanBeQueriedForDetailPages() {
    UserAccount parent = service.registerUser("parent_case4", "123456", "李家长", "18840000001", UserRole.PARENT);
    UserAccount tutor = service.registerUser("tutor_case4", "123456", "张教员", "18840000002", UserRole.TUTOR);

    TutorProfile profile = service.submitTutorProfile(tutor.getId(), "南华大学", "计算机科学与技术", "数学,物理", "有三年一对一辅导经验", 3, "线上+线下", "可按章节输出学习计划与周反馈");
    TutorDemand demand = service.publishDemand(
        parent.getId(),
        "初三数学冲刺辅导",
        "数学",
        "初三",
        "衡阳市石鼓区",
        BigDecimal.valueOf(120),
        BigDecimal.valueOf(160),
        "周六下午",
        "希望重点提升压轴题和函数综合题"
    );

    TutorProfile storedProfile = service.profileDetail(profile.getId());
    TutorDemand storedDemand = service.demandDetail(demand.getId());

    assertThat(storedProfile.getUser().getDisplayName()).isEqualTo("张教员");
    assertThat(storedProfile.getSchool()).isEqualTo("南华大学");
    assertThat(storedDemand.getParent().getDisplayName()).isEqualTo("李家长");
    assertThat(storedDemand.getDescription()).contains("压轴题");
  }

  @Test
  void rejectedTutorProfileCanBeRevisedAndSubmittedAgain() {
    UserAccount admin = service.registerUser("admin_case5", "123456", "管理员", "18850000000", UserRole.ADMIN);
    UserAccount tutor = service.registerUser("tutor_case5", "123456", "赵教员", "18850000002", UserRole.TUTOR);
    TutorProfile profile = service.submitTutorProfile(tutor.getId(), "南华大学", "数学", "数学", "资料过于简单", 1, "线上", "曾辅导同班同学完成期末复习");
    service.approveTutorProfile(admin.getId(), profile.getId(), false, "请补充教学经历");

    TutorProfile revised = service.resubmitTutorProfile(
        tutor.getId(),
        "南华大学",
        "数学与应用数学",
        "数学,物理",
        "补充两年初中数学一对一辅导经历，可提供阶段性学习反馈",
        2,
        "线上+线下",
        "2023年至今持续参与初中数学家教，擅长阶段性周报和错题整理"
    );

    assertThat(revised.getId()).isEqualTo(profile.getId());
    assertThat(revised.getStatus()).isEqualTo(AuditStatus.PENDING);
    assertThat(revised.getReviewRemark()).isNull();
    assertThat(revised.getMajor()).isEqualTo("数学与应用数学");
    assertThat(revised.getIntroduction()).contains("两年初中数学");
    assertThat(revised.getTeachingExperienceYears()).isEqualTo(2);
    assertThat(revised.getServiceMode()).isEqualTo("线上+线下");
    assertThat(revised.getResumeText()).contains("阶段性周报");
  }

  @Test
  void rejectedDemandCanBeRevisedAndSubmittedAgain() {
    UserAccount admin = service.registerUser("admin_case6", "123456", "管理员", "18860000000", UserRole.ADMIN);
    UserAccount parent = service.registerUser("parent_case6", "123456", "王家长", "18860000001", UserRole.PARENT);
    TutorDemand demand = service.publishDemand(
        parent.getId(),
        "英语辅导",
        "英语",
        "初二",
        "衡阳",
        BigDecimal.valueOf(80),
        BigDecimal.valueOf(120),
        "周末",
        "描述较少"
    );
    service.auditDemand(admin.getId(), demand.getId(), false, "请补充学生基础和具体目标");

    TutorDemand revised = service.resubmitDemand(
        parent.getId(),
        demand.getId(),
        "初二英语阅读与语法提升",
        "英语",
        "初二",
        "衡阳市雁峰区",
        BigDecimal.valueOf(100),
        BigDecimal.valueOf(150),
        "周六上午",
        "学生阅读理解较弱，希望重点提升语法、完形填空和阅读速度"
    );

    assertThat(revised.getId()).isEqualTo(demand.getId());
    assertThat(revised.getStatus()).isEqualTo(DemandStatus.PENDING_REVIEW);
    assertThat(revised.getReviewRemark()).isNull();
    assertThat(revised.getTitle()).isEqualTo("初二英语阅读与语法提升");
    assertThat(revised.getDescription()).contains("完形填空");
  }

  @Test
  void tutorProfileStoresResumeAndCommercialServiceFields() {
    UserAccount tutor = service.registerUser("tutor_case7", "123456", "周教员", "18870000002", UserRole.TUTOR);

    TutorProfile profile = service.submitTutorProfile(
        tutor.getId(),
        "南华大学",
        "信息与计算科学",
        "数学,英语",
        "擅长制定周学习计划",
        3,
        "线上+线下",
        "曾服务 12 名初高中学生，提供阶段测评、周学习反馈和家长沟通记录。"
    );

    assertThat(profile.getTeachingExperienceYears()).isEqualTo(3);
    assertThat(profile.getServiceMode()).isEqualTo("线上+线下");
    assertThat(profile.getResumeText()).contains("阶段测评");
  }
}
