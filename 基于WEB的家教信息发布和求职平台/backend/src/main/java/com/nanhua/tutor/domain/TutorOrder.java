package com.nanhua.tutor.domain;

import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.OneToOne;
import java.time.LocalDateTime;

@Entity
public class TutorOrder {
  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;
  @OneToOne(optional = false)
  @JoinColumn(name = "demand_id")
  private TutorDemand demand;
  @OneToOne(optional = false)
  @JoinColumn(name = "application_id")
  private TutorApplication application;
  @ManyToOne(optional = false)
  @JoinColumn(name = "parent_id")
  private UserAccount parent;
  @ManyToOne(optional = false)
  @JoinColumn(name = "tutor_id")
  private UserAccount tutor;
  @Enumerated(EnumType.STRING)
  private OrderStatus status = OrderStatus.ACTIVE;
  private LocalDateTime createdAt = LocalDateTime.now();

  protected TutorOrder() {
  }

  public TutorOrder(TutorDemand demand, TutorApplication application) {
    this.demand = demand;
    this.application = application;
    this.parent = demand.getParent();
    this.tutor = application.getTutor();
  }

  public Long getId() {
    return id;
  }

  public TutorDemand getDemand() {
    return demand;
  }

  public TutorApplication getApplication() {
    return application;
  }

  public UserAccount getParent() {
    return parent;
  }

  public UserAccount getTutor() {
    return tutor;
  }

  public OrderStatus getStatus() {
    return status;
  }

  public LocalDateTime getCreatedAt() {
    return createdAt;
  }
}
