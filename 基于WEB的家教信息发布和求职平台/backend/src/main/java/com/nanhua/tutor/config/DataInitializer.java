package com.nanhua.tutor.config;

import com.nanhua.tutor.domain.TutorDemand;
import com.nanhua.tutor.domain.TutorProfile;
import com.nanhua.tutor.domain.UserAccount;
import com.nanhua.tutor.domain.UserRole;
import com.nanhua.tutor.service.TutorPlatformService;
import java.math.BigDecimal;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class DataInitializer {
  @Bean
  CommandLineRunner seedDemoData(TutorPlatformService service) {
    return args -> {
      try {
        UserAccount admin = service.registerUser("admin", "123456", "管理员", "18800000000", UserRole.ADMIN);
        UserAccount parent = service.registerUser("parent", "123456", "张女士", "18800000001", UserRole.PARENT);
        UserAccount tutor = service.registerUser("tutor", "123456", "李同学", "18800000002", UserRole.TUTOR);
        UserAccount tutorPending = service.registerUser("tutor_pending", "123456", "陈同学", "18800000003", UserRole.TUTOR);

        TutorProfile profile = service.submitTutorProfile(
            tutor.getId(),
            "南华大学",
            "信息与计算科学",
            "数学,物理,英语",
            "擅长初高中数学与学习规划。",
            3,
            "线上+线下",
            "连续三年提供中学数学与英语辅导，支持课后反馈、阶段测评和家长沟通。"
        );
        service.approveTutorProfile(admin.getId(), profile.getId(), true, "示例数据自动认证");
        service.submitTutorProfile(
            tutorPending.getId(),
            "衡阳师范学院",
            "英语",
            "英语",
            "正在申请成为平台认证教员。",
            1,
            "线上",
            "可提供英语阅读与口语基础训练，已准备纸质简历和成绩证明。"
        );

        TutorDemand demand = service.publishDemand(
            parent.getId(),
            "初三数学周末提高",
            "数学",
            "初三",
            "衡阳市蒸湘区",
            BigDecimal.valueOf(120),
            BigDecimal.valueOf(180),
            "周六下午",
            "希望教员有耐心，能帮助孩子梳理函数与几何题型。"
        );
        service.auditDemand(admin.getId(), demand.getId(), true, "示例需求审核通过");
      } catch (RuntimeException ignored) {
        // Re-running against a persistent database should not duplicate seed rows.
      }
    };
  }
}
