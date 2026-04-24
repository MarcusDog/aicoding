package com.nanhua.tutor.service;

import com.nanhua.tutor.domain.ApplicationStatus;
import com.nanhua.tutor.domain.AuditRecord;
import com.nanhua.tutor.domain.AuditStatus;
import com.nanhua.tutor.domain.DashboardSummary;
import com.nanhua.tutor.domain.DemandStatus;
import com.nanhua.tutor.domain.OrderStatus;
import com.nanhua.tutor.domain.TutorApplication;
import com.nanhua.tutor.domain.TutorDemand;
import com.nanhua.tutor.domain.TutorOrder;
import com.nanhua.tutor.domain.TutorProfile;
import com.nanhua.tutor.domain.UserAccount;
import com.nanhua.tutor.domain.UserRole;
import com.nanhua.tutor.repository.AuditRecordRepository;
import com.nanhua.tutor.repository.TutorApplicationRepository;
import com.nanhua.tutor.repository.TutorDemandRepository;
import com.nanhua.tutor.repository.TutorOrderRepository;
import com.nanhua.tutor.repository.TutorProfileRepository;
import com.nanhua.tutor.repository.UserAccountRepository;
import java.math.BigDecimal;
import java.util.List;
import java.util.Comparator;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional
public class TutorPlatformService {
  private final UserAccountRepository users;
  private final TutorProfileRepository profiles;
  private final TutorDemandRepository demands;
  private final TutorApplicationRepository applications;
  private final TutorOrderRepository orders;
  private final AuditRecordRepository audits;
  private final TutorResumeStorageService resumeStorage;

  public TutorPlatformService(
      UserAccountRepository users,
      TutorProfileRepository profiles,
      TutorDemandRepository demands,
      TutorApplicationRepository applications,
      TutorOrderRepository orders,
      AuditRecordRepository audits,
      TutorResumeStorageService resumeStorage
  ) {
    this.users = users;
    this.profiles = profiles;
    this.demands = demands;
    this.applications = applications;
    this.orders = orders;
    this.audits = audits;
    this.resumeStorage = resumeStorage;
  }

  public UserAccount registerUser(String username, String password, String displayName, String phone, UserRole role) {
    users.findByUsername(username).ifPresent(existing -> {
      throw new BusinessException("用户名已存在");
    });
    return users.save(new UserAccount(username, password, displayName, phone, role));
  }

  public UserAccount login(String username, String password) {
    UserAccount user = users.findByUsername(username)
        .orElseThrow(() -> new BusinessException("用户不存在"));
    if (!user.getPassword().equals(password)) {
      throw new BusinessException("密码错误");
    }
    return user;
  }

  public TutorProfile submitTutorProfile(
      Long tutorId,
      String school,
      String major,
      String subjects,
      String introduction,
      Integer teachingExperienceYears,
      String serviceMode,
      String resumeText
  ) {
    UserAccount tutor = requireUser(tutorId, UserRole.TUTOR);
    profiles.findByUser(tutor).ifPresent(existing -> {
      throw new BusinessException("教员资料已提交");
    });
    return profiles.save(new TutorProfile(
        tutor,
        school,
        major,
        subjects,
        introduction,
        teachingExperienceYears,
        serviceMode,
        resumeText
    ));
  }

  public TutorProfile resubmitTutorProfile(
      Long tutorId,
      String school,
      String major,
      String subjects,
      String introduction,
      Integer teachingExperienceYears,
      String serviceMode,
      String resumeText
  ) {
    UserAccount tutor = requireUser(tutorId, UserRole.TUTOR);
    TutorProfile profile = profiles.findByUser(tutor)
        .orElseThrow(() -> new BusinessException("教员资料不存在"));
    if (profile.getStatus() != AuditStatus.REJECTED) {
      throw new BusinessException("只有被驳回的教员资料才能重新提交");
    }
    profile.revise(school, major, subjects, introduction, teachingExperienceYears, serviceMode, resumeText);
    return profile;
  }

  public TutorProfile attachResumeFile(Long tutorId, org.springframework.web.multipart.MultipartFile file) {
    UserAccount tutor = requireUser(tutorId, UserRole.TUTOR);
    TutorProfile profile = profiles.findByUser(tutor)
        .orElseThrow(() -> new BusinessException("请先提交教员资料"));
    TutorResumeStorageService.StoredResume storedResume = resumeStorage.store(profile, file);
    profile.attachResumeFile(
        storedResume.fileName(),
        storedResume.filePath(),
        storedResume.contentType(),
        storedResume.fileSize()
    );
    return profile;
  }

  public TutorProfile approveTutorProfile(Long adminId, Long profileId, boolean approved, String remark) {
    UserAccount admin = requireUser(adminId, UserRole.ADMIN);
    TutorProfile profile = profiles.findById(profileId)
        .orElseThrow(() -> new BusinessException("教员资料不存在"));
    if (approved) {
      profile.approve(remark);
    } else {
      profile.reject(remark);
    }
    audits.save(new AuditRecord("TUTOR_PROFILE", profileId, "CERTIFICATION", approved ? "APPROVED" : "REJECTED", remark, admin));
    return profile;
  }

  public TutorDemand publishDemand(
      Long parentId,
      String title,
      String subject,
      String gradeLevel,
      String location,
      BigDecimal budgetMin,
      BigDecimal budgetMax,
      String schedule,
      String description
  ) {
    UserAccount parent = requireUser(parentId, UserRole.PARENT);
    if (budgetMin.compareTo(BigDecimal.ZERO) < 0 || budgetMax.compareTo(budgetMin) < 0) {
      throw new BusinessException("预算范围不合法");
    }
    return demands.save(new TutorDemand(parent, title, subject, gradeLevel, location, budgetMin, budgetMax, schedule, description));
  }

  public TutorDemand resubmitDemand(
      Long parentId,
      Long demandId,
      String title,
      String subject,
      String gradeLevel,
      String location,
      BigDecimal budgetMin,
      BigDecimal budgetMax,
      String schedule,
      String description
  ) {
    UserAccount parent = requireUser(parentId, UserRole.PARENT);
    TutorDemand demand = demands.findById(demandId)
        .orElseThrow(() -> new BusinessException("家教需求不存在"));
    if (!demand.getParent().getId().equals(parent.getId())) {
      throw new BusinessException("只能修改自己发布的需求");
    }
    if (demand.getStatus() != DemandStatus.REJECTED) {
      throw new BusinessException("只有被驳回的需求才能重新提交");
    }
    if (budgetMin.compareTo(BigDecimal.ZERO) < 0 || budgetMax.compareTo(budgetMin) < 0) {
      throw new BusinessException("预算范围不合法");
    }
    demand.revise(title, subject, gradeLevel, location, budgetMin, budgetMax, schedule, description);
    return demand;
  }

  public TutorDemand auditDemand(Long adminId, Long demandId, boolean approved, String remark) {
    UserAccount admin = requireUser(adminId, UserRole.ADMIN);
    TutorDemand demand = demands.findById(demandId)
        .orElseThrow(() -> new BusinessException("家教需求不存在"));
    if (approved) {
      demand.approve(remark);
    } else {
      demand.reject(remark);
    }
    audits.save(new AuditRecord("DEMAND", demandId, "DEMAND_REVIEW", approved ? "APPROVED" : "REJECTED", remark, admin));
    return demand;
  }

  public TutorApplication applyForDemand(Long tutorId, Long demandId, String coverLetter) {
    UserAccount tutor = requireUser(tutorId, UserRole.TUTOR);
    TutorProfile profile = profiles.findByUser(tutor)
        .orElseThrow(() -> new BusinessException("请先提交教员认证资料"));
    if (profile.getStatus() != AuditStatus.APPROVED) {
      throw new BusinessException("教员认证通过后才能申请接单");
    }
    TutorDemand demand = demands.findById(demandId)
        .orElseThrow(() -> new BusinessException("家教需求不存在"));
    if (demand.getStatus() != DemandStatus.OPEN) {
      throw new BusinessException("当前需求不可申请");
    }
    if (applications.existsByDemandAndTutor(demand, tutor)) {
      throw new BusinessException("不能重复申请同一需求");
    }
    return applications.save(new TutorApplication(demand, tutor, coverLetter));
  }

  public TutorOrder approveApplication(Long adminId, Long applicationId, String remark) {
    UserAccount admin = requireUser(adminId, UserRole.ADMIN);
    TutorApplication application = applications.findById(applicationId)
        .orElseThrow(() -> new BusinessException("接单申请不存在"));
    if (application.getStatus() != ApplicationStatus.SUBMITTED) {
      throw new BusinessException("申请已处理");
    }
    application.accept(remark);
    application.getDemand().markMatched();
    TutorOrder order = orders.save(new TutorOrder(application.getDemand(), application));
    audits.save(new AuditRecord("APPLICATION", applicationId, "APPLICATION_APPROVAL", "APPROVED", remark, admin));
    return order;
  }

  public TutorApplication rejectApplication(Long adminId, Long applicationId, String remark) {
    UserAccount admin = requireUser(adminId, UserRole.ADMIN);
    TutorApplication application = applications.findById(applicationId)
        .orElseThrow(() -> new BusinessException("接单申请不存在"));
    if (application.getStatus() != ApplicationStatus.SUBMITTED) {
      throw new BusinessException("申请已处理");
    }
    application.reject(remark);
    audits.save(new AuditRecord("APPLICATION", applicationId, "APPLICATION_APPROVAL", "REJECTED", remark, admin));
    return application;
  }

  @Transactional(readOnly = true)
  public DashboardSummary dashboard() {
    return new DashboardSummary(
        users.countByRole(UserRole.PARENT),
        users.countByRole(UserRole.TUTOR),
        users.countByRole(UserRole.ADMIN),
        demands.countByStatus(DemandStatus.OPEN),
        profiles.countByStatus(AuditStatus.PENDING),
        applications.countByStatus(ApplicationStatus.SUBMITTED),
        orders.countByStatus(OrderStatus.ACTIVE)
    );
  }

  @Transactional(readOnly = true)
  public List<TutorDemand> openDemands() {
    return demands.findByStatusOrderByCreatedAtDesc(DemandStatus.OPEN);
  }

  @Transactional(readOnly = true)
  public TutorDemand demandDetail(Long demandId) {
    return demands.findById(demandId)
        .orElseThrow(() -> new BusinessException("家教需求不存在"));
  }

  @Transactional(readOnly = true)
  public List<TutorDemand> parentDemands(Long parentId) {
    return demands.findByParentOrderByCreatedAtDesc(requireUser(parentId, UserRole.PARENT));
  }

  @Transactional(readOnly = true)
  public List<TutorApplication> tutorApplications(Long tutorId) {
    return applications.findByTutorOrderByCreatedAtDesc(requireUser(tutorId, UserRole.TUTOR));
  }

  @Transactional(readOnly = true)
  public TutorProfile profileDetail(Long profileId) {
    return profiles.findById(profileId)
        .orElseThrow(() -> new BusinessException("教员资料不存在"));
  }

  @Transactional(readOnly = true)
  public TutorProfile profileDetailByUserId(Long userId) {
    UserAccount tutor = requireUser(userId, UserRole.TUTOR);
    return profiles.findByUser(tutor)
        .orElseThrow(() -> new BusinessException("教员资料不存在"));
  }

  @Transactional(readOnly = true)
  public List<TutorProfile> approvedProfiles() {
    return profiles.findAll().stream()
        .filter(profile -> profile.getStatus() == AuditStatus.APPROVED)
        .sorted(Comparator.comparing(TutorProfile::getCreatedAt).reversed())
        .toList();
  }

  @Transactional(readOnly = true)
  public List<TutorOrder> parentOrders(Long parentId) {
    return orders.findByParentOrderByCreatedAtDesc(requireUser(parentId, UserRole.PARENT));
  }

  @Transactional(readOnly = true)
  public List<TutorOrder> tutorOrders(Long tutorId) {
    return orders.findByTutorOrderByCreatedAtDesc(requireUser(tutorId, UserRole.TUTOR));
  }

  @Transactional(readOnly = true)
  public List<TutorProfile> allProfiles() {
    return profiles.findAll();
  }

  @Transactional(readOnly = true)
  public List<TutorDemand> allDemands() {
    return demands.findAll();
  }

  @Transactional(readOnly = true)
  public List<TutorApplication> allApplications() {
    return applications.findAll();
  }

  @Transactional(readOnly = true)
  public List<TutorOrder> allOrders() {
    return orders.findAll();
  }

  @Transactional(readOnly = true)
  public List<AuditRecord> recentAudits() {
    return audits.findTop20ByOrderByCreatedAtDesc();
  }

  private UserAccount requireUser(Long userId, UserRole role) {
    UserAccount user = users.findById(userId)
        .orElseThrow(() -> new BusinessException("用户不存在"));
    if (user.getRole() != role) {
      throw new BusinessException("当前用户角色无权操作");
    }
    return user;
  }
}
