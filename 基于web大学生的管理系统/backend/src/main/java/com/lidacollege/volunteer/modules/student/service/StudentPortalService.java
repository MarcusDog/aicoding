package com.lidacollege.volunteer.modules.student.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.LambdaUpdateWrapper;
import com.lidacollege.volunteer.common.exception.BusinessException;
import com.lidacollege.volunteer.common.security.SecurityHelper;
import com.lidacollege.volunteer.modules.activity.entity.VolunteerActivity;
import com.lidacollege.volunteer.modules.activity.mapper.VolunteerActivityMapper;
import com.lidacollege.volunteer.modules.hours.entity.ServiceHoursRecord;
import com.lidacollege.volunteer.modules.hours.mapper.ServiceHoursRecordMapper;
import com.lidacollege.volunteer.modules.sign.entity.ActivitySign;
import com.lidacollege.volunteer.modules.sign.mapper.ActivitySignMapper;
import com.lidacollege.volunteer.modules.signup.entity.ActivitySignup;
import com.lidacollege.volunteer.modules.signup.mapper.ActivitySignupMapper;
import com.lidacollege.volunteer.modules.student.dto.CancelSignupRequest;
import com.lidacollege.volunteer.modules.student.dto.SignCodeRequest;
import com.lidacollege.volunteer.modules.student.dto.StudentProfileUpdateRequest;
import com.lidacollege.volunteer.modules.system.entity.MessageNotice;
import com.lidacollege.volunteer.modules.system.entity.Notice;
import com.lidacollege.volunteer.modules.system.entity.Student;
import com.lidacollege.volunteer.modules.system.entity.SysUser;
import com.lidacollege.volunteer.modules.system.mapper.MessageNoticeMapper;
import com.lidacollege.volunteer.modules.system.mapper.NoticeMapper;
import com.lidacollege.volunteer.modules.system.mapper.StudentMapper;
import com.lidacollege.volunteer.modules.system.mapper.SysUserMapper;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.stream.Collectors;
import lombok.RequiredArgsConstructor;
import org.apache.commons.lang3.StringUtils;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class StudentPortalService {

    private final StudentMapper studentMapper;
    private final SysUserMapper sysUserMapper;
    private final VolunteerActivityMapper volunteerActivityMapper;
    private final ActivitySignupMapper activitySignupMapper;
    private final ActivitySignMapper activitySignMapper;
    private final ServiceHoursRecordMapper serviceHoursRecordMapper;
    private final NoticeMapper noticeMapper;
    private final MessageNoticeMapper messageNoticeMapper;

    public Map<String, Object> homeData() {
        Student student = currentStudent();
        SysUser sysUser = currentSysUser();
        List<VolunteerActivity> recentActivities = volunteerActivityMapper.selectList(new LambdaQueryWrapper<VolunteerActivity>()
            .in(VolunteerActivity::getActivityStatus, List.of("PUBLISHED", "SIGNUP_CLOSED", "IN_PROGRESS"))
            .orderByDesc(VolunteerActivity::getCreatedAt)
            .last("limit 5"));
        List<Notice> notices = noticeMapper.selectList(new LambdaQueryWrapper<Notice>()
            .eq(Notice::getPublishStatus, "PUBLISHED")
            .orderByDesc(Notice::getPublishedAt)
            .last("limit 5"));
        long signupCount = activitySignupMapper.selectCount(new LambdaQueryWrapper<ActivitySignup>()
            .eq(ActivitySignup::getStudentId, student.getId()));
        long unreadCount = messageNoticeMapper.selectCount(new LambdaQueryWrapper<MessageNotice>()
            .eq(MessageNotice::getUserId, sysUser.getId())
            .eq(MessageNotice::getIsRead, 0));

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("student", student);
        result.put("summary", Map.of(
            "totalServiceHours", student.getTotalServiceHours(),
            "signupCount", signupCount,
            "unreadCount", unreadCount
        ));
        result.put("recentActivities", recentActivities);
        result.put("notices", notices);
        return result;
    }

    public List<VolunteerActivity> listActivities(String keyword, String status) {
        LambdaQueryWrapper<VolunteerActivity> wrapper = new LambdaQueryWrapper<VolunteerActivity>()
            .notIn(VolunteerActivity::getActivityStatus, List.of("DRAFT"))
            .orderByDesc(VolunteerActivity::getStartTime);
        if (StringUtils.isNotBlank(keyword)) {
            wrapper.like(VolunteerActivity::getTitle, keyword);
        }
        if (StringUtils.isNotBlank(status)) {
            wrapper.eq(VolunteerActivity::getActivityStatus, status);
        }
        return volunteerActivityMapper.selectList(wrapper);
    }

    public Map<String, Object> activityDetail(Long activityId) {
        Student student = currentStudent();
        VolunteerActivity activity = getActivity(activityId);
        ActivitySignup signup = activitySignupMapper.selectOne(new LambdaQueryWrapper<ActivitySignup>()
            .eq(ActivitySignup::getActivityId, activityId)
            .eq(ActivitySignup::getStudentId, student.getId()));
        long approvedCount = activitySignupMapper.selectCount(new LambdaQueryWrapper<ActivitySignup>()
            .eq(ActivitySignup::getActivityId, activityId)
            .eq(ActivitySignup::getSignupStatus, "APPROVED"));
        return Map.of(
            "activity", activity,
            "signup", signup,
            "approvedCount", approvedCount,
            "remainingCount", Math.max(activity.getRecruitCount() - (int) approvedCount, 0)
        );
    }

    @Transactional
    public void applyActivity(Long activityId) {
        Student student = currentStudent();
        VolunteerActivity activity = getActivity(activityId);
        validateActivityCanSignup(activity);
        ActivitySignup existing = activitySignupMapper.selectOne(new LambdaQueryWrapper<ActivitySignup>()
            .eq(ActivitySignup::getActivityId, activityId)
            .eq(ActivitySignup::getStudentId, student.getId()));
        if (existing != null) {
            throw new BusinessException("你已经报名过该活动");
        }

        ActivitySignup signup = new ActivitySignup();
        signup.setActivityId(activityId);
        signup.setStudentId(student.getId());
        signup.setSignupStatus("PENDING");
        signup.setSignupTime(LocalDateTime.now());
        signup.setCreatedAt(LocalDateTime.now());
        signup.setUpdatedAt(LocalDateTime.now());
        signup.setIsDeleted(0);
        activitySignupMapper.insert(signup);
    }

    @Transactional
    public void cancelSignup(Long signupId, CancelSignupRequest request) {
        Student student = currentStudent();
        ActivitySignup signup = activitySignupMapper.selectById(signupId);
        if (signup == null || !Objects.equals(signup.getStudentId(), student.getId())) {
            throw new BusinessException("报名记录不存在");
        }
        VolunteerActivity activity = getActivity(signup.getActivityId());
        if (activity.getStartTime().isBefore(LocalDateTime.now())) {
            throw new BusinessException("活动开始后不能取消报名");
        }
        ActivitySign sign = activitySignMapper.selectOne(new LambdaQueryWrapper<ActivitySign>()
            .eq(ActivitySign::getActivityId, signup.getActivityId())
            .eq(ActivitySign::getStudentId, student.getId()));
        if (sign != null && !"UNSIGNED".equals(sign.getSignStatus()) && !"ABSENT".equals(sign.getSignStatus())) {
            throw new BusinessException("已产生签到记录，不能取消报名");
        }
        signup.setSignupStatus("CANCELLED");
        signup.setCancelReason(request.cancelReason());
        signup.setUpdatedAt(LocalDateTime.now());
        activitySignupMapper.updateById(signup);
    }

    public List<Map<String, Object>> mySignups() {
        Student student = currentStudent();
        List<ActivitySignup> signups = activitySignupMapper.selectList(new LambdaQueryWrapper<ActivitySignup>()
            .eq(ActivitySignup::getStudentId, student.getId())
            .orderByDesc(ActivitySignup::getSignupTime));
        return signups.stream().map(signup -> {
            VolunteerActivity activity = volunteerActivityMapper.selectById(signup.getActivityId());
            ActivitySign sign = activitySignMapper.selectOne(new LambdaQueryWrapper<ActivitySign>()
                .eq(ActivitySign::getActivityId, signup.getActivityId())
                .eq(ActivitySign::getStudentId, student.getId()));
            Map<String, Object> row = new LinkedHashMap<>();
            row.put("signup", signup);
            row.put("activity", activity);
            row.put("sign", sign);
            return row;
        }).collect(Collectors.toList());
    }

    @Transactional
    public void signIn(SignCodeRequest request) {
        Student student = currentStudent();
        VolunteerActivity activity = getActivity(request.activityId());
        ActivitySignup signup = getApprovedSignup(student.getId(), request.activityId());
        ActivitySign sign = getSignRecord(student.getId(), request.activityId());
        LocalDateTime now = LocalDateTime.now();
        if (now.isBefore(activity.getStartTime().minusMinutes(30)) || now.isAfter(activity.getStartTime().plusMinutes(30))) {
            throw new BusinessException("当前不在签到时间范围内");
        }
        if (!Objects.equals(activity.getCheckInCode(), request.code())) {
            throw new BusinessException("签到码错误");
        }
        if (!"UNSIGNED".equals(sign.getSignStatus())) {
            throw new BusinessException("你已完成签到，不能重复签到");
        }
        sign.setSignStatus("SIGNED_IN");
        sign.setSignInTime(now);
        sign.setSignInMode("CODE");
        sign.setUpdatedAt(now);
        activitySignMapper.updateById(sign);
    }

    @Transactional
    public void signOut(SignCodeRequest request) {
        Student student = currentStudent();
        VolunteerActivity activity = getActivity(request.activityId());
        getApprovedSignup(student.getId(), request.activityId());
        ActivitySign sign = getSignRecord(student.getId(), request.activityId());
        LocalDateTime now = LocalDateTime.now();
        if (now.isBefore(activity.getEndTime().minusMinutes(30)) || now.isAfter(activity.getEndTime().plusMinutes(120))) {
            throw new BusinessException("当前不在签退时间范围内");
        }
        if (!Objects.equals(activity.getCheckOutCode(), request.code())) {
            throw new BusinessException("签退码错误");
        }
        if (!"SIGNED_IN".equals(sign.getSignStatus())) {
            throw new BusinessException("当前状态不能签退");
        }
        sign.setSignStatus("SIGNED_OUT");
        sign.setSignOutTime(now);
        sign.setSignOutMode("CODE");
        sign.setUpdatedAt(now);
        activitySignMapper.updateById(sign);
        generateHoursRecord(student.getId(), activity, sign);
    }

    public List<ServiceHoursRecord> myHours() {
        Student student = currentStudent();
        return serviceHoursRecordMapper.selectList(new LambdaQueryWrapper<ServiceHoursRecord>()
            .eq(ServiceHoursRecord::getStudentId, student.getId())
            .orderByDesc(ServiceHoursRecord::getGeneratedAt));
    }

    public List<MessageNotice> myMessages() {
        SysUser sysUser = currentSysUser();
        return messageNoticeMapper.selectList(new LambdaQueryWrapper<MessageNotice>()
            .eq(MessageNotice::getUserId, sysUser.getId())
            .orderByDesc(MessageNotice::getCreatedAt));
    }

    public Student myProfile() {
        return currentStudent();
    }

    @Transactional
    public void updateProfile(StudentProfileUpdateRequest request) {
        Student student = currentStudent();
        student.setPhone(request.phone());
        student.setEmail(request.email());
        student.setAvatarUrl(request.avatarUrl());
        student.setRemark(request.remark());
        student.setUpdatedAt(LocalDateTime.now());
        studentMapper.updateById(student);
    }

    private SysUser currentSysUser() {
        SysUser sysUser = sysUserMapper.selectById(SecurityHelper.currentUser().getUserId());
        if (sysUser == null) {
            throw new BusinessException("用户不存在");
        }
        return sysUser;
    }

    private Student currentStudent() {
        SecurityHelper.requireStudent();
        Student student = studentMapper.selectById(SecurityHelper.currentUser().getRefId());
        if (student == null) {
            throw new BusinessException("学生信息不存在");
        }
        return student;
    }

    private VolunteerActivity getActivity(Long activityId) {
        VolunteerActivity activity = volunteerActivityMapper.selectById(activityId);
        if (activity == null) {
            throw new BusinessException("活动不存在");
        }
        return activity;
    }

    private ActivitySignup getApprovedSignup(Long studentId, Long activityId) {
        ActivitySignup signup = activitySignupMapper.selectOne(new LambdaQueryWrapper<ActivitySignup>()
            .eq(ActivitySignup::getActivityId, activityId)
            .eq(ActivitySignup::getStudentId, studentId)
            .eq(ActivitySignup::getSignupStatus, "APPROVED"));
        if (signup == null) {
            throw new BusinessException("当前活动报名未审核通过");
        }
        return signup;
    }

    private ActivitySign getSignRecord(Long studentId, Long activityId) {
        ActivitySign sign = activitySignMapper.selectOne(new LambdaQueryWrapper<ActivitySign>()
            .eq(ActivitySign::getActivityId, activityId)
            .eq(ActivitySign::getStudentId, studentId));
        if (sign == null) {
            throw new BusinessException("签到记录不存在");
        }
        return sign;
    }

    private void validateActivityCanSignup(VolunteerActivity activity) {
        if (List.of("CANCELLED", "COMPLETED", "IN_PROGRESS").contains(activity.getActivityStatus())) {
            throw new BusinessException("当前活动不能报名");
        }
        if (activity.getSignupDeadline().isBefore(LocalDateTime.now())) {
            throw new BusinessException("活动报名已截止");
        }
        long approvedCount = activitySignupMapper.selectCount(new LambdaQueryWrapper<ActivitySignup>()
            .eq(ActivitySignup::getActivityId, activity.getId())
            .eq(ActivitySignup::getSignupStatus, "APPROVED"));
        if (approvedCount >= activity.getRecruitCount()) {
            throw new BusinessException("活动名额已满");
        }
    }

    private void generateHoursRecord(Long studentId, VolunteerActivity activity, ActivitySign sign) {
        ServiceHoursRecord existing = serviceHoursRecordMapper.selectOne(new LambdaQueryWrapper<ServiceHoursRecord>()
            .eq(ServiceHoursRecord::getActivityId, activity.getId())
            .eq(ServiceHoursRecord::getStudentId, studentId));
        if (existing != null) {
            return;
        }
        ActivitySignup signup = activitySignupMapper.selectOne(new LambdaQueryWrapper<ActivitySignup>()
            .eq(ActivitySignup::getActivityId, activity.getId())
            .eq(ActivitySignup::getStudentId, studentId));
        ServiceHoursRecord record = new ServiceHoursRecord();
        record.setActivityId(activity.getId());
        record.setStudentId(studentId);
        record.setSignupId(signup == null ? null : signup.getId());
        record.setSignId(sign.getId());
        record.setHoursValue(activity.getServiceHours());
        record.setHoursStatus("PENDING_CONFIRM");
        record.setGeneratedAt(LocalDateTime.now());
        record.setCreatedAt(LocalDateTime.now());
        record.setUpdatedAt(LocalDateTime.now());
        serviceHoursRecordMapper.insert(record);
    }
}
