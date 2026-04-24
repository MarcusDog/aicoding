package com.nanhua.tutor.web;

import com.nanhua.tutor.domain.UserRole;
import com.nanhua.tutor.service.BusinessException;
import com.nanhua.tutor.service.TutorPlatformService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@CrossOrigin
@RestController
@RequestMapping("/api/auth")
public class AuthController {
  private final TutorPlatformService service;
  private final ApiViewMapper mapper;

  public AuthController(TutorPlatformService service, ApiViewMapper mapper) {
    this.service = service;
    this.mapper = mapper;
  }

  @PostMapping("/login")
  UserView login(@Valid @RequestBody LoginRequest request) {
    return mapper.user(service.login(request.username(), request.password()));
  }

  @PostMapping("/register")
  UserView register(@Valid @RequestBody RegisterRequest request) {
    return mapper.user(service.registerUser(
        request.username(),
        request.password(),
        request.displayName(),
        request.phone(),
        parseRole(request.role())
    ));
  }

  private UserRole parseRole(String role) {
    try {
      UserRole parsed = UserRole.valueOf(role);
      if (parsed == UserRole.ADMIN) {
        throw new BusinessException("注册角色不合法");
      }
      return parsed;
    } catch (IllegalArgumentException ex) {
      throw new BusinessException("注册角色不合法");
    }
  }

  record LoginRequest(@NotBlank String username, @NotBlank String password) {
  }

  record RegisterRequest(
      @NotBlank String username,
      @NotBlank String password,
      @NotBlank String displayName,
      @NotBlank String phone,
      @NotBlank String role
  ) {
  }
}
