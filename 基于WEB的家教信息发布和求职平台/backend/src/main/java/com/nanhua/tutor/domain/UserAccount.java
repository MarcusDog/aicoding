package com.nanhua.tutor.domain;

import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import java.time.LocalDateTime;

@Entity
public class UserAccount {
  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;
  private String username;
  private String password;
  private String displayName;
  private String phone;
  @Enumerated(EnumType.STRING)
  private UserRole role;
  @Enumerated(EnumType.STRING)
  private AccountStatus status = AccountStatus.ACTIVE;
  private LocalDateTime createdAt = LocalDateTime.now();

  protected UserAccount() {
  }

  public UserAccount(String username, String password, String displayName, String phone, UserRole role) {
    this.username = username;
    this.password = password;
    this.displayName = displayName;
    this.phone = phone;
    this.role = role;
  }

  public Long getId() {
    return id;
  }

  public String getUsername() {
    return username;
  }

  public String getPassword() {
    return password;
  }

  public String getDisplayName() {
    return displayName;
  }

  public String getPhone() {
    return phone;
  }

  public UserRole getRole() {
    return role;
  }

  public AccountStatus getStatus() {
    return status;
  }

  public LocalDateTime getCreatedAt() {
    return createdAt;
  }

  public void disable() {
    this.status = AccountStatus.DISABLED;
  }
}
