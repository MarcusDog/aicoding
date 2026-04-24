package com.nanhua.tutor.web;

import com.nanhua.tutor.domain.TutorApplication;
import com.nanhua.tutor.domain.TutorDemand;
import com.nanhua.tutor.domain.TutorOrder;
import com.nanhua.tutor.domain.TutorProfile;
import com.nanhua.tutor.service.TutorPlatformService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import java.util.List;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestPart;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

@CrossOrigin
@RestController
@RequestMapping("/api/tutors")
public class TutorController {
  private final TutorPlatformService service;
  private final ApiViewMapper mapper;

  public TutorController(TutorPlatformService service, ApiViewMapper mapper) {
    this.service = service;
    this.mapper = mapper;
  }

  @PostMapping("/{tutorId}/profile")
  TutorProfileView submitProfile(@PathVariable Long tutorId, @Valid @RequestBody ProfileRequest request) {
    TutorProfile profile = service.submitTutorProfile(
        tutorId,
        request.school(),
        request.major(),
        request.subjects(),
        request.introduction(),
        request.teachingExperienceYears(),
        request.serviceMode(),
        request.resumeText()
    );
    return mapper.profile(profile);
  }

  @PutMapping("/{tutorId}/profile")
  TutorProfileView resubmitProfile(@PathVariable Long tutorId, @Valid @RequestBody ProfileRequest request) {
    TutorProfile profile = service.resubmitTutorProfile(
        tutorId,
        request.school(),
        request.major(),
        request.subjects(),
        request.introduction(),
        request.teachingExperienceYears(),
        request.serviceMode(),
        request.resumeText()
    );
    return mapper.profile(profile);
  }

  @PostMapping(path = "/{tutorId}/profile/resume-file", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
  TutorProfileView uploadResumeFile(@PathVariable Long tutorId, @RequestPart("file") MultipartFile file) {
    return mapper.profile(service.attachResumeFile(tutorId, file));
  }

  @GetMapping("/{tutorId}/profile")
  TutorProfileView profile(@PathVariable Long tutorId) {
    return mapper.profile(service.profileDetailByUserId(tutorId));
  }

  @GetMapping("/demands/open")
  List<DemandView> openDemands() {
    return service.openDemands().stream().map(mapper::demand).toList();
  }

  @PostMapping("/{tutorId}/applications")
  ApplicationView apply(@PathVariable Long tutorId, @Valid @RequestBody ApplicationRequest request) {
    TutorApplication application = service.applyForDemand(tutorId, request.demandId(), request.coverLetter());
    return mapper.application(application);
  }

  @GetMapping("/{tutorId}/applications")
  List<ApplicationView> applications(@PathVariable Long tutorId) {
    return service.tutorApplications(tutorId).stream().map(mapper::application).toList();
  }

  @GetMapping("/{tutorId}/orders")
  List<OrderView> orders(@PathVariable Long tutorId) {
    List<TutorOrder> orders = service.tutorOrders(tutorId);
    return orders.stream().map(mapper::order).toList();
  }

  record ProfileRequest(
      @NotBlank String school,
      @NotBlank String major,
      @NotBlank String subjects,
      @NotBlank String introduction,
      @Min(0)
      @NotNull Integer teachingExperienceYears,
      @NotBlank String serviceMode,
      @NotBlank String resumeText
  ) {
  }

  record ApplicationRequest(Long demandId, @NotBlank String coverLetter) {
  }
}
