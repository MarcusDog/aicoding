package com.nanhua.tutor.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import java.time.LocalDateTime;

@Entity
public class AuditRecord {
  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;
  private String targetType;
  private Long targetId;
  private String action;
  private String result;
  @Column(length = 1000)
  private String remark;
  @ManyToOne
  @JoinColumn(name = "reviewer_id")
  private UserAccount reviewer;
  private LocalDateTime createdAt = LocalDateTime.now();

  protected AuditRecord() {
  }

  public AuditRecord(String targetType, Long targetId, String action, String result, String remark, UserAccount reviewer) {
    this.targetType = targetType;
    this.targetId = targetId;
    this.action = action;
    this.result = result;
    this.remark = remark;
    this.reviewer = reviewer;
  }

  public Long getId() {
    return id;
  }

  public String getTargetType() {
    return targetType;
  }

  public Long getTargetId() {
    return targetId;
  }

  public String getAction() {
    return action;
  }

  public String getResult() {
    return result;
  }

  public String getRemark() {
    return remark;
  }

  public UserAccount getReviewer() {
    return reviewer;
  }

  public LocalDateTime getCreatedAt() {
    return createdAt;
  }
}
