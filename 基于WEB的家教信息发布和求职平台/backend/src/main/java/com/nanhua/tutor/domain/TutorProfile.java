package com.nanhua.tutor.domain;

import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.Column;
import jakarta.persistence.OneToOne;
import java.time.LocalDateTime;

@Entity
public class TutorProfile {
  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;
  @OneToOne(optional = false)
  @JoinColumn(name = "user_id")
  private UserAccount user;
  private String school;
  private String major;
  private String subjects;
  private String introduction;
  private Integer teachingExperienceYears;
  private String serviceMode;
  @Column(length = 3000)
  private String resumeText;
  private String resumeFileName;
  private String resumeFilePath;
  private String resumeFileContentType;
  private Long resumeFileSize;
  @Column(length = 500)
  private String reviewRemark;
  @Enumerated(EnumType.STRING)
  private AuditStatus status = AuditStatus.PENDING;
  private LocalDateTime createdAt = LocalDateTime.now();

  protected TutorProfile() {
  }

  public TutorProfile(
      UserAccount user,
      String school,
      String major,
      String subjects,
      String introduction,
      Integer teachingExperienceYears,
      String serviceMode,
      String resumeText
  ) {
    this.user = user;
    this.school = school;
    this.major = major;
    this.subjects = subjects;
    this.introduction = introduction;
    this.teachingExperienceYears = teachingExperienceYears;
    this.serviceMode = serviceMode;
    this.resumeText = resumeText;
  }

  public Long getId() {
    return id;
  }

  public UserAccount getUser() {
    return user;
  }

  public String getSchool() {
    return school;
  }

  public String getMajor() {
    return major;
  }

  public String getSubjects() {
    return subjects;
  }

  public String getIntroduction() {
    return introduction;
  }

  public Integer getTeachingExperienceYears() {
    return teachingExperienceYears;
  }

  public String getServiceMode() {
    return serviceMode;
  }

  public String getResumeText() {
    return resumeText;
  }

  public String getResumeFileName() {
    return resumeFileName;
  }

  public String getResumeFilePath() {
    return resumeFilePath;
  }

  public String getResumeFileContentType() {
    return resumeFileContentType;
  }

  public Long getResumeFileSize() {
    return resumeFileSize;
  }

  public AuditStatus getStatus() {
    return status;
  }

  public String getReviewRemark() {
    return reviewRemark;
  }

  public LocalDateTime getCreatedAt() {
    return createdAt;
  }

  public void approve(String remark) {
    this.reviewRemark = remark;
    this.status = AuditStatus.APPROVED;
  }

  public void reject(String remark) {
    this.reviewRemark = remark;
    this.status = AuditStatus.REJECTED;
  }

  public void revise(
      String school,
      String major,
      String subjects,
      String introduction,
      Integer teachingExperienceYears,
      String serviceMode,
      String resumeText
  ) {
    this.school = school;
    this.major = major;
    this.subjects = subjects;
    this.introduction = introduction;
    this.teachingExperienceYears = teachingExperienceYears;
    this.serviceMode = serviceMode;
    this.resumeText = resumeText;
    this.reviewRemark = null;
    this.status = AuditStatus.PENDING;
  }

  public void attachResumeFile(String resumeFileName, String resumeFilePath, String resumeFileContentType, Long resumeFileSize) {
    this.resumeFileName = resumeFileName;
    this.resumeFilePath = resumeFilePath;
    this.resumeFileContentType = resumeFileContentType;
    this.resumeFileSize = resumeFileSize;
  }
}
