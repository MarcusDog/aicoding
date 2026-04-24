package com.nanhua.tutor.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
public class TutorDemand {
  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;
  @ManyToOne(optional = false)
  @JoinColumn(name = "parent_id")
  private UserAccount parent;
  private String title;
  private String subject;
  private String gradeLevel;
  private String location;
  private BigDecimal budgetMin;
  private BigDecimal budgetMax;
  private String schedule;
  @Column(length = 1000)
  private String description;
  @Column(length = 500)
  private String reviewRemark;
  @Enumerated(EnumType.STRING)
  private DemandStatus status = DemandStatus.PENDING_REVIEW;
  private LocalDateTime createdAt = LocalDateTime.now();

  protected TutorDemand() {
  }

  public TutorDemand(
      UserAccount parent,
      String title,
      String subject,
      String gradeLevel,
      String location,
      BigDecimal budgetMin,
      BigDecimal budgetMax,
      String schedule,
      String description
  ) {
    this.parent = parent;
    this.title = title;
    this.subject = subject;
    this.gradeLevel = gradeLevel;
    this.location = location;
    this.budgetMin = budgetMin;
    this.budgetMax = budgetMax;
    this.schedule = schedule;
    this.description = description;
  }

  public Long getId() {
    return id;
  }

  public UserAccount getParent() {
    return parent;
  }

  public String getTitle() {
    return title;
  }

  public String getSubject() {
    return subject;
  }

  public String getGradeLevel() {
    return gradeLevel;
  }

  public String getLocation() {
    return location;
  }

  public BigDecimal getBudgetMin() {
    return budgetMin;
  }

  public BigDecimal getBudgetMax() {
    return budgetMax;
  }

  public String getSchedule() {
    return schedule;
  }

  public String getDescription() {
    return description;
  }

  public DemandStatus getStatus() {
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
    this.status = DemandStatus.OPEN;
  }

  public void reject(String remark) {
    this.reviewRemark = remark;
    this.status = DemandStatus.REJECTED;
  }

  public void markMatched() {
    this.status = DemandStatus.MATCHED;
  }

  public void revise(
      String title,
      String subject,
      String gradeLevel,
      String location,
      BigDecimal budgetMin,
      BigDecimal budgetMax,
      String schedule,
      String description
  ) {
    this.title = title;
    this.subject = subject;
    this.gradeLevel = gradeLevel;
    this.location = location;
    this.budgetMin = budgetMin;
    this.budgetMax = budgetMax;
    this.schedule = schedule;
    this.description = description;
    this.reviewRemark = null;
    this.status = DemandStatus.PENDING_REVIEW;
  }
}
