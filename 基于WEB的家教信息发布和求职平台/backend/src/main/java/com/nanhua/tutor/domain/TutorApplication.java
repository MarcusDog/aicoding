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
import java.time.LocalDateTime;

@Entity
public class TutorApplication {
  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;
  @ManyToOne(optional = false)
  @JoinColumn(name = "demand_id")
  private TutorDemand demand;
  @ManyToOne(optional = false)
  @JoinColumn(name = "tutor_id")
  private UserAccount tutor;
  @Column(length = 1000)
  private String coverLetter;
  @Column(length = 500)
  private String reviewRemark;
  @Enumerated(EnumType.STRING)
  private ApplicationStatus status = ApplicationStatus.SUBMITTED;
  private LocalDateTime createdAt = LocalDateTime.now();

  protected TutorApplication() {
  }

  public TutorApplication(TutorDemand demand, UserAccount tutor, String coverLetter) {
    this.demand = demand;
    this.tutor = tutor;
    this.coverLetter = coverLetter;
  }

  public Long getId() {
    return id;
  }

  public TutorDemand getDemand() {
    return demand;
  }

  public UserAccount getTutor() {
    return tutor;
  }

  public String getCoverLetter() {
    return coverLetter;
  }

  public ApplicationStatus getStatus() {
    return status;
  }

  public String getReviewRemark() {
    return reviewRemark;
  }

  public LocalDateTime getCreatedAt() {
    return createdAt;
  }

  public void accept(String remark) {
    this.reviewRemark = remark;
    this.status = ApplicationStatus.ACCEPTED;
  }

  public void reject(String remark) {
    this.reviewRemark = remark;
    this.status = ApplicationStatus.REJECTED;
  }
}
