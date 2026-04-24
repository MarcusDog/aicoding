package com.nanhua.tutor.web;

import com.nanhua.tutor.domain.AuditRecord;
import com.nanhua.tutor.domain.TutorApplication;
import com.nanhua.tutor.domain.TutorDemand;
import com.nanhua.tutor.domain.TutorOrder;
import com.nanhua.tutor.domain.TutorProfile;
import com.nanhua.tutor.domain.UserAccount;
import org.springframework.stereotype.Component;

@Component
public class ApiViewMapper {
  UserView user(UserAccount account) {
    return new UserView(
        account.getId(),
        account.getUsername(),
        account.getDisplayName(),
        account.getPhone(),
        account.getRole().name(),
        account.getStatus().name(),
        account.getCreatedAt()
    );
  }

  TutorProfileView profile(TutorProfile profile) {
    return new TutorProfileView(
        profile.getId(),
        profile.getUser().getId(),
        profile.getUser().getDisplayName(),
        profile.getSchool(),
        profile.getMajor(),
        profile.getSubjects(),
        profile.getIntroduction(),
        profile.getTeachingExperienceYears(),
        profile.getServiceMode(),
        profile.getResumeText(),
        profile.getResumeFileName(),
        profile.getResumeFileContentType(),
        profile.getResumeFileSize(),
        profile.getResumeFileName() == null ? null : "/api/catalog/tutors/" + profile.getId() + "/resume-file",
        profile.getStatus().name(),
        profile.getReviewRemark(),
        profile.getCreatedAt()
    );
  }

  DemandView demand(TutorDemand demand) {
    return new DemandView(
        demand.getId(),
        demand.getParent().getId(),
        demand.getParent().getDisplayName(),
        demand.getTitle(),
        demand.getSubject(),
        demand.getGradeLevel(),
        demand.getLocation(),
        demand.getBudgetMin(),
        demand.getBudgetMax(),
        demand.getSchedule(),
        demand.getDescription(),
        demand.getStatus().name(),
        demand.getReviewRemark(),
        demand.getCreatedAt()
    );
  }

  ApplicationView application(TutorApplication application) {
    return new ApplicationView(
        application.getId(),
        application.getDemand().getId(),
        application.getDemand().getTitle(),
        application.getTutor().getId(),
        application.getTutor().getDisplayName(),
        application.getCoverLetter(),
        application.getStatus().name(),
        application.getReviewRemark(),
        application.getCreatedAt()
    );
  }

  OrderView order(TutorOrder order) {
    return new OrderView(
        order.getId(),
        order.getDemand().getId(),
        order.getDemand().getTitle(),
        order.getParent().getDisplayName(),
        order.getTutor().getDisplayName(),
        order.getStatus().name(),
        order.getCreatedAt()
    );
  }

  AuditRecordView audit(AuditRecord audit) {
    return new AuditRecordView(
        audit.getId(),
        audit.getTargetType(),
        audit.getTargetId(),
        audit.getAction(),
        audit.getResult(),
        audit.getRemark(),
        audit.getReviewer() == null ? "" : audit.getReviewer().getDisplayName(),
        audit.getCreatedAt()
    );
  }
}
