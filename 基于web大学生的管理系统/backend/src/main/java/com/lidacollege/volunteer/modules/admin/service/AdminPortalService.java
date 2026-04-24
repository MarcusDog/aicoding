package com.lidacollege.volunteer.modules.admin.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.lidacollege.volunteer.common.exception.BusinessException;
import com.lidacollege.volunteer.common.security.SecurityHelper;
import com.lidacollege.volunteer.common.util.PasswordUtils;
import com.lidacollege.volunteer.modules.activity.entity.VolunteerActivity;
import com.lidacollege.volunteer.modules.activity.mapper.VolunteerActivityMapper;
import com.lidacollege.volunteer.modules.admin.dto.ActivitySaveRequest;
import com.lidacollege.volunteer.modules.admin.dto.AdminSaveRequest;
import com.lidacollege.volunteer.modules.admin.dto.FixSignRequest;
import com.lidacollege.volunteer.modules.admin.dto.HoursUpdateRequest;
import com.lidacollege.volunteer.modules.admin.dto.NoticeSaveRequest;
import com.lidacollege.volunteer.modules.admin.dto.ReviewRequest;
import com.lidacollege.volunteer.modules.admin.dto.StudentSaveRequest;
import com.lidacollege.volunteer.modules.hours.entity.ServiceHoursRecord;
import com.lidacollege.volunteer.modules.hours.mapper.ServiceHoursRecordMapper;
import com.lidacollege.volunteer.modules.sign.entity.ActivitySign;
import com.lidacollege.volunteer.modules.sign.mapper.ActivitySignMapper;
import com.lidacollege.volunteer.modules.signup.entity.ActivitySignup;
import com.lidacollege.volunteer.modules.signup.mapper.ActivitySignupMapper;
import com.lidacollege.volunteer.modules.system.entity.AdminUser;
import com.lidacollege.volunteer.modules.system.entity.MessageNotice;
import com.lidacollege.volunteer.modules.system.entity.Notice;
import com.lidacollege.volunteer.modules.system.entity.OperationLog;
import com.lidacollege.volunteer.modules.system.entity.Student;
import com.lidacollege.volunteer.modules.system.entity.SysUser;
import com.lidacollege.volunteer.modules.system.mapper.AdminUserMapper;
import com.lidacollege.volunteer.modules.system.mapper.MessageNoticeMapper;
import com.lidacollege.volunteer.modules.system.mapper.NoticeMapper;
import com.lidacollege.volunteer.modules.system.mapper.OperationLogMapper;
import com.lidacollege.volunteer.modules.system.mapper.StudentMapper;
import com.lidacollege.volunteer.modules.system.mapper.SysUserMapper;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.YearMonth;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;
import java.util.stream.Collectors;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class AdminPortalService {

    private final StudentMapper studentMapper;
    private final AdminUserMapper adminUserMapper;
    private final SysUserMapper sysUserMapper;
    private final VolunteerActivityMapper volunteerActivityMapper;
    private final ActivitySignupMapper activitySignupMapper;
    private final ActivitySignMapper activitySignMapper;
    private final ServiceHoursRecordMapper serviceHoursRecordMapper;
    private final NoticeMapper noticeMapper;
    private final MessageNoticeMapper messageNoticeMapper;
    private final OperationLogMapper operationLogMapper;

    public Map<String, Object> dashboard() {
        requireAdmin();
        List<VolunteerActivity> activities = volunteerActivityMapper.selectList(new LambdaQueryWrapper<>());
        List<ServiceHoursRecord> confirmedHours = serviceHoursRecordMapper.selectList(new LambdaQueryWrapper<ServiceHoursRecord>()
            .eq(ServiceHoursRecord::getHoursStatus, "CONFIRMED"));
        long signupCount = activitySignupMapper.selectCount(new LambdaQueryWrapper<ActivitySignup>());
        long completedActivityCount = activities.stream().filter(it -> "COMPLETED".equals(it.getActivityStatus())).count();
        BigDecimal totalHours = confirmedHours.stream()
            .map(ServiceHoursRecord::getHoursValue)
            .filter(Objects::nonNull)
            .reduce(BigDecimal.ZERO, BigDecimal::add);

        Map<String, Long> monthCountMap = activities.stream().collect(Collectors.groupingBy(
            activity -> YearMonth.from(activity.getStartTime()).toString(),
            LinkedHashMap::new,
            Collectors.counting()
        ));
        Map<String, Long> categoryCountMap = activities.stream().collect(Collectors.groupingBy(
            VolunteerActivity::getCategoryCode,
            LinkedHashMap::new,
            Collectors.counting()
        ));
        Map<String, BigDecimal> collegeHoursMap = studentMapper.selectList(new LambdaQueryWrapper<Student>())
            .stream()
            .collect(Collectors.groupingBy(
                Student::getCollegeName,
                LinkedHashMap::new,
                Collectors.mapping(
                    student -> student.getTotalServiceHours() == null ? BigDecimal.ZERO : student.getTotalServiceHours(),
                    Collectors.reducing(BigDecimal.ZERO, BigDecimal::add)
                )
            ));

        return Map.of(
            "summary", Map.of(
                "activityCount", activities.size(),
                "signupCount", signupCount,
                "completedActivityCount", completedActivityCount,
                "totalServiceHours", totalHours
            ),
            "activityByMonth", monthCountMap,
            "activityByCategory", categoryCountMap,
            "hoursByCollege", collegeHoursMap
        );
    }

    public List<Student> listStudents() {
        requireAdmin();
        return studentMapper.selectList(new LambdaQueryWrapper<Student>().orderByAsc(Student::getStudentNo));
    }

    @Transactional
    public void saveStudent(Long id, StudentSaveRequest request) {
        requireAdmin();
        Student student = id == null ? new Student() : mustStudent(id);
        boolean creating = student.getId() == null;
        student.setStudentNo(request.studentNo());
        student.setName(request.name());
        student.setGender(request.gender());
        student.setCollegeName(request.collegeName());
        student.setMajorName(request.majorName());
        student.setClassName(request.className());
        student.setPhone(request.phone());
        student.setEmail(request.email());
        student.setAvatarUrl(request.avatarUrl());
        student.setRemark(request.remark());
        student.setStudentStatus("NORMAL");
        if (creating) {
            student.setTotalServiceHours(BigDecimal.ZERO);
            student.setCreatedAt(LocalDateTime.now());
            student.setUpdatedAt(LocalDateTime.now());
            student.setIsDeleted(0);
            studentMapper.insert(student);
            SysUser sysUser = new SysUser();
            sysUser.setUsername(request.studentNo());
            sysUser.setPasswordHash(PasswordUtils.sha256(request.password() == null ? "123456" : request.password()));
            sysUser.setRoleCode("STUDENT");
            sysUser.setRefId(student.getId());
            sysUser.setAccountStatus("ENABLED");
            sysUser.setCreatedAt(LocalDateTime.now());
            sysUser.setUpdatedAt(LocalDateTime.now());
            sysUser.setIsDeleted(0);
            sysUserMapper.insert(sysUser);
        } else {
            student.setUpdatedAt(LocalDateTime.now());
            studentMapper.updateById(student);
        }
        logOperation("STUDENT", creating ? "CREATE" : "UPDATE", student.getId(), "维护学生信息");
    }

    public List<AdminUser> listAdmins() {
        requireAdmin();
        return adminUserMapper.selectList(new LambdaQueryWrapper<AdminUser>().orderByAsc(AdminUser::getAdminNo));
    }

    @Transactional
    public void saveAdmin(Long id, AdminSaveRequest request) {
        requireAdmin();
        AdminUser adminUser = id == null ? new AdminUser() : mustAdmin(id);
        boolean creating = adminUser.getId() == null;
        adminUser.setAdminNo(request.adminNo());
        adminUser.setName(request.name());
        adminUser.setPhone(request.phone());
        adminUser.setEmail(request.email());
        adminUser.setTitleName(request.titleName());
        adminUser.setAdminStatus("NORMAL");
        if (creating) {
            adminUser.setCreatedAt(LocalDateTime.now());
            adminUser.setUpdatedAt(LocalDateTime.now());
            adminUser.setIsDeleted(0);
            adminUserMapper.insert(adminUser);
            SysUser sysUser = new SysUser();
            sysUser.setUsername(request.adminNo());
            sysUser.setPasswordHash(PasswordUtils.sha256(request.password() == null ? "123456" : request.password()));
            sysUser.setRoleCode("ADMIN");
            sysUser.setRefId(adminUser.getId());
            sysUser.setAccountStatus("ENABLED");
            sysUser.setCreatedAt(LocalDateTime.now());
            sysUser.setUpdatedAt(LocalDateTime.now());
            sysUser.setIsDeleted(0);
            sysUserMapper.insert(sysUser);
        } else {
            adminUser.setUpdatedAt(LocalDateTime.now());
            adminUserMapper.updateById(adminUser);
        }
        logOperation("ADMIN", creating ? "CREATE" : "UPDATE", adminUser.getId(), "维护管理员信息");
    }

    public List<VolunteerActivity> listActivities() {
        requireAdmin();
        return volunteerActivityMapper.selectList(new LambdaQueryWrapper<VolunteerActivity>()
            .orderByDesc(VolunteerActivity::getCreatedAt));
    }

    @Transactional
    public void saveActivity(Long id, ActivitySaveRequest request) {
        requireAdmin();
        VolunteerActivity activity = id == null ? new VolunteerActivity() : mustActivity(id);
        if (request.endTime().isBefore(request.startTime()) || request.signupDeadline().isAfter(request.startTime())) {
            throw new BusinessException("活动时间配置不合法");
        }
        boolean creating = activity.getId() == null;
        activity.setTitle(request.title());
        activity.setCategoryCode(request.categoryCode());
        activity.setLocation(request.location());
        activity.setOrganizerName(request.organizerName());
        activity.setDescription(request.description());
        activity.setCoverUrl(request.coverUrl());
        activity.setAttachmentUrl(request.attachmentUrl());
        activity.setRecruitCount(request.recruitCount());
        activity.setSignupDeadline(request.signupDeadline());
        activity.setStartTime(request.startTime());
        activity.setEndTime(request.endTime());
        activity.setServiceHours(request.serviceHours());
        if (creating) {
            activity.setActivityStatus("DRAFT");
            activity.setCreatedAt(LocalDateTime.now());
            activity.setUpdatedAt(LocalDateTime.now());
            activity.setIsDeleted(0);
            volunteerActivityMapper.insert(activity);
        } else {
            activity.setUpdatedAt(LocalDateTime.now());
            volunteerActivityMapper.updateById(activity);
        }
        logOperation("ACTIVITY", creating ? "CREATE" : "UPDATE", activity.getId(), "维护活动信息");
    }

    @Transactional
    public void publishActivity(Long activityId) {
        requireAdmin();
        VolunteerActivity activity = mustActivity(activityId);
        activity.setActivityStatus("PUBLISHED");
        activity.setCheckInCode(randomCode());
        activity.setCheckOutCode(randomCode());
        activity.setPublishedAt(LocalDateTime.now());
        activity.setPublishedBy(SecurityHelper.currentUser().getUserId());
        activity.setUpdatedAt(LocalDateTime.now());
        volunteerActivityMapper.updateById(activity);
        logOperation("ACTIVITY", "PUBLISH", activityId, "发布活动");
    }

    @Transactional
    public void cancelActivity(Long activityId) {
        requireAdmin();
        VolunteerActivity activity = mustActivity(activityId);
        activity.setActivityStatus("CANCELLED");
        activity.setUpdatedAt(LocalDateTime.now());
        volunteerActivityMapper.updateById(activity);

        List<ActivitySignup> signups = activitySignupMapper.selectList(new LambdaQueryWrapper<ActivitySignup>()
            .eq(ActivitySignup::getActivityId, activityId));
        for (ActivitySignup signup : signups) {
            pushMessageForStudent(signup.getStudentId(), "ACTIVITY_CHANGED", "活动取消通知",
                "你报名的活动《" + activity.getTitle() + "》已取消", "ACTIVITY", activityId);
        }
        List<ServiceHoursRecord> hoursRecords = serviceHoursRecordMapper.selectList(new LambdaQueryWrapper<ServiceHoursRecord>()
            .eq(ServiceHoursRecord::getActivityId, activityId)
            .ne(ServiceHoursRecord::getHoursStatus, "REVOKED"));
        for (ServiceHoursRecord record : hoursRecords) {
            record.setHoursStatus("REVOKED");
            record.setRemark("活动取消自动撤销");
            record.setUpdatedAt(LocalDateTime.now());
            serviceHoursRecordMapper.updateById(record);
            refreshStudentTotalHours(record.getStudentId());
        }
        logOperation("ACTIVITY", "CANCEL", activityId, "取消活动");
    }

    public List<Map<String, Object>> listSignups() {
        requireAdmin();
        List<ActivitySignup> signups = activitySignupMapper.selectList(new LambdaQueryWrapper<ActivitySignup>()
            .orderByDesc(ActivitySignup::getSignupTime));
        return signups.stream().map(signup -> {
            Student student = studentMapper.selectById(signup.getStudentId());
            VolunteerActivity activity = volunteerActivityMapper.selectById(signup.getActivityId());
            return Map.of("signup", signup, "student", student, "activity", activity);
        }).collect(Collectors.toList());
    }

    @Transactional
    public void approveSignup(Long signupId, ReviewRequest request) {
        requireAdmin();
        ActivitySignup signup = mustSignup(signupId);
        VolunteerActivity activity = mustActivity(signup.getActivityId());
        long approvedCount = activitySignupMapper.selectCount(new LambdaQueryWrapper<ActivitySignup>()
            .eq(ActivitySignup::getActivityId, activity.getId())
            .eq(ActivitySignup::getSignupStatus, "APPROVED"));
        if (approvedCount >= activity.getRecruitCount()) {
            throw new BusinessException("活动名额已满");
        }
        signup.setSignupStatus("APPROVED");
        signup.setReviewComment(request.reviewComment());
        signup.setReviewedBy(SecurityHelper.currentUser().getUserId());
        signup.setReviewedAt(LocalDateTime.now());
        signup.setUpdatedAt(LocalDateTime.now());
        activitySignupMapper.updateById(signup);

        ActivitySign sign = new ActivitySign();
        sign.setActivityId(signup.getActivityId());
        sign.setStudentId(signup.getStudentId());
        sign.setSignStatus("UNSIGNED");
        sign.setCreatedAt(LocalDateTime.now());
        sign.setUpdatedAt(LocalDateTime.now());
        activitySignMapper.insert(sign);
        pushMessageForStudent(signup.getStudentId(), "SIGNUP_APPROVED", "报名审核通过",
            "你报名的活动《" + activity.getTitle() + "》已审核通过", "SIGNUP", signupId);
        logOperation("SIGNUP", "APPROVE", signupId, "审核通过报名");
    }

    @Transactional
    public void rejectSignup(Long signupId, ReviewRequest request) {
        requireAdmin();
        ActivitySignup signup = mustSignup(signupId);
        signup.setSignupStatus("REJECTED");
        signup.setReviewComment(request.reviewComment());
        signup.setReviewedBy(SecurityHelper.currentUser().getUserId());
        signup.setReviewedAt(LocalDateTime.now());
        signup.setUpdatedAt(LocalDateTime.now());
        activitySignupMapper.updateById(signup);
        pushMessageForStudent(signup.getStudentId(), "SIGNUP_REJECTED", "报名审核驳回",
            "你报名的活动审核未通过", "SIGNUP", signupId);
        logOperation("SIGNUP", "REJECT", signupId, "驳回报名");
    }

    public List<Map<String, Object>> listSigns() {
        requireAdmin();
        List<ActivitySign> signs = activitySignMapper.selectList(new LambdaQueryWrapper<ActivitySign>()
            .orderByDesc(ActivitySign::getCreatedAt));
        return signs.stream().map(sign -> Map.of(
            "sign", sign,
            "student", studentMapper.selectById(sign.getStudentId()),
            "activity", volunteerActivityMapper.selectById(sign.getActivityId())
        )).collect(Collectors.toList());
    }

    @Transactional
    public void fixSign(Long signId, FixSignRequest request) {
        requireAdmin();
        ActivitySign sign = activitySignMapper.selectById(signId);
        if (sign == null) {
            throw new BusinessException("签到记录不存在");
        }
        sign.setSignStatus("ADMIN_FIXED");
        sign.setSignInTime(request.signInTime());
        sign.setSignOutTime(request.signOutTime());
        sign.setSignInMode("ADMIN");
        sign.setSignOutMode("ADMIN");
        sign.setSignInOperatorId(SecurityHelper.currentUser().getUserId());
        sign.setSignOutOperatorId(SecurityHelper.currentUser().getUserId());
        sign.setExceptionRemark(request.exceptionRemark());
        sign.setUpdatedAt(LocalDateTime.now());
        activitySignMapper.updateById(sign);

        VolunteerActivity activity = mustActivity(sign.getActivityId());
        ServiceHoursRecord record = serviceHoursRecordMapper.selectOne(new LambdaQueryWrapper<ServiceHoursRecord>()
            .eq(ServiceHoursRecord::getActivityId, sign.getActivityId())
            .eq(ServiceHoursRecord::getStudentId, sign.getStudentId()));
        if (record == null) {
            record = new ServiceHoursRecord();
            record.setActivityId(sign.getActivityId());
            record.setStudentId(sign.getStudentId());
            record.setSignId(sign.getId());
            record.setHoursValue(activity.getServiceHours());
            record.setHoursStatus("PENDING_CONFIRM");
            record.setGeneratedAt(LocalDateTime.now());
            record.setCreatedAt(LocalDateTime.now());
            record.setUpdatedAt(LocalDateTime.now());
            ActivitySignup signup = activitySignupMapper.selectOne(new LambdaQueryWrapper<ActivitySignup>()
                .eq(ActivitySignup::getActivityId, sign.getActivityId())
                .eq(ActivitySignup::getStudentId, sign.getStudentId()));
            if (signup != null) {
                record.setSignupId(signup.getId());
            }
            serviceHoursRecordMapper.insert(record);
        }
        logOperation("SIGN", "FIX", signId, "管理员补录签到");
    }

    public List<Map<String, Object>> listHours() {
        requireAdmin();
        return serviceHoursRecordMapper.selectList(new LambdaQueryWrapper<ServiceHoursRecord>()
                .orderByDesc(ServiceHoursRecord::getGeneratedAt))
            .stream()
            .map(record -> Map.of(
                "record", record,
                "student", studentMapper.selectById(record.getStudentId()),
                "activity", volunteerActivityMapper.selectById(record.getActivityId())
            ))
            .collect(Collectors.toList());
    }

    @Transactional
    public void confirmHours(Long recordId, HoursUpdateRequest request) {
        requireAdmin();
        ServiceHoursRecord record = serviceHoursRecordMapper.selectById(recordId);
        if (record == null) {
            throw new BusinessException("时长记录不存在");
        }
        record.setHoursStatus("CONFIRMED");
        if (request.hoursValue() != null) {
            record.setHoursValue(request.hoursValue());
        }
        record.setRemark(request.remark());
        record.setConfirmedBy(SecurityHelper.currentUser().getUserId());
        record.setConfirmedAt(LocalDateTime.now());
        record.setUpdatedAt(LocalDateTime.now());
        serviceHoursRecordMapper.updateById(record);
        refreshStudentTotalHours(record.getStudentId());
        pushMessageForStudent(record.getStudentId(), "HOURS_CONFIRMED", "时长确认通知", "你的服务时长已确认", "HOURS", recordId);
        logOperation("HOURS", "CONFIRM", recordId, "确认服务时长");
    }

    @Transactional
    public void revokeHours(Long recordId, HoursUpdateRequest request) {
        requireAdmin();
        ServiceHoursRecord record = serviceHoursRecordMapper.selectById(recordId);
        if (record == null) {
            throw new BusinessException("时长记录不存在");
        }
        record.setHoursStatus("REVOKED");
        record.setRemark(request.remark());
        record.setConfirmedBy(SecurityHelper.currentUser().getUserId());
        record.setConfirmedAt(LocalDateTime.now());
        record.setUpdatedAt(LocalDateTime.now());
        serviceHoursRecordMapper.updateById(record);
        refreshStudentTotalHours(record.getStudentId());
        logOperation("HOURS", "REVOKE", recordId, "撤销服务时长");
    }

    public List<Notice> listNotices() {
        requireAdmin();
        return noticeMapper.selectList(new LambdaQueryWrapper<Notice>().orderByDesc(Notice::getCreatedAt));
    }

    @Transactional
    public void saveNotice(Long id, NoticeSaveRequest request) {
        requireAdmin();
        Notice notice = id == null ? new Notice() : noticeMapper.selectById(id);
        boolean creating = notice == null || notice.getId() == null;
        if (notice == null) {
            notice = new Notice();
        }
        notice.setTitle(request.title());
        notice.setContent(request.content());
        notice.setAttachmentUrl(request.attachmentUrl());
        notice.setTargetScope("ALL_STUDENTS");
        notice.setPublishStatus("PUBLISHED");
        notice.setPublishedBy(SecurityHelper.currentUser().getUserId());
        notice.setPublishedAt(LocalDateTime.now());
        if (creating) {
            notice.setCreatedAt(LocalDateTime.now());
            notice.setUpdatedAt(LocalDateTime.now());
            notice.setIsDeleted(0);
            noticeMapper.insert(notice);
        } else {
            notice.setUpdatedAt(LocalDateTime.now());
            noticeMapper.updateById(notice);
        }
        List<SysUser> students = sysUserMapper.selectList(new LambdaQueryWrapper<SysUser>()
            .eq(SysUser::getRoleCode, "STUDENT")
            .eq(SysUser::getAccountStatus, "ENABLED"));
        for (SysUser sysUser : students) {
            MessageNotice messageNotice = new MessageNotice();
            messageNotice.setUserId(sysUser.getId());
            messageNotice.setMessageType("NOTICE_PUBLISHED");
            messageNotice.setTitle("新公告通知");
            messageNotice.setContent(request.title());
            messageNotice.setBizType("NOTICE");
            messageNotice.setBizId(notice.getId());
            messageNotice.setIsRead(0);
            messageNotice.setCreatedAt(LocalDateTime.now());
            messageNoticeMapper.insert(messageNotice);
        }
        logOperation("NOTICE", creating ? "CREATE" : "UPDATE", notice.getId(), "发布公告");
    }

    public Map<String, Object> activityReport() {
        requireAdmin();
        List<VolunteerActivity> activities = listActivities();
        List<Map<String, Object>> rows = new ArrayList<>();
        for (VolunteerActivity activity : activities) {
            long signupCount = activitySignupMapper.selectCount(new LambdaQueryWrapper<ActivitySignup>()
                .eq(ActivitySignup::getActivityId, activity.getId()));
            long approvedCount = activitySignupMapper.selectCount(new LambdaQueryWrapper<ActivitySignup>()
                .eq(ActivitySignup::getActivityId, activity.getId())
                .eq(ActivitySignup::getSignupStatus, "APPROVED"));
            long signCount = activitySignMapper.selectCount(new LambdaQueryWrapper<ActivitySign>()
                .eq(ActivitySign::getActivityId, activity.getId())
                .in(ActivitySign::getSignStatus, List.of("SIGNED_IN", "SIGNED_OUT", "ADMIN_FIXED")));
            long completedCount = activitySignMapper.selectCount(new LambdaQueryWrapper<ActivitySign>()
                .eq(ActivitySign::getActivityId, activity.getId())
                .in(ActivitySign::getSignStatus, List.of("SIGNED_OUT", "ADMIN_FIXED")));
            BigDecimal totalHours = serviceHoursRecordMapper.selectList(new LambdaQueryWrapper<ServiceHoursRecord>()
                    .eq(ServiceHoursRecord::getActivityId, activity.getId())
                    .eq(ServiceHoursRecord::getHoursStatus, "CONFIRMED"))
                .stream()
                .map(ServiceHoursRecord::getHoursValue)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
            rows.add(Map.of(
                "activity", activity,
                "signupCount", signupCount,
                "approvedCount", approvedCount,
                "signCount", signCount,
                "completedCount", completedCount,
                "totalHours", totalHours
            ));
        }
        return Map.of("records", rows);
    }

    public Map<String, Object> studentHoursReport() {
        requireAdmin();
        List<Map<String, Object>> rows = studentMapper.selectList(new LambdaQueryWrapper<Student>()
                .orderByDesc(Student::getTotalServiceHours))
            .stream()
            .map(student -> Map.of(
                "student", student,
                "confirmedCount", serviceHoursRecordMapper.selectCount(new LambdaQueryWrapper<ServiceHoursRecord>()
                    .eq(ServiceHoursRecord::getStudentId, student.getId())
                    .eq(ServiceHoursRecord::getHoursStatus, "CONFIRMED"))
            ))
            .collect(Collectors.toList());
        return Map.of("records", rows);
    }

    public Map<String, Object> monthlyReport() {
        requireAdmin();
        Map<String, Long> activityCount = volunteerActivityMapper.selectList(new LambdaQueryWrapper<VolunteerActivity>())
            .stream()
            .filter(activity -> !"CANCELLED".equals(activity.getActivityStatus()))
            .collect(Collectors.groupingBy(activity -> YearMonth.from(activity.getStartTime()).toString(), Collectors.counting()));
        Map<String, BigDecimal> totalHours = serviceHoursRecordMapper.selectList(new LambdaQueryWrapper<ServiceHoursRecord>()
                .eq(ServiceHoursRecord::getHoursStatus, "CONFIRMED"))
            .stream()
            .collect(Collectors.groupingBy(
                record -> YearMonth.from(record.getGeneratedAt()).toString(),
                Collectors.mapping(ServiceHoursRecord::getHoursValue, Collectors.reducing(BigDecimal.ZERO, BigDecimal::add))
            ));
        return Map.of("activityCount", activityCount, "totalHours", totalHours);
    }

    public String exportActivityCsv() {
        requireAdmin();
        StringBuilder sb = new StringBuilder("活动名称,类别,地点,报名人数,签到人数,完成人数,累计时长\n");
        List<Map<String, Object>> records = (List<Map<String, Object>>) activityReport().get("records");
        for (Map<String, Object> row : records) {
            VolunteerActivity activity = (VolunteerActivity) row.get("activity");
            sb.append(activity.getTitle()).append(',')
                .append(activity.getCategoryCode()).append(',')
                .append(activity.getLocation()).append(',')
                .append(row.get("signupCount")).append(',')
                .append(row.get("signCount")).append(',')
                .append(row.get("completedCount")).append(',')
                .append(row.get("totalHours")).append('\n');
        }
        return sb.toString();
    }

    public String exportStudentHoursCsv() {
        requireAdmin();
        StringBuilder sb = new StringBuilder("学号,姓名,学院,专业,班级,累计时长,已完成活动数\n");
        List<Map<String, Object>> records = (List<Map<String, Object>>) studentHoursReport().get("records");
        for (Map<String, Object> row : records) {
            Student student = (Student) row.get("student");
            sb.append(student.getStudentNo()).append(',')
                .append(student.getName()).append(',')
                .append(student.getCollegeName()).append(',')
                .append(student.getMajorName()).append(',')
                .append(student.getClassName()).append(',')
                .append(student.getTotalServiceHours()).append(',')
                .append(row.get("confirmedCount")).append('\n');
        }
        return sb.toString();
    }

    private void requireAdmin() {
        SecurityHelper.requireAdmin();
    }

    private Student mustStudent(Long id) {
        Student student = studentMapper.selectById(id);
        if (student == null) {
            throw new BusinessException("学生不存在");
        }
        return student;
    }

    private AdminUser mustAdmin(Long id) {
        AdminUser adminUser = adminUserMapper.selectById(id);
        if (adminUser == null) {
            throw new BusinessException("管理员不存在");
        }
        return adminUser;
    }

    private VolunteerActivity mustActivity(Long id) {
        VolunteerActivity activity = volunteerActivityMapper.selectById(id);
        if (activity == null) {
            throw new BusinessException("活动不存在");
        }
        return activity;
    }

    private ActivitySignup mustSignup(Long id) {
        ActivitySignup signup = activitySignupMapper.selectById(id);
        if (signup == null) {
            throw new BusinessException("报名记录不存在");
        }
        return signup;
    }

    private void refreshStudentTotalHours(Long studentId) {
        Student student = studentMapper.selectById(studentId);
        if (student == null) {
            return;
        }
        BigDecimal total = serviceHoursRecordMapper.selectList(new LambdaQueryWrapper<ServiceHoursRecord>()
                .eq(ServiceHoursRecord::getStudentId, studentId)
                .eq(ServiceHoursRecord::getHoursStatus, "CONFIRMED"))
            .stream()
            .map(ServiceHoursRecord::getHoursValue)
            .filter(Objects::nonNull)
            .reduce(BigDecimal.ZERO, BigDecimal::add);
        student.setTotalServiceHours(total);
        student.setUpdatedAt(LocalDateTime.now());
        studentMapper.updateById(student);
    }

    private void pushMessageForStudent(Long studentId, String type, String title, String content, String bizType, Long bizId) {
        SysUser studentUser = sysUserMapper.selectOne(new LambdaQueryWrapper<SysUser>()
            .eq(SysUser::getRoleCode, "STUDENT")
            .eq(SysUser::getRefId, studentId));
        if (studentUser == null) {
            return;
        }
        MessageNotice messageNotice = new MessageNotice();
        messageNotice.setUserId(studentUser.getId());
        messageNotice.setMessageType(type);
        messageNotice.setTitle(title);
        messageNotice.setContent(content);
        messageNotice.setBizType(bizType);
        messageNotice.setBizId(bizId);
        messageNotice.setIsRead(0);
        messageNotice.setCreatedAt(LocalDateTime.now());
        messageNoticeMapper.insert(messageNotice);
    }

    private void logOperation(String module, String operationType, Long bizId, String description) {
        OperationLog log = new OperationLog();
        log.setOperatorUserId(SecurityHelper.currentUser().getUserId());
        log.setOperatorRoleCode(SecurityHelper.currentUser().getRoleCode());
        log.setModuleName(module);
        log.setOperationType(operationType);
        log.setBizId(bizId);
        log.setRequestPath("/api/admin");
        log.setOperationDesc(description);
        log.setOperationTime(LocalDateTime.now());
        operationLogMapper.insert(log);
    }

    private String randomCode() {
        return UUID.randomUUID().toString().replace("-", "").substring(0, 6).toUpperCase();
    }
}
