package com.nanhua.tutor.web;

import com.nanhua.tutor.domain.DashboardSummary;
import com.nanhua.tutor.service.TutorPlatformService;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@CrossOrigin
@RestController
@RequestMapping("/api/dashboard")
public class DashboardController {
  private final TutorPlatformService service;

  public DashboardController(TutorPlatformService service) {
    this.service = service;
  }

  @GetMapping
  DashboardSummary dashboard() {
    return service.dashboard();
  }
}
