package com.nanhua.tutor.web;

import com.nanhua.tutor.domain.TutorProfile;
import com.nanhua.tutor.service.TutorResumeStorageService;
import com.nanhua.tutor.service.TutorPlatformService;
import java.nio.charset.StandardCharsets;
import java.util.List;
import org.springframework.core.io.Resource;
import org.springframework.http.ContentDisposition;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@CrossOrigin
@RestController
@RequestMapping("/api/catalog")
public class CatalogController {
  private final TutorPlatformService service;
  private final TutorResumeStorageService resumeStorage;
  private final ApiViewMapper mapper;

  public CatalogController(TutorPlatformService service, TutorResumeStorageService resumeStorage, ApiViewMapper mapper) {
    this.service = service;
    this.resumeStorage = resumeStorage;
    this.mapper = mapper;
  }

  @GetMapping("/demands/open")
  List<DemandView> openDemands() {
    return service.openDemands().stream().map(mapper::demand).toList();
  }

  @GetMapping("/demands/{demandId}")
  DemandView demandDetail(@PathVariable Long demandId) {
    return mapper.demand(service.demandDetail(demandId));
  }

  @GetMapping("/tutors")
  List<TutorProfileView> approvedTutors() {
    return service.approvedProfiles().stream().map(mapper::profile).toList();
  }

  @GetMapping("/tutors/{profileId}")
  TutorProfileView profileDetail(@PathVariable Long profileId) {
    return mapper.profile(service.profileDetail(profileId));
  }

  @GetMapping("/tutor-users/{tutorUserId}/profile")
  TutorProfileView profileByTutorUser(@PathVariable Long tutorUserId) {
    return mapper.profile(service.profileDetailByUserId(tutorUserId));
  }

  @GetMapping("/tutors/{profileId}/resume-file")
  ResponseEntity<Resource> resumeFile(@PathVariable Long profileId) {
    TutorProfile profile = service.profileDetail(profileId);
    Resource resource = resumeStorage.loadAsResource(profile);
    MediaType mediaType = profile.getResumeFileContentType() == null
        ? MediaType.APPLICATION_OCTET_STREAM
        : MediaType.parseMediaType(profile.getResumeFileContentType());
    return ResponseEntity.ok()
        .contentType(mediaType)
        .header(
            HttpHeaders.CONTENT_DISPOSITION,
            ContentDisposition.attachment()
                .filename(profile.getResumeFileName(), StandardCharsets.UTF_8)
                .build()
                .toString()
        )
        .body(resource);
  }
}
