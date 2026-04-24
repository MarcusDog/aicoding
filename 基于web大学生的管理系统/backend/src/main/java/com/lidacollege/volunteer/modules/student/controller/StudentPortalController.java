package com.lidacollege.volunteer.modules.student.controller;

import com.lidacollege.volunteer.common.api.ApiResponse;
import com.lidacollege.volunteer.modules.activity.entity.VolunteerActivity;
import com.lidacollege.volunteer.modules.hours.entity.ServiceHoursRecord;
import com.lidacollege.volunteer.modules.student.dto.CancelSignupRequest;
import com.lidacollege.volunteer.modules.student.dto.SignCodeRequest;
import com.lidacollege.volunteer.modules.student.dto.StudentProfileUpdateRequest;
import com.lidacollege.volunteer.modules.student.service.StudentPortalService;
import com.lidacollege.volunteer.modules.system.entity.MessageNotice;
import com.lidacollege.volunteer.modules.system.entity.Student;
import jakarta.validation.Valid;
import java.util.List;
import java.util.Map;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/student")
@RequiredArgsConstructor
public class StudentPortalController {

    private final StudentPortalService studentPortalService;

    @GetMapping("/home")
    public ApiResponse<Map<String, Object>> home() {
        return ApiResponse.ok(studentPortalService.homeData());
    }

    @GetMapping("/activities")
    public ApiResponse<List<VolunteerActivity>> activities(
        @RequestParam(required = false) String keyword,
        @RequestParam(required = false) String status
    ) {
        return ApiResponse.ok(studentPortalService.listActivities(keyword, status));
    }

    @GetMapping("/activities/{activityId}")
    public ApiResponse<Map<String, Object>> activityDetail(@PathVariable Long activityId) {
        return ApiResponse.ok(studentPortalService.activityDetail(activityId));
    }

    @PostMapping("/signups/{activityId}")
    public ApiResponse<Void> apply(@PathVariable Long activityId) {
        studentPortalService.applyActivity(activityId);
        return ApiResponse.ok("报名成功", null);
    }

    @PutMapping("/signups/{signupId}/cancel")
    public ApiResponse<Void> cancel(@PathVariable Long signupId, @Valid @RequestBody CancelSignupRequest request) {
        studentPortalService.cancelSignup(signupId, request);
        return ApiResponse.ok("取消报名成功", null);
    }

    @GetMapping("/signups")
    public ApiResponse<List<Map<String, Object>>> signups() {
        return ApiResponse.ok(studentPortalService.mySignups());
    }

    @PostMapping("/sign-in")
    public ApiResponse<Void> signIn(@Valid @RequestBody SignCodeRequest request) {
        studentPortalService.signIn(request);
        return ApiResponse.ok("签到成功", null);
    }

    @PostMapping("/sign-out")
    public ApiResponse<Void> signOut(@Valid @RequestBody SignCodeRequest request) {
        studentPortalService.signOut(request);
        return ApiResponse.ok("签退成功", null);
    }

    @GetMapping("/hours")
    public ApiResponse<List<ServiceHoursRecord>> hours() {
        return ApiResponse.ok(studentPortalService.myHours());
    }

    @GetMapping("/messages")
    public ApiResponse<List<MessageNotice>> messages() {
        return ApiResponse.ok(studentPortalService.myMessages());
    }

    @GetMapping("/profile")
    public ApiResponse<Student> profile() {
        return ApiResponse.ok(studentPortalService.myProfile());
    }

    @PutMapping("/profile")
    public ApiResponse<Void> updateProfile(@RequestBody StudentProfileUpdateRequest request) {
        studentPortalService.updateProfile(request);
        return ApiResponse.ok("个人信息更新成功", null);
    }
}
