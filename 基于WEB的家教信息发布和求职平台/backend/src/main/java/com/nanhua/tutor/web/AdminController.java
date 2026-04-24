package com.nanhua.tutor.web;

import com.nanhua.tutor.domain.TutorApplication;
import com.nanhua.tutor.domain.TutorDemand;
import com.nanhua.tutor.domain.TutorOrder;
import com.nanhua.tutor.domain.TutorProfile;
import com.nanhua.tutor.service.TutorPlatformService;
import jakarta.validation.constraints.NotNull;
import java.util.List;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@CrossOrigin
@RestController
@RequestMapping("/api/admin")
public class AdminController {
  private final TutorPlatformService service;
  private final ApiViewMapper mapper;

  public AdminController(TutorPlatformService service, ApiViewMapper mapper) {
    this.service = service;
    this.mapper = mapper;
  }

  @GetMapping("/profiles")
  List<TutorProfileView> profiles() {
    return service.allProfiles().stream().map(mapper::profile).toList();
  }

  @PostMapping("/{adminId}/profiles/{profileId}/audit")
  TutorProfileView auditProfile(@PathVariable Long adminId, @PathVariable Long profileId, @RequestBody AuditRequest request) {
    TutorProfile profile = service.approveTutorProfile(adminId, profileId, request.approved(), request.remark());
    return mapper.profile(profile);
  }

  @GetMapping("/demands")
  List<DemandView> demands() {
    return service.allDemands().stream().map(mapper::demand).toList();
  }

  @PostMapping("/{adminId}/demands/{demandId}/audit")
  DemandView auditDemand(@PathVariable Long adminId, @PathVariable Long demandId, @RequestBody AuditRequest request) {
    TutorDemand demand = service.auditDemand(adminId, demandId, request.approved(), request.remark());
    return mapper.demand(demand);
  }

  @GetMapping("/applications")
  List<ApplicationView> applications() {
    return service.allApplications().stream().map(mapper::application).toList();
  }

  @PostMapping("/{adminId}/applications/{applicationId}/review")
  ApplicationView reviewApplication(@PathVariable Long adminId, @PathVariable Long applicationId, @RequestBody AuditRequest request) {
    TutorApplication application = request.approved()
        ? service.approveApplication(adminId, applicationId, request.remark()).getApplication()
        : service.rejectApplication(adminId, applicationId, request.remark());
    return mapper.application(application);
  }

  @PostMapping("/{adminId}/applications/{applicationId}/approve")
  OrderView approveApplication(@PathVariable Long adminId, @PathVariable Long applicationId, @RequestBody RemarkRequest request) {
    TutorOrder order = service.approveApplication(adminId, applicationId, request.remark());
    return mapper.order(order);
  }

  @GetMapping("/orders")
  List<OrderView> orders() {
    return service.allOrders().stream().map(mapper::order).toList();
  }

  @GetMapping("/audits")
  List<AuditRecordView> audits() {
    return service.recentAudits().stream().map(mapper::audit).toList();
  }

  record AuditRequest(@NotNull Boolean approved, String remark) {
  }

  record RemarkRequest(String remark) {
  }
}
