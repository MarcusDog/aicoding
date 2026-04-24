package com.lidacollege.volunteer.modules.admin.controller;

import com.lidacollege.volunteer.common.api.ApiResponse;
import com.lidacollege.volunteer.modules.activity.entity.VolunteerActivity;
import com.lidacollege.volunteer.modules.admin.dto.ActivitySaveRequest;
import com.lidacollege.volunteer.modules.admin.dto.AdminSaveRequest;
import com.lidacollege.volunteer.modules.admin.dto.FixSignRequest;
import com.lidacollege.volunteer.modules.admin.dto.HoursUpdateRequest;
import com.lidacollege.volunteer.modules.admin.dto.NoticeSaveRequest;
import com.lidacollege.volunteer.modules.admin.dto.ReviewRequest;
import com.lidacollege.volunteer.modules.admin.dto.StudentSaveRequest;
import com.lidacollege.volunteer.modules.admin.service.AdminPortalService;
import com.lidacollege.volunteer.modules.system.entity.AdminUser;
import com.lidacollege.volunteer.modules.system.entity.Notice;
import com.lidacollege.volunteer.modules.system.entity.Student;
import jakarta.validation.Valid;
import java.util.List;
import java.util.Map;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/admin")
@RequiredArgsConstructor
public class AdminPortalController {

    private final AdminPortalService adminPortalService;

    @GetMapping("/dashboard")
    public ApiResponse<Map<String, Object>> dashboard() {
        return ApiResponse.ok(adminPortalService.dashboard());
    }

    @GetMapping("/students")
    public ApiResponse<List<Student>> students() {
        return ApiResponse.ok(adminPortalService.listStudents());
    }

    @PostMapping("/students")
    public ApiResponse<Void> createStudent(@RequestBody StudentSaveRequest request) {
        adminPortalService.saveStudent(null, request);
        return ApiResponse.ok("学生创建成功", null);
    }

    @PutMapping("/students/{id}")
    public ApiResponse<Void> updateStudent(@PathVariable Long id, @RequestBody StudentSaveRequest request) {
        adminPortalService.saveStudent(id, request);
        return ApiResponse.ok("学生更新成功", null);
    }

    @GetMapping("/admin-users")
    public ApiResponse<List<AdminUser>> admins() {
        return ApiResponse.ok(adminPortalService.listAdmins());
    }

    @PostMapping("/admin-users")
    public ApiResponse<Void> createAdmin(@RequestBody AdminSaveRequest request) {
        adminPortalService.saveAdmin(null, request);
        return ApiResponse.ok("管理员创建成功", null);
    }

    @PutMapping("/admin-users/{id}")
    public ApiResponse<Void> updateAdmin(@PathVariable Long id, @RequestBody AdminSaveRequest request) {
        adminPortalService.saveAdmin(id, request);
        return ApiResponse.ok("管理员更新成功", null);
    }

    @GetMapping("/activities")
    public ApiResponse<List<VolunteerActivity>> activities() {
        return ApiResponse.ok(adminPortalService.listActivities());
    }

    @PostMapping("/activities")
    public ApiResponse<Void> createActivity(@Valid @RequestBody ActivitySaveRequest request) {
        adminPortalService.saveActivity(null, request);
        return ApiResponse.ok("活动创建成功", null);
    }

    @PutMapping("/activities/{id}")
    public ApiResponse<Void> updateActivity(@PathVariable Long id, @Valid @RequestBody ActivitySaveRequest request) {
        adminPortalService.saveActivity(id, request);
        return ApiResponse.ok("活动更新成功", null);
    }

    @PostMapping("/activities/{id}/publish")
    public ApiResponse<Void> publishActivity(@PathVariable Long id) {
        adminPortalService.publishActivity(id);
        return ApiResponse.ok("活动发布成功", null);
    }

    @PostMapping("/activities/{id}/cancel")
    public ApiResponse<Void> cancelActivity(@PathVariable Long id) {
        adminPortalService.cancelActivity(id);
        return ApiResponse.ok("活动取消成功", null);
    }

    @GetMapping("/signups")
    public ApiResponse<List<Map<String, Object>>> signups() {
        return ApiResponse.ok(adminPortalService.listSignups());
    }

    @PostMapping("/signups/{id}/approve")
    public ApiResponse<Void> approveSignup(@PathVariable Long id, @RequestBody ReviewRequest request) {
        adminPortalService.approveSignup(id, request);
        return ApiResponse.ok("审核通过成功", null);
    }

    @PostMapping("/signups/{id}/reject")
    public ApiResponse<Void> rejectSignup(@PathVariable Long id, @RequestBody ReviewRequest request) {
        adminPortalService.rejectSignup(id, request);
        return ApiResponse.ok("驳回成功", null);
    }

    @GetMapping("/signs")
    public ApiResponse<List<Map<String, Object>>> signs() {
        return ApiResponse.ok(adminPortalService.listSigns());
    }

    @PostMapping("/signs/{id}/fix")
    public ApiResponse<Void> fixSign(@PathVariable Long id, @RequestBody FixSignRequest request) {
        adminPortalService.fixSign(id, request);
        return ApiResponse.ok("签到补录成功", null);
    }

    @GetMapping("/hours")
    public ApiResponse<List<Map<String, Object>>> hours() {
        return ApiResponse.ok(adminPortalService.listHours());
    }

    @PostMapping("/hours/{id}/confirm")
    public ApiResponse<Void> confirmHours(@PathVariable Long id, @RequestBody HoursUpdateRequest request) {
        adminPortalService.confirmHours(id, request);
        return ApiResponse.ok("时长确认成功", null);
    }

    @PostMapping("/hours/{id}/revoke")
    public ApiResponse<Void> revokeHours(@PathVariable Long id, @RequestBody HoursUpdateRequest request) {
        adminPortalService.revokeHours(id, request);
        return ApiResponse.ok("时长撤销成功", null);
    }

    @GetMapping("/notices")
    public ApiResponse<List<Notice>> notices() {
        return ApiResponse.ok(adminPortalService.listNotices());
    }

    @PostMapping("/notices")
    public ApiResponse<Void> createNotice(@RequestBody NoticeSaveRequest request) {
        adminPortalService.saveNotice(null, request);
        return ApiResponse.ok("公告发布成功", null);
    }

    @PutMapping("/notices/{id}")
    public ApiResponse<Void> updateNotice(@PathVariable Long id, @RequestBody NoticeSaveRequest request) {
        adminPortalService.saveNotice(id, request);
        return ApiResponse.ok("公告更新成功", null);
    }

    @GetMapping("/reports/activity")
    public ApiResponse<Map<String, Object>> activityReport() {
        return ApiResponse.ok(adminPortalService.activityReport());
    }

    @GetMapping("/reports/student-hours")
    public ApiResponse<Map<String, Object>> studentHoursReport() {
        return ApiResponse.ok(adminPortalService.studentHoursReport());
    }

    @GetMapping("/reports/monthly")
    public ApiResponse<Map<String, Object>> monthlyReport() {
        return ApiResponse.ok(adminPortalService.monthlyReport());
    }

    @GetMapping("/reports/export/activity")
    public ResponseEntity<String> exportActivity() {
        return csvResponse("activity-report.csv", adminPortalService.exportActivityCsv());
    }

    @GetMapping("/reports/export/student-hours")
    public ResponseEntity<String> exportStudentHours() {
        return csvResponse("student-hours-report.csv", adminPortalService.exportStudentHoursCsv());
    }

    private ResponseEntity<String> csvResponse(String filename, String body) {
        return ResponseEntity.ok()
            .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=" + filename)
            .contentType(MediaType.parseMediaType("text/csv;charset=UTF-8"))
            .body(body);
    }
}
