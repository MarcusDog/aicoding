package com.nanhua.tutor.web;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class FrontendController {
  @GetMapping({
      "/",
      "/login",
      "/register",
      "/demands",
      "/demands/{id}",
      "/tutors",
      "/tutors/{id}",
      "/tutor-users/{userId}/profile",
      "/parent",
      "/tutor",
      "/admin"
  })
  String index() {
    return "forward:/index.html";
  }
}
