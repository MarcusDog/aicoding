package com.nanhua.tutor.web;

import java.math.BigDecimal;
import java.time.LocalDateTime;

record UserView(
    Long id,
    String username,
    String displayName,
    String phone,
    String role,
    String status,
    LocalDateTime createdAt
) {
}

record TutorProfileView(
    Long id,
    Long userId,
    String userName,
    String school,
    String major,
    String subjects,
    String introduction,
    Integer teachingExperienceYears,
    String serviceMode,
    String resumeText,
    String resumeFileName,
    String resumeFileContentType,
    Long resumeFileSize,
    String resumeFileDownloadUrl,
    String status,
    String reviewRemark,
    LocalDateTime createdAt
) {
}

record DemandView(
    Long id,
    Long parentId,
    String parentName,
    String title,
    String subject,
    String gradeLevel,
    String location,
    BigDecimal budgetMin,
    BigDecimal budgetMax,
    String schedule,
    String description,
    String status,
    String reviewRemark,
    LocalDateTime createdAt
) {
}

record ApplicationView(
    Long id,
    Long demandId,
    String demandTitle,
    Long tutorId,
    String tutorName,
    String coverLetter,
    String status,
    String reviewRemark,
    LocalDateTime createdAt
) {
}

record OrderView(
    Long id,
    Long demandId,
    String demandTitle,
    String parentName,
    String tutorName,
    String status,
    LocalDateTime createdAt
) {
}

record AuditRecordView(
    Long id,
    String targetType,
    Long targetId,
    String action,
    String result,
    String remark,
    String reviewerName,
    LocalDateTime createdAt
) {
}
